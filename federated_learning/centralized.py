import torch
from torch import nn
import torch.nn.functional as F
from torchvision.transforms import (
    Compose,
    ToTensor,
    Normalize,
    RandomCrop,
    RandomHorizontalFlip
)
from torch.utils.data import DataLoader
from torchvision.datasets import CIFAR10
from tqdm import tqdm

DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print(f"[Info] Using device: {DEVICE}")

###############################################################################
# 1. 改良的 CNN 模型結構
###############################################################################
class Net(nn.Module):
    """
    與原本相比，調整部分 layer 參數：
    - conv1: 改成 3->16, kernel_size=3, padding=1
    - conv2: 改成 16->32, kernel_size=3, padding=1
    - fc 的輸入改 accordingly (32 * 8 * 8), 
      也可自行再擴大 channel or 加 layers
    """
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(3, 16, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)
        self.fc1  = nn.Linear(32 * 8 * 8, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 10)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))   # shape: [N,16,16,16]
        x = self.pool(F.relu(self.conv2(x)))   # shape: [N,32,8,8]
        x = x.view(-1, 32 * 8 * 8)             # 改為 (32*8*8)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        return self.fc3(x)


###############################################################################
# 2. 資料載入 (含 Data Augmentation)
###############################################################################
def load_data():
    """
    - 增加資料增強:
      RandomCrop(32, padding=4), RandomHorizontalFlip()
    - Normalize((0.5,0.5,0.5),(0.5,0.5,0.5)) 與原一致
    """
    transform_train = Compose([
        RandomCrop(32, padding=4),
        RandomHorizontalFlip(),
        ToTensor(),
        Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])
    transform_test = Compose([
        ToTensor(),
        Normalize((0.5,0.5,0.5),(0.5,0.5,0.5))
    ])

    trainset = CIFAR10("./data", train=True, download=True, transform=transform_train)
    testset = CIFAR10("./data", train=False, download=True, transform=transform_test)

    trainloader = DataLoader(trainset, batch_size=32, shuffle=True)
    testloader = DataLoader(testset, batch_size=32)
    return trainloader, testloader


###############################################################################
# 3. 訓練函式
###############################################################################
def train(net, trainloader, epochs):
    """
    - 改用 Adam 或調整SGD學習率
    - 此處示範Adam(lr=1e-3), 也可留SGD只調lr=0.001
    - 增加 epoch 數 (例如從5提高到10或20)
    - 回傳最終一個 epoch (loss, acc) 供需要時使用
    """
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(net.parameters(), lr=1e-3)

    net.train()
    for epoch in range(epochs):
        print(f"Epoch {epoch + 1}/{epochs}")
        running_loss = 0.0
        correct = 0
        total = 0

        for images, labels in tqdm(trainloader, desc="Training", leave=False):
            images, labels = images.to(DEVICE), labels.to(DEVICE)
            optimizer.zero_grad()

            outputs = net(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

        epoch_loss = running_loss / len(trainloader)
        epoch_acc = correct / total
        print(f"[Train] Epoch {epoch+1} => Loss: {epoch_loss:.4f}, Acc: {epoch_acc:.4f}")

    # 回傳最終 epoch 的loss/acc (若需要客戶端傳metrics可使用)
    return epoch_loss, epoch_acc


###############################################################################
# 4. 測試函式
###############################################################################
def test(net, testloader):
    criterion = nn.CrossEntropyLoss()
    correct, total, total_loss = 0, 0, 0.0
    net.eval()
    with torch.no_grad():
        for images, labels in tqdm(testloader, desc="Testing", leave=False):
            images, labels = images.to(DEVICE), labels.to(DEVICE)
            outputs = net(images)
            loss = criterion(outputs, labels).item()
            total_loss += loss
            total += labels.size(0)
            correct += (torch.max(outputs,1)[1] == labels).sum().item()
    avg_loss = total_loss / len(testloader)
    acc = correct / total
    return avg_loss, acc

###############################################################################
# 5. 初始化模型
###############################################################################
def load_model():
    net = Net().to(DEVICE)
    return net

###############################################################################
# 6. 主程式 (非聯邦學習情境測試)
###############################################################################
if __name__ == "__main__":
    net = load_model()
    trainloader, testloader = load_data()

    # 原本只有5 epoch => 建議增加到10或更多
    EPOCHS = 10
    train(net, trainloader, EPOCHS)
    loss, accuracy = test(net, testloader)
    print(f"[Test] Loss:{loss:.5f}, Accuracy:{accuracy:.3f}")
