# lora_linear.py (獨立檔案或放一起)
import math
import torch
from torch import nn

class LoRALinear(nn.Module):
    """
    簡化版 LoRA：只針對線性層做 rank-r 的增量。
    凍結 main_weight，僅更新 lora_A, lora_B。
    """
    def __init__(self, in_features, out_features, rank=4, bias=True):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.rank = rank

        # 原權重 (frozen)
        self.main_weight = nn.Parameter(
            torch.zeros(out_features, in_features),
            requires_grad=False
        )
        nn.init.kaiming_uniform_(self.main_weight, a=math.sqrt(5))

        # LoRA 欄位
        self.lora_A = nn.Parameter(torch.zeros(rank, in_features))
        self.lora_B = nn.Parameter(torch.zeros(out_features, rank))
        nn.init.kaiming_uniform_(self.lora_A, a=math.sqrt(5))
        nn.init.kaiming_uniform_(self.lora_B, a=math.sqrt(5))

        # bias
        if bias:
            self.bias = nn.Parameter(torch.zeros(out_features))
        else:
            self.register_parameter('bias', None)

    def forward(self, x):
        lora_increment = self.lora_B @ self.lora_A  # (out_features, in_features)
        effective_weight = self.main_weight + lora_increment  # shape同 main_weight
        out = x.matmul(effective_weight.T)
        if self.bias is not None:
            out += self.bias
        return out
