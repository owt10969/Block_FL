# federated_learning/client.py

from .centralized import load_data, load_model, train, test
from collections import OrderedDict
import flwr as fl
import torch
import rsa
import json

###############################################################################
# 1. 設定裝置 (GPU 或 CPU)
###############################################################################
DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

###############################################################################
# 2. 生成 RSA 公私鑰 (public_key, private_key)
###############################################################################
public_key, private_key = rsa.newkeys(512)

###############################################################################
# 3. 輔助函式：載入/設定 PyTorch 模型參數
###############################################################################
def set_parameters(model, parameters):
    state_dict_keys = list(model.state_dict().keys())
    if len(parameters) != len(state_dict_keys):
        raise ValueError(
            f"Mismatch between model parameters "
            f"({len(state_dict_keys)}) and received parameters ({len(parameters)})"
        )
    # 將每個權重轉成 tensor, 並移動到 DEVICE (cuda / cpu)
    state_dict = OrderedDict({
        key: torch.tensor(param).to(DEVICE) for key, param in zip(state_dict_keys, parameters)
    })
    model.load_state_dict(state_dict, strict=True)

def get_parameters(model):
    """
    將 PyTorch 模型的 state_dict 轉成 List[np.ndarray] 結構,
    以便回傳給 Flower 伺服器。
    """
    return [val.cpu().numpy() for _, val in model.state_dict().items()]

###############################################################################
# 4. 載入本地模型與資料
###############################################################################
net = load_model()
trainloader, testloader = load_data()

###############################################################################
# 5. 定義 Flower 客戶端類別
###############################################################################
class FlowerClient(fl.client.NumPyClient):
    def get_parameters(self, config):
        """
        在初始階段呼叫, 回傳本地模型參數 (list of np.ndarray).
        """
        parameters = get_parameters(net)
        print("Client sending parameters to server:")
        for name, param in zip(net.state_dict().keys(), parameters):
            print(f"{name}: {param.shape}")
        return parameters
    
    def fit(self, parameters, config):
        """
        - 1. 接收伺服器下發的全局參數並載入
        - 2. 進行一次本地訓練
        - 3. 序列化更新後參數 + 簽名
        - 4. 透過 metrics 回傳給伺服器
        """
        # 1. 將全局參數載入到本地模型
        set_parameters(net, parameters)
        net.to(DEVICE)

        # 2. 執行本地訓練 (epochs=1)
        train(net, trainloader, epochs=1)

        # 3. 取出更新後的參數, 序列化 => JSON, 然後用私鑰簽名
        updated_parameters = get_parameters(net)
        param_json = json.dumps([arr.tolist() for arr in updated_parameters])
        signature = rsa.sign(param_json.encode('utf-8'), private_key, 'SHA-256')

        # 4. 將簽名與序列化後參數傳給伺服器 (儲存在 metrics)
        metrics = {
            "param_json": param_json,       # 模型參數的 JSON
            "signature": signature.hex(),   # 簽名 (hex)
            #"client_public_key": public_key.save_pkcs1().decode("utf-8")
        }

        # 回傳 (更新後參數, 資料集大小, metrics)
        return updated_parameters, len(trainloader.dataset), metrics

    def evaluate(self, parameters, config):
        """
        進行本地評估/測試, 回傳 loss, num_examples, 以及自訂測試指標
        """
        set_parameters(net, parameters)
        loss, accuracy = test(net, testloader)
        print(f"[Client] Evaluate => loss: {loss:.4f}, accuracy: {accuracy:.2%}")
        return float(loss), len(testloader.dataset), {"accuracy": accuracy}

###############################################################################
# 6. 啟動 Flower 客戶端 (連線到伺服器)
###############################################################################
def main():
    fl.client.start_numpy_client(
        server_address="127.0.0.1:8080",
        client=FlowerClient(),
    )

if __name__ == '__main__':
    main()
