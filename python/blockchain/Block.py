import hashlib
import json
import time

class Block:
    def __init__(self, previous_hash, difficulty, miner, miner_rewards):
        self.previous_hash = previous_hash  # 前一個區塊的哈希值
        self.hash = ''                      # 當前區塊的哈希值，初始為空
        self.difficulty = difficulty        # 挖礦難度
        self.nonce = 0                      # 工作量證明的隨機數
        self.timestamp = int(time.time())   # 區塊創建的時間戳
        self.transactions = []              # 區塊中的交易列表
        self.miner = miner                  # 挖礦者的地址
        self.miner_rewards = miner_rewards  # 挖礦獎勵

    def calculate_hash(self):
        """
        計算區塊的哈希值，基於區塊的內容（不包含自身的哈希值）。
        """
        # 將交易轉換為字典並序列化
        transactions_dict = [tx.to_dict() for tx in self.transactions]
        block_content = {
            'previous_hash': self.previous_hash,
            'timestamp': self.timestamp,
            'transactions': transactions_dict,
            'nonce': self.nonce,
            'difficulty': self.difficulty,
            'miner': self.miner,
            'miner_rewards': self.miner_rewards
        }

        # 轉json
        block_string = json.dumps(block_content, sort_keys=True).encode()

        return hashlib.sha256(block_string).hexdigest()

    def __repr__(self):
        return f"Block(Hash: {self.hash}, Previous Hash: {self.previous_hash}, Nonce: {self.nonce}, Timestamp: {self.timestamp})"
