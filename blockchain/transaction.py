
import time
class Transaction:
    def __init__(self, sender, receiver, amounts, fee, message,hash_value,metadata):
        self.sender = sender
        self.receiver = receiver
        self.amounts = amounts
        self.fee = fee
        self.message = message
        self.timestamp = int(time.time())
        self.hash_value = hash_value # model 參數 雜湊值
        self.metadata = metadata if metadata else {} # model 參數 元數據
        
    
    def to_dict(self):
        return {
            'sender': self.sender,
            'receiver': self.receiver,
            'amounts': self.amounts,
            'fee': self.fee,
            'message': self.message,
            'timestamp': self.timestamp,
            'hash_value': self.hash_value,
            'metadata': self.metadata
        }
    
    @staticmethod
    def from_dict(transaction_dict):
        return Transaction(
            transaction_dict['sender'],
            transaction_dict['receiver'],
            transaction_dict['amounts'],
            transaction_dict['fee'],
            transaction_dict['message'],
            transaction_dict['hash_value'],
            transaction_dict['metadata']
        )
