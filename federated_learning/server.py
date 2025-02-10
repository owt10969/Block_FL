# federated_learning/server.py

import flwr as fl
from flwr.common import parameters_to_ndarrays
import json
import rsa  # 用於簽名驗證

from blockchain.blockchain import BlockChain

def weighted_average(metrics):
    """ 用於 evaluate_metrics_aggregation_fn, 聚合客戶端測試指標 """
    accuracies = [num_examples * m["accuracy"] for num_examples, m in metrics]
    examples = [num_examples for num_examples, _ in metrics]
    return {"accuracy": sum(accuracies) / sum(examples)}

def fit_metrics_aggregation_fn(metrics):
    """
    用於 fit_metrics_aggregation_fn, 聚合客戶端訓練指標
    metrics 形如: [(num_examples, {"loss":..., "accuracy":...}), ...]
    """
    total_loss = 0.0
    total_acc = 0.0
    total_samples = 0
    for (num_examples, m) in metrics:
        if "loss" in m:
            total_loss += m["loss"] * num_examples
        if "accuracy" in m:
            total_acc += m["accuracy"] * num_examples
        total_samples += num_examples

    if total_samples == 0:
        return {"loss": 0.0, "accuracy": 0.0}

    return {
        "loss": total_loss / total_samples,
        "accuracy": total_acc / total_samples,
    }

class BlockchainFedAvg(fl.server.strategy.FedAvg):
    def __init__(self, blockchain: BlockChain, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.blockchain = blockchain
        self.round_num = 0

    def verify_client_signature(self, param_json: str, signature_hex: str, client_pubkey_str: str) -> bool:
        """動態接收每個客戶端的公鑰字串，然後用 rsa.verify 進行驗證."""
        if not param_json or not signature_hex or not client_pubkey_str:
            return False
        try:
            signature = bytes.fromhex(signature_hex)
            public_key = rsa.PublicKey.load_pkcs1(client_pubkey_str.encode('utf-8'))
            rsa.verify(param_json.encode('utf-8'), signature, public_key)
            print("[Server] Signature verified OK.")
            return True
        except Exception as e:
            print(f"[Server] Signature verification failed: {e}")
            return False

    def aggregate_fit(self, rnd: int, results, failures):
        # 1. 在聚合前，先驗證每個客戶端的簽名
        valid_results = []
        for client_idx, fit_res in enumerate(results):
            metrics = fit_res[1].metrics
            if metrics is not None:
                param_json = metrics.get("param_json", "")
                signature_hex = metrics.get("signature", "")
                client_pubkey_str = metrics.get("client_public_key", "")
                verified = self.verify_client_signature(param_json, signature_hex, client_pubkey_str)
                if not verified:
                    print(f"[Server] Client {client_idx} signature invalid, skip it.")
                    continue
            valid_results.append(fit_res)

        # 2. 呼叫父類別的方法 (FedAvg) 進行參數聚合
        aggregated_parameters, aggregated_metrics = super().aggregate_fit(rnd, valid_results, failures)

        # 3. 上鏈 (若 aggregated_parameters 不為 None)
        if aggregated_parameters is not None:
            np_arrays = parameters_to_ndarrays(aggregated_parameters)
            arrays_as_lists = [arr.tolist() for arr in np_arrays]
            aggregated_parameters_json = json.dumps(arrays_as_lists)

            self.blockchain.add_federated_learning_transaction(aggregated_parameters_json, rnd)
            self.blockchain.add_block_with_aggregated_model(aggregated_parameters_json, rnd)

            self.round_num += 1

        return aggregated_parameters, aggregated_metrics

def main():
    # 初始化區塊鏈
    blockchain = BlockChain()

    # 初始化 Flower 伺服器策略
    strategy = BlockchainFedAvg(
        blockchain=blockchain,
        fraction_fit=0.5,
        fraction_evaluate=0.5,
        min_fit_clients=2,
        min_evaluate_clients=2,
        min_available_clients=2,
        evaluate_metrics_aggregation_fn=weighted_average,         # 聚合測試指標
        fit_metrics_aggregation_fn=fit_metrics_aggregation_fn,    # 聚合訓練指標
    )

    fl.server.start_server(
        server_address="0.0.0.0:8080",
        config=fl.server.ServerConfig(num_rounds=3),
        strategy=strategy,
    )

if __name__ == "__main__":
    main()
