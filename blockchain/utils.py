# blockchain/utils.py

import hashlib
import json

def compute_hash(block):
    """
    計算給定區塊的哈希值。
    """
    block_string = json.dumps(block, sort_keys=True).encode()
    return hashlib.sha256(block_string).hexdigest()

def serialize_transaction(transaction):
    """
    將交易物件序列化為字典。
    """
    return transaction.to_dict()

def deserialize_transaction(tx_dict):
    """
    從字典反序列化為交易物件。
    """
    from .transaction import Transaction
    return Transaction.from_dict(tx_dict)
