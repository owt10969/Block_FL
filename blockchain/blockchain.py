# blockchain/blockchain.py

import hashlib
import pickle
import socket
import sys
import threading
import time
import random

import rsa
import json
from .Block import Block
from .transaction import Transaction
from .utils import compute_hash
from .p2p import P2PNetwork

class BlockChain:
    """
    一個用來表示區塊鏈的類別。

    屬性 (Attributes)
    ----------
    adjust_difficulty_blocks : int
        在挖出多少區塊後，難度會被調整。
    difficulty : int
        區塊鏈目前的挖礦難度。
    block_time : int
        挖出一個區塊所預期耗費的時間（秒）。
    miner_rewards : int
        礦工挖出區塊後的獎勵。
    block_limitation : int
        每個區塊所能容納的最大交易筆數。
    chain : list
        用來儲存整個區塊鏈的清單。
    pending_transactions : list
        用來儲存尚未被打包的交易清單。
    socket_host : str
        P2P 連線用的主機位址。
    socket_port : int
        P2P 連線用的通訊埠號。
    node_address : set
        節點位址的集合。
    connection_nodes : dict
        儲存連線節點資訊的字典。
    receive_verified_block : bool
        是否已接收到經過驗證的區塊之旗標。

    方法 (Methods)
    -------
    __init__():
        使用預設數值初始化區塊鏈。
    create_genesis_block():
        建立創世區塊。
    initialize_transaction(sender, receiver, amount, fee, message):
        初始化一筆新的交易。
    transaction_to_string(transaction):
        將交易物件轉換為字串格式。
    get_transactions_string(block):
        將區塊中的所有交易轉換為字串格式。
    get_hash(block, nonce):
        產生區塊的雜湊值。
    add_transaction_to_block(block):
        將交易新增至區塊。
    mine_block(miner):
        開始挖礦並產生新的區塊。
    adjust_difficulty():
        調整挖礦的難度。
    get_balance(account):
        取得指定帳戶的餘額。
    verify_blockchain():
        驗證整個區塊鏈的完整性。
    generate_address():
        產生新的錢包位址。
    get_address_from_public(public):
        從公鑰中提取位址。
    extract_from_private(private):
        從私鑰物件中提取私鑰字串。
    add_transaction(transaction, signature):
        將交易加入到待處理交易清單中。
    start():
        開始進行挖礦流程。
    clone_blockchain(address):
        從其他節點複製區塊鏈資料。
    broadcast_block(new_block):
        向其他節點廣播新區塊。
    broadcast_transaction(new_transaction):
        向其他節點廣播新交易。
    broadcast_message_to_nodes(request, data=None):
        向所有已連線的節點廣播指定訊息。
    receive_broadcast_block(block_data):
        接收並驗證其他節點廣播的區塊。
    """

    def __init__(self, genesis_miner_pub_key = ""):
        self.adjust_difficulty_blocks = 10
        self.difficulty = 1
        self.block_time = 30
        self.miner_rewards = 10
        self.block_limitation = 32
        self.chain = []
        self.pending_transactions = []

        # P2P 連線設定
        self.socket_host = "127.0.0.1"
        self.socket_port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
        self.node_address = {f"{self.socket_host}:{self.socket_port}"}
        self.connection_nodes = {}
        if len(sys.argv) == 3:
            self.clone_blockchain(sys.argv[2])
            print(f"Node list: {self.node_address}")
            self.broadcast_message_to_nodes("add_node", f"{self.socket_host}:{self.socket_port}")

        # 接收經過驗證的區塊旗標
        self.receive_verified_block = False
        self.create_genesis_block(genesis_miner_pub_key)

        # 初始化 P2P 網路
        self.p2p = P2PNetwork(self, self.socket_host, self.socket_port)

    def create_genesis_block(self, genesis_miner_pub_key = ""):
        print("Create genesis block...")
        genesis_tx = Transaction(
            sender="0",  # 系統或無效的發送者
            receiver=genesis_miner_pub_key,
            amounts=self.miner_rewards,
            fee=0,
            message="Genesis Block",
            hash_value="0" * 64,
            metadata={"note": "Genesis"}
        )
        genesis_block = Block(previous_hash="0" * 64, difficulty=self.difficulty, miner=genesis_miner_pub_key, miner_rewards=self.miner_rewards)
        genesis_block.transactions.append(genesis_tx)
        genesis_block.hash = genesis_block.calculate_hash()
        self.chain.append(genesis_block)
        print(f"Genesis Block Hash: {genesis_block.hash}")

    def initialize_transaction(self, sender, receiver, amount, fee, message):
        # No need to check balance
        new_transaction = Transaction(sender, receiver, amount, fee, message)
        return new_transaction

    def transaction_to_string(self, transaction):
        transaction_dict = {
            'sender': str(transaction.sender),
            'receiver': str(transaction.receiver),
            'amounts': transaction.amounts,
            'fee': transaction.fee,
            'message': transaction.message
        }
        return str(transaction_dict)

    def get_transactions_string(self, block):
        transaction_str = ''
        for transaction in block.transactions:
            transaction_str += self.transaction_to_string(transaction)
        return transaction_str

    def get_hash(self, block, nonce):
        s = hashlib.sha1()
        s.update(
            (
                block.previous_hash
                + str(block.timestamp)
                + self.get_transactions_string(block)
                + str(nonce)
            ).encode("utf-8")
        )
        h = s.hexdigest()
        return h

    def add_transaction_to_block(self, block):
        # Get the transaction with highest fee by block_limitation
        self.pending_transactions.sort(key=lambda x: x.fee, reverse=True)
        if len(self.pending_transactions) > self.block_limitation:
            transcation_accepted = self.pending_transactions[:self.block_limitation]
            self.pending_transactions = self.pending_transactions[self.block_limitation:]
        else:
            transcation_accepted = self.pending_transactions
            self.pending_transactions = []
        block.transactions = transcation_accepted

    def mine_block(self, miner):
        start = time.process_time()

        last_block = self.chain[-1]
        new_block = Block(previous_hash=last_block.hash, difficulty=self.difficulty, miner=miner, miner_rewards=self.miner_rewards)

        self.add_transaction_to_block(new_block)
        new_block.previous_hash = last_block.hash
        new_block.difficulty = self.difficulty
        new_block.hash = self.get_hash(new_block, new_block.nonce)
        new_block.nonce = random.getrandbits(32)

        while new_block.hash[:self.difficulty] != '0' * self.difficulty:
            new_block.nonce += 1
            new_block.hash = self.get_hash(new_block, new_block.nonce)
            if self.receive_verified_block:
                print(f"[**] Verified received block. Mine next!")
                self.receive_verified_block = False
                return False

        self.broadcast_block(new_block)

        time_consumed = round(time.process_time() - start, 5)
        print(f"Hash: {new_block.hash} @ diff {self.difficulty}; {time_consumed}s")
        self.chain.append(new_block)

    def adjust_difficulty(self):
        if len(self.chain) % self.adjust_difficulty_blocks != 1:
            return self.difficulty
        elif len(self.chain) <= self.adjust_difficulty_blocks:
            return self.difficulty
        else:
            start = self.chain[-self.adjust_difficulty_blocks - 1].timestamp
            finish = self.chain[-1].timestamp
            average_time_consumed = round((finish - start) / self.adjust_difficulty_blocks, 2)
            if average_time_consumed > self.block_time:
                print(f"Average block time:{average_time_consumed}s. Lower the difficulty")
                self.difficulty -= 1 if self.difficulty > 1 else 1
            else:
                print(f"Average block time:{average_time_consumed}s. Increase the difficulty")
                self.difficulty += 1
            return self.difficulty

    def get_balance(self, account):
        balance = 0
        for block in self.chain:
            # Check miner reward
            if block.miner == account:
                balance += block.miner_rewards
            for transaction in block.transactions:
                if transaction.sender == account:
                    balance -= transaction.amounts
                    balance -= transaction.fee
                elif transaction.receiver == account:
                    balance += transaction.amounts
        return balance

    def verify_blockchain(self):
        previous_hash = ''
        for idx, block in enumerate(self.chain):
            if block.calculate_hash() != block.hash:
                print("Error: Hash not matched!")
                return False
            elif previous_hash != block.previous_hash and idx != 0:
                print("Error: Hash not matched to previous_hash")
                return False
            previous_hash = block.hash
        print("Hash correct!")
        return True

    def generate_address(self):
        public, private = rsa.newkeys(512)
        public_key = public.save_pkcs1()
        private_key = private.save_pkcs1()
        return self.get_address_from_public(public_key), \
            self.extract_from_private(private_key)

    def get_address_from_public(self, public):
        address = str(public).replace('\\n', '')
        address = address.replace("b'-----BEGIN RSA PUBLIC KEY-----", '')
        address = address.replace("-----END RSA PUBLIC KEY-----'", '')
        address = address.replace(' ', '')
        return address

    def extract_from_private(self, private):
        private_key = str(private).replace('\\n', '')
        private_key = private_key.replace("b'-----BEGIN RSA PRIVATE KEY-----", '')
        private_key = private_key.replace("-----END RSA PRIVATE KEY-----'", '')
        private_key = private_key.replace(' ', '')
        return private_key

    def add_transaction(self, transaction, signature):
        public_key = transaction.sender 
        public_key_pkcs = rsa.PublicKey.load_pkcs1(public_key.encode('utf-8'))
        transaction_str = self.transaction_to_string(transaction)
        if transaction.fee + transaction.amounts > self.get_balance(transaction.sender):
            return False, "Balance not enough!"
        try:
            # 驗證發送者
            rsa.verify(transaction_str.encode('utf-8'), signature, public_key_pkcs)
            self.pending_transactions.append(transaction)
            return True, "Authorized successfully!"
        except Exception:
            return False, "RSA Verified wrong!"

    def start(self):
        address, private = self.generate_address()
        print(f"Miner address: {address}")
        print(f"Miner private: {private}")
        if len(sys.argv) < 3:
            self.create_genesis_block()
        while True:
            self.mine_block(address)
            self.adjust_difficulty()

    def receive_socket_message(self, connection, address):
        with connection:
            print(f'Connected by: {address}')
            address_concat = f"{address[0]}:{address[1]}"
            while True:
                try:
                    message = b""
                    while True:
                        part = connection.recv(4096)
                        if not part:
                            break
                        message += part
                        if len(part) < 4096:
                            break
                    if not message:
                        break
                    parsed_message = pickle.loads(message)
                except Exception as e:
                    print(f"Failed to parse message from {address_concat}: {e}")
                    continue

                if parsed_message["request"] == "get_balance":
                    print("Start to get the balance for client...")
                    account = parsed_message["address"]
                    balance = self.get_balance(account)
                    response = {
                        "address": account,
                        "balance": balance
                    }
                elif parsed_message["request"] == "transaction":
                    print("Start to transaction for client...")
                    new_transaction = parsed_message["data"]
                    result, result_message = self.add_transaction(
                        new_transaction,
                        parsed_message.get("signature")
                    )
                    response = {
                        "result": result,
                        "result_message": result_message
                    }
                    if result:
                        self.broadcast_transaction(new_transaction)
                # 接收到同步區塊的請求
                elif parsed_message["request"] == "clone_blockchain":
                    print(f"[*] Receive blockchain clone request by {address_concat}...")
                    message = {
                        "request": "upload_blockchain",
                        "blockchain_data": self
                    }
                    try:
                        connection.sendall(pickle.dumps(message))
                    except Exception as e:
                        print(f"Failed to send blockchain data to {address_concat}: {e}")
                    continue
                # 接收到挖掘出的新區塊
                elif parsed_message["request"] == "broadcast_block":
                    print(f"[*] Receive block broadcast by {address_concat}...")
                    self.receive_broadcast_block(parsed_message["data"])
                    continue
                # 接收到廣播的交易
                elif parsed_message["request"] == "broadcast_transaction":
                    print(f"[*] Receive transaction broadcast by {address_concat}...")
                    self.pending_transactions.append(parsed_message["data"])
                    continue
                # 接收到新增節點的請求
                elif parsed_message["request"] == "add_node":
                    print(f"[*] Receive add_node broadcast by {address_concat}...")
                    self.node_address.add(parsed_message["data"])
                    continue
                else:
                    response = {
                        "message": "Unknown command."
                    }
                try:
                    response_bytes = json.dumps(response).encode('utf8')
                    connection.sendall(response_bytes)
                except Exception as e:
                    print(f"Failed to send response to {address_concat}: {e}")

    def clone_blockchain(self, address):
        print(f"Start to clone blockchain by {address}")
        target_host, target_port = address.split(":")
        target_port = int(target_port)
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect((target_host, target_port))
        except Exception as e:
            print(f"Failed to connect to {address}: {e}")
            return
        message = {"request": "clone_blockchain"}
        try:
            client.send(pickle.dumps(message))
        except Exception as e:
            print(f"Failed to send clone request to {address}: {e}")
            client.close()
            return
        response = b""
        print(f"Start to receive blockchain data by {address}")
        while True:
            part = client.recv(4096)
            if not part:
                break
            response += part
            if len(part) < 4096:
                break
        client.close()
        try:
            response = pickle.loads(response)["blockchain_data"]
            self.adjust_difficulty_blocks = response.adjust_difficulty_blocks
            self.difficulty = response.difficulty
            self.block_time = response.block_time
            self.miner_rewards = response.miner_rewards
            self.block_limitation = response.block_limitation
            self.chain = response.chain
            self.pending_transactions = response.pending_transactions
            self.node_address.update(response.node_address)
            print("Blockchain cloned successfully.")
        except Exception as e:
            print(f"Failed to clone blockchain: {e}")

    def broadcast_block(self, new_block):
        self.broadcast_message_to_nodes("broadcast_block", new_block)

    def broadcast_transaction(self, new_transaction):
        self.broadcast_message_to_nodes("broadcast_transaction", new_transaction)

    def broadcast_message_to_nodes(self, request, data=None):
        address_concat = f"{self.socket_host}:{self.socket_port}"
        message = {
            "request": request,
            "data": data
        }
        for node_address in self.node_address:
            if node_address != address_concat:
                target_host, target_port = node_address.split(":")
                target_port = int(target_port)
                try:
                    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    client.connect((target_host, target_port))
                    client.sendall(pickle.dumps(message))
                    client.close()
                except Exception as e:
                    print(f"Failed to connect to {node_address}: {e}")

    def receive_broadcast_block(self, block_data):
        last_block = self.chain[-1]
        # Check the hash of received block
        if block_data.previous_hash != last_block.hash:
            print("[**] Received block error: Previous hash not matched!")
            return False
        elif block_data.difficulty != self.difficulty:
            print("[**] Received block error: Difficulty not matched!")
            return False
        elif block_data.hash != block_data.calculate_hash():
            print(block_data.hash)
            print("[**] Received block error: Hash calculation not matched!")
            return False
        else:
            # 確認該區塊是否滿足難度
            if block_data.hash[:self.difficulty] == '0' * self.difficulty:
                for transaction in block_data.transactions:
                    try:
                        self.pending_transactions.remove(transaction)
                    except ValueError:
                        print(f"[Warning] Transaction not found in pending: {transaction.hash_value}")

                self.receive_verified_block = True
                self.chain.append(block_data)
                print(f"Block #{len(self.chain)-1} received and added to the chain.")
                return True
            else:
                print(f"[**] Received block error: Hash not matched by diff!")
                return False
            
    def add_federated_learning_transaction(self, aggregated_parameters, round_num):
        """
        將聯邦學習聚合後的模型參數作為一筆交易添加到待處理交易清單中。
        """
        tx = Transaction(
            sender="FederatedLearningServer",
            receiver="GlobalModel",
            amounts=0,
            fee=0,
            message=f"Round {round_num} Aggregated Model Parameters",
            hash_value=aggregated_parameters,
            metadata={"round": round_num, "timestamp": int(time.time())}
        )
        self.pending_transactions.append(tx)
        print(f"Added FL transaction for round {round_num} to pending transactions.")

    def add_block_with_aggregated_model(self, aggregated_parameters, round_num):
        """
        創建一個新的區塊，包含聯邦學習聚合後的模型參數。
        """
        new_block = Block(previous_hash=self.chain[-1].hash, difficulty=self.difficulty, miner="FederatedLearningServer", miner_rewards=self.miner_rewards)
        # 將聚合後的模型參數作為交易添加到區塊
        tx = Transaction(
            sender="FederatedLearningServer",
            receiver="GlobalModel",
            amounts=0,
            fee=0,
            message=f"Round {round_num} Aggregated Model Parameters",
            hash_value=aggregated_parameters,
            metadata={"round": round_num, "timestamp": int(time.time())}
        )
        new_block.transactions.append(tx)
        # 計算哈希並挖礦
        new_block.hash = new_block.calculate_hash()
        while new_block.hash[:self.difficulty] != '0' * self.difficulty:
            new_block.nonce += 1
            new_block.hash = new_block.calculate_hash()
        # 將新區塊添加到區塊鏈
        self.chain.append(new_block)
        print(f"New block added with hash: {new_block.hash}")

    def display_chain(self):
        """
        顯示整個區塊鏈的內容。
        """
        print("=== 區塊鏈內容 ===")
        for idx, block in enumerate(self.chain):
            print(f"\n區塊 #{idx}:")
            print(f"  哈希值: {block.hash}")
            print(f"  前一區塊哈希值: {block.previous_hash}")
            print(f"  Nonce: {block.nonce}")
            print(f"  時間戳: {block.timestamp}")
            print(f"  挖礦者: {block.miner}")
            print(f"  挖礦獎勵: {block.miner_rewards}")
            print(f"  交易列表:")
            for tx in block.transactions:
                print(f"    - 發送者: {tx.sender}")
                print(f"      接收者: {tx.receiver}")
                print(f"      金額: {tx.amounts}")
                print(f"      手續費: {tx.fee}")
                print(f"      訊息: {tx.message}")
                print(f"      雜湊值: {tx.hash_value}")
                print(f"      元數據: {tx.metadata}")
        print("\n=== 區塊鏈結束 ===\n")