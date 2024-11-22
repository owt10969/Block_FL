from centralized import load_data, load_model, train, test
from collections import OrderedDict
import flwr as fl
import torch


DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
def set_parameters(model, parameters):
    state_dict_keys = list(model.state_dict().keys())
    if len(parameters) != len(state_dict_keys):
        raise ValueError(
            f"Mismatch between model parameters ({len(state_dict_keys)}) and received parameters ({len(parameters)})"
        )
    state_dict = OrderedDict({
        key: torch.tensor(param).to(DEVICE) for key, param in zip(state_dict_keys, parameters)
    })
    model.load_state_dict(state_dict, strict=True)

net = load_model()
trainloader, testloader = load_data()

class FlowerClient(fl.client.NumPyClient):
    def get_parameters(self, config):
        parameters = [val.cpu().numpy() for _, val in net.state_dict().items()]
        print("Client sending parameters to server:")
        for name, param in zip(net.state_dict().keys(), parameters):
            print(f"{name}: {param.shape}")
        return parameters
    
    def fit(self, parameters, config):
        set_parameters(net, parameters)
        train(net, trainloader, epochs=1)
        return self.get_parameters({}), len(trainloader.dataset), {}
    
    def evaluate(self, parameters, config):
        set_parameters(net, parameters)
        loss, accuracy = test(net, testloader)
        return float(loss), len(testloader.dataset), {"accuracy": accuracy}

fl.client.start_numpy_client(
    server_address="127.0.0.1:8080",
    client=FlowerClient(),
)