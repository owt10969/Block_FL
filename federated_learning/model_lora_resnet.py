# model_lora_resnet.py

import torch
import torch.nn as nn
import torchvision.models as models
from .lora_linear import LoRALinear  

class ResNet18LoRA(nn.Module):
    def __init__(self, num_classes=10, rank=4):
        super(ResNet18LoRA, self).__init__()
        # 1. 取得預訓練的 resnet18
        self.base = models.resnet18(pretrained=True)
        # 2. 凍結所有層
        for param in self.base.parameters():
            param.requires_grad = False

        # 3. 取得原 fc in_features
        in_feats = self.base.fc.in_features
        # 4. 用 LoRALinear 替換 resnet18 的最後一層
        self.lora_fc = LoRALinear(in_feats, num_classes, rank=rank, bias=True)

        # 5. 也可以保留 bias 原本 ?? 
        #   這裡先採用 LoRALinear 自帶 bias

    def forward(self, x):
        # 讓 base resnet18 走到 flatten layer前 => self.base's forward
        # resnet18 的 forward -> 但最後一層 fc 我們自己接
        # 簡易作法：把 fc 替換掉
        x = self.base.relu(self.base.bn1(self.base.conv1(x)))
        x = self.base.layer1(self.base.maxpool(x))
        x = self.base.layer2(x)
        x = self.base.layer3(x)
        x = self.base.layer4(x)
        x = self.base.avgpool(x)
        x = torch.flatten(x, 1)
        # 進行 LoRA FC
        x = self.lora_fc(x)
        return x
