# centralized.py

import torch
from torch import nn
import torch.nn.functional as F
from torchvision.transforms import Compose, ToTensor, Normalize, RandomCrop, RandomHorizontalFlip
from torch.utils.data import DataLoader
from torchvision.datasets import CIFAR10
from tqdm import tqdm

from .model_lora_resnet import ResNet18LoRA  # 以 LoRA 方式擴充的 ResNet18

DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print(f"[Info] Using device: {DEVICE}")

def load_data():
    """
    加入 Data Augmentation:
    - RandomCrop(32, padding=4): 隨機裁剪 + 邊界填充
    - RandomHorizontalFlip(): 隨機水平翻轉
    """
    transform_train = Compose([
        RandomCrop(32, padding=4),
        RandomHorizontalFlip(),
        ToTensor(),
        Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])
    transform_test = Compose([
        ToTensor(),
        Normalize((0.5, 0.5, 0.5),(0.5, 0.5, 0.5))
    ])

    trainset = CIFAR10("./data", train=True, download=True, transform=transform_train)
    testset = CIFAR10("./data", train=False, download=True, transform=transform_test)

    # 調整 batch_size，如果您算力充足可提高 batch_size (如64)
    trainloader = DataLoader(trainset, batch_size=32, shuffle=True)
    testloader = DataLoader(testset, batch_size=32)
    return trainloader, testloader

def load_model():
    """
    回傳 LoRA + Pretrained ResNet18
    rank=4 只在最後 fc 做低秩微調。
    """
    net = ResNet18LoRA(num_classes=10, rank=4)
    net.to(DEVICE)
    return net

def train(net, trainloader, epochs):
    """
    - 改用 Adam 優化器 (lr=1e-3 只是範例, 可再調整)
    - epochs: 視情況可增加, 如10或20
    """
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(
        filter(lambda p: p.requires_grad, net.parameters()),
        lr=1e-3
    )

    net.train()
    for epoch in range(epochs):
        print(f"Epoch {epoch+1}/{epochs}")
        running_loss = 0.0
        total, correct = 0, 0
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

        avg_loss = running_loss / len(trainloader)
        acc = correct / total
        print(f"[Train] Epoch {epoch+1}/{epochs} => Loss: {avg_loss:.4f}, Accuracy: {acc:.4f}")

def test(net, testloader):
    """
    測試階段: 保持原本流程
    """
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
            correct += (torch.max(outputs, 1)[1] == labels).sum().item()

    avg_loss = total_loss / len(testloader)
    acc = correct / total
    return avg_loss, acc

if __name__ == "__main__":
    net = load_model()
    trainloader, testloader = load_data()

    # 調整 epochs 至更大, 如10
    train(net, trainloader, epochs=10)

    loss, accuracy = test(net, testloader)
    print(f"[Test] Loss: {loss:.5f}, Accuracy: {accuracy:.3f}")
