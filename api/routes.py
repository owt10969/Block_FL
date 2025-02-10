from flask import Flask, request, jsonify
from blockchain.transaction import Transaction
from mq.rabbitmq_client import send_transaction_message
import json

try:
    from main import fed_Blockchain # import from main.py
except ImportError:
    fed_Blockchain = None

app = Flask(__name__)

@app.route('/balance/<string:address>', methods=['GET'])
def get_balance(address): # 取得指定位置的餘額
    if not fed_Blockchain:
        return jsonify({"error": "Blockchain not initialized"}), 500
    balance = fed_Blockchain.get_balance(address)
    return jsonify({"address": address, "balance": balance})

@app.route('/pendding/transaction', methods=['POST']) # 新增交易到pending_transaction
"""
    新增交易到 pending_transactions
    Body 參數舉例:
    {
        "sender": "public_key_string",
        "receiver": "some_address",
        "amount": 10,
        "fee": 1,
        "signature": "base64_signature"
    }
    """
def add_transaction():
    data = request.get_json() or {}
    tx_data = {
        "sender": data.get("sender", ""),
        "receiver": data.get("receiver", ""),
        "amount": data.get("amount", 0),
        "fee": data.get("fee", 0),
        "signature": data.get("signature", ""),
        "message": data.get("message", "")
    }

    send_transaction_message(tx_data) # 塞進ＭＱ

    return jsonify({"message": "Transaction request accepted. Will be processed asynchronously."})


@app.route('/mining/mine_block', methods=['POST']) # 手動觸發挖礦
"""
手動觸發挖礦
Body 參數舉例:
{
    "miner": "miner_address"
}
"""
def mine_block():
    if not fed_Blockchain:
        return jsonify({"error": "Blockchain not initialized"}), 500
    
    data = request.get_json() or {}
    miner_address = data.get("miner")

    if not miner_address:
        return jsonify({"error": "Missing miner address."}), 400
    
    result = fed_Blockchain.mine_block(miner_address)

    current_diff = fed_Blockchain.adjust_difficulty() # 調整難度

    return jsonify({
        "mined": True if result not False else False
        "current_difficulty": current_diff
    })

@app.route('/blockchain/getChain') # 取得整條區塊鏈
def get_all_blocks():
    if not fed_Blockchain:
        return jsonify({"error": "Blockchain not initializer"}), 500
    
    chain_data = []
    for idx, block in enumerate(fed_Blockchain.chain):
        block_info = {
            "index": idx,
            "hash": block.hash,
            "previous_hash": block.previous_hash,
            "timestamp": block.timestamp,
            "nonce": block.nonce,
            "miner": block.miner,
            "miner_rewards": block.miner_rewards,
            "difficulty": block.difficulty,
            "transactions": []
        }
        for tx in block.transaction:
            block_info["transactions"].append({
                "sender": tx.sender,
                "receiver": tx.receiver,
                "amounts": tx.amounts,
                "fee": tx.fee,
                "message": tx.message,
                "hash_value": tx.hash_value,
                "metadata": tx.metadata
            })
        chain_data.append(block_info)
    
    return jsonify({"chain": chain_data})

@app.route('/blockchain/verifyChain', methods=['GET'])
def verify_chain():
    """
    驗證整條區塊鏈的完整性
    GET /blockchain/verifyChain
    """
    if not fed_Blockchain:
        return jsonify({"error": "Blockchain not initialized"}), 500

    result = fed_Blockchain.verify_blockchain()
    return jsonify({"verify_result": result})


@app.route('/wallet/new_address', methods=['GET'])
def generate_new_address():
    """
    產生新的錢包地址 (公私鑰)
    GET /wallet/new_address
    回傳範例:
    {
      "address": "<public_key_address>",
      "private_key": "<private_key_string>"
    }
    """
    if not fed_Blockchain:
        return jsonify({"error": "Blockchain not initialized"}), 500

    address, private_key = fed_Blockchain.generate_address()
    return jsonify({
        "address": address,
        "private_key": private_key
    })


@app.route('/p2p/nodes', methods=['GET'])
def get_all_nodes():
    """
    查詢目前已知的節點清單
    GET /p2p/nodes
    """
    if not fed_Blockchain:
        return jsonify({"error": "Blockchain not initialized"}), 500

    return jsonify({"nodes": list(fed_Blockchain.node_address)})


@app.route('/p2p/add_node', methods=['POST'])
def add_node():
    """
    新增節點到 node_address
    POST /p2p/add_node
    範例 JSON:
    {
      "node": "127.0.0.1:5001"
    }
    """
    if not fed_Blockchain:
        return jsonify({"error": "Blockchain not initialized"}), 500

    data = request.get_json() or {}
    node = data.get("node", "")
    if not node:
        return jsonify({"error": "Missing node address"}), 400

    fed_Blockchain.node_address.add(node)
    return jsonify({"message": f"Node {node} added", "nodes": list(fed_Blockchain.node_address)})


@app.route('/p2p/clone_blockchain', methods=['POST'])
def clone_blockchain():
    """
    從指定節點複製整條區塊鏈
    POST /p2p/clone_blockchain
    範例 JSON:
    {
      "target_node": "127.0.0.1:5001"
    }
    """
    if not fed_Blockchain:
        return jsonify({"error": "Blockchain not initialized"}), 500

    data = request.get_json() or {}
    target_node = data.get("target_node", "")
    if not target_node:
        return jsonify({"error": "Missing target_node"}), 400

    fed_Blockchain.clone_blockchain(target_node)
    return jsonify({"message": f"Cloned blockchain from {target_node}"})


# 若需要廣播交易/區塊的 API，也可在這邊加上：
@app.route('/p2p/broadcast_transaction', methods=['POST'])
def broadcast_transaction():
    """
    手動廣播交易給其他節點
    POST /p2p/broadcast_transaction
    範例 JSON:
    {
      "sender": "public_key_string",
      "receiver": "some_address",
      "amount": 10,
      "fee": 1,
      "message": "Some note",
      "signature": "base64_signature"
    }
    """
    if not fed_Blockchain:
        return jsonify({"error": "Blockchain not initialized"}), 500

    data = request.get_json() or {}
    sender = data.get("sender", "")
    receiver = data.get("receiver", "")
    amount = data.get("amount", 0)
    fee = data.get("fee", 0)
    signature = data.get("signature", "")
    message = data.get("message", "")

    # 直接建立交易物件
    new_tx = Transaction(
        sender=sender,
        receiver=receiver,
        amounts=amount,
        fee=fee,
        message=message,
        hash_value="",
        metadata={}
    )

    success, result_message = fed_Blockchain.add_transaction(new_tx, signature)
    if success:
        fed_Blockchain.broadcast_transaction(new_tx)

    return jsonify({
        "success": success,
        "message": result_message
    })


@app.route('/p2p/broadcast_block', methods=['POST'])
def broadcast_block():
    """
    手動廣播區塊給其他節點
    通常真實場景下不會手動呼叫此 API，
    而是礦工挖到區塊後自動廣播。
    """
    if not fed_Blockchain:
        return jsonify({"error": "Blockchain not initialized"}), 500

    block_data = request.get_json() or {}
    fed_Blockchain.broadcast_block(block_data)
    return jsonify({"message": "Broadcast block request sent"})

@app.route('/p2p/broadcast_message', methods=['POST'])
def broadcast_message():
    """
    向所有已知節點廣播一個自訂的 request/data 訊息
    
    POST /p2p/broadcast_message
    範例 JSON:
    {
      "request": "notify_all",
      "data": {
        "msg": "Hello nodes!",
        "timestamp": 1234567890
      }
    }
    """
    if not fed_Blockchain:
        return jsonify({"error": "Blockchain not initialized"}), 500

    payload = request.get_json() or {}
    req_type = payload.get("request", "")
    req_data = payload.get("data", {})

    if not req_type:
        return jsonify({"error": "Missing 'request' field in JSON body"}), 400

    # 呼叫區塊鏈的廣播方法
    fed_Blockchain.broadcast_message_to_nodes(req_type, req_data)

    return jsonify({
        "message": "Broadcast message sent to all nodes.",
        "request": req_type,
        "data": req_data,
        "nodes": list(fed_Blockchain.node_address)
    })


