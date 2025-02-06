# blockchain_test.py

import sys
import time
import threading
import hashlib
import json
import pickle
import socket

# 確保 blockchain 模組在 Python 路徑中
sys.path.append('.')

from blockchain.blockchain import BlockChain
from blockchain.transaction import Transaction
from blockchain.Block import Block

import rsa

def generate_keys():
    """
    生成 RSA 公私鑰對。
    """
    (public_key, private_key) = rsa.newkeys(512)
    public_pem = public_key.save_pkcs1().decode('utf-8')
    private_pem = private_key.save_pkcs1().decode('utf-8')
    return public_pem, private_pem

def sign_transaction(private_key_pem, transaction_str):
    """
    使用私鑰簽名交易字串。
    """
    private_key = rsa.PrivateKey.load_pkcs1(private_key_pem.encode('utf-8'))
    signature = rsa.sign(transaction_str.encode('utf-8'), private_key, 'SHA-256')
    return signature

def test_blockchain():
    print("=== 區塊鏈測試開始 ===\n")

    # 1. 生成創世礦工的公私鑰對
    print("生成創世礦工的 RSA 密鑰對...")
    genesis_miner_pub, genesis_miner_priv = generate_keys()
    print("創世礦工的密鑰對生成完成。\n")

    # 2. 創建區塊鏈實例
    print("創建區塊鏈實例...")
    blockchain = BlockChain(genesis_miner_pub_key=genesis_miner_pub)
    print("區塊鏈創建完成。\n")

    # 3. 顯示創世區塊
    print("顯示創世區塊:")
    blockchain.display_chain()
    print("\n")

    # 4. 生成其他參與者的密鑰對
    print("生成其他參與者的 RSA 密鑰對...")
    alice_pub, alice_priv = generate_keys()
    bob_pub, bob_priv = generate_keys()
    charlie_pub, charlie_priv = generate_keys()
    print("其他參與者的密鑰對生成完成。\n")

    # 5. 創建並添加一筆從創世礦工到 Alice 的交易，以給予 Alice 初始餘額
    print("創建並添加一筆從創世礦工到 Alice 的交易...")
    tx_genesis_to_alice = Transaction(
        sender=genesis_miner_pub,  # 創世礦工的公鑰作為發送者
        receiver=alice_pub,
        amounts=10,  # 調整為 10，符合創世礦工的餘額
        fee=0,
        message="Genesis Miner pays Alice",
        hash_value="hash_genesis_to_alice",
        metadata={"note": "Initial funding for Alice"}
    )

    # 簽名交易
    tx_genesis_to_alice_str = blockchain.transaction_to_string(tx_genesis_to_alice)
    tx_genesis_to_alice_signature = sign_transaction(genesis_miner_priv, tx_genesis_to_alice_str)

    # 添加交易到區塊鏈
    result_genesis_tx, message_genesis_tx = blockchain.add_transaction(tx_genesis_to_alice, signature=tx_genesis_to_alice_signature)
    print(f"創世礦工到 Alice 的交易添加結果: {message_genesis_tx}\n")

    # 6. 挖礦以確認創世礦工到 Alice 的交易
    print("挖礦以確認創世礦工到 Alice 的交易...")
    new_block1 = blockchain.mine_block(miner=genesis_miner_pub)
    if new_block1:
        print("挖礦完成，區塊已添加。\n")
    else:
        print("挖礦被中斷。\n")

    # 7. 顯示更新後的區塊鏈
    print("顯示更新後的區塊鏈:")
    blockchain.display_chain()
    print("\n")

    # 8. 創建並添加其他交易（Alice -> Bob, Bob -> Charlie, Charlie -> Dave）
    print("創建並添加其他交易...")
    # 定義交易
    tx1 = Transaction(
        sender=alice_pub,
        receiver=bob_pub,
        amounts=50,
        fee=1,
        message="Alice pays Bob",
        hash_value="hash_tx1",
        metadata={"note": "第一筆交易"}
    )
    tx2 = Transaction(
        sender=bob_pub,
        receiver=charlie_pub,
        amounts=30,
        fee=0.5,
        message="Bob pays Charlie",
        hash_value="hash_tx2",
        metadata={"note": "第二筆交易"}
    )
    tx3 = Transaction(
        sender=charlie_pub,
        receiver="Dave",  # 假設 Dave 是系統或另一個帳戶
        amounts=20,
        fee=0.2,
        message="Charlie pays Dave",
        hash_value="hash_tx3",
        metadata={"note": "第三筆交易"}
    )

    # 簽名交易
    tx1_str = blockchain.transaction_to_string(tx1)
    tx1_signature = sign_transaction(alice_priv, tx1_str)

    tx2_str = blockchain.transaction_to_string(tx2)
    tx2_signature = sign_transaction(bob_priv, tx2_str)

    tx3_str = blockchain.transaction_to_string(tx3)
    tx3_signature = sign_transaction(charlie_priv, tx3_str)

    # 添加交易到區塊鏈
    result1, message1 = blockchain.add_transaction(tx1, signature=tx1_signature)
    print(f"交易1添加結果: {message1}")
    result2, message2 = blockchain.add_transaction(tx2, signature=tx2_signature)
    print(f"交易2添加結果: {message2}")
    result3, message3 = blockchain.add_transaction(tx3, signature=tx3_signature)
    print(f"交易3添加結果: {message3}\n")

    # 9. 顯示未確認的交易
    print("顯示未確認的交易:")
    for tx in blockchain.pending_transactions:
        print(tx.to_dict())
    print("\n")

    # 10. 挖礦，創建新的區塊
    print("開始挖礦，創建新區塊...")
    new_block2 = blockchain.mine_block(miner=alice_pub)
    if new_block2:
        print("挖礦完成，區塊已添加。\n")
    else:
        print("挖礦被中斷。\n")

    # 11. 顯示更新後的區塊鏈
    print("顯示更新後的區塊鏈:")
    blockchain.display_chain()
    print("\n")

    # 12. 檢查區塊鏈有效性
    print("檢查區塊鏈有效性...")
    is_valid = blockchain.verify_blockchain()
    print(f"區塊鏈有效性: {is_valid}\n")

    # 13. 嘗試篡改區塊鏈
    print("嘗試篡改區塊鏈中的一個區塊...")
    if len(blockchain.chain) > 2:
        tampered_block = blockchain.chain[2]
        try:
            tampered_block.transactions[0].amounts = 1000  # 修改交易金額
            tampered_block.hash = tampered_block.calculate_hash()  # 重新計算哈希
            print(f"篡改後的區塊哈希: {tampered_block.hash}")
        except IndexError:
            print("區塊中沒有交易可供篡改。")
    else:
        print("區塊鏈中沒有足夠的區塊進行篡改。")
    print("\n")

    # 14. 再次檢查區塊鏈有效性
    print("再次檢查區塊鏈有效性...")
    is_valid_after_tamper = blockchain.verify_blockchain()
    print(f"區塊鏈有效性 (篡改後): {is_valid_after_tamper}\n")

    print("=== 區塊鏈測試結束 ===")

if __name__ == "__main__":
    test_blockchain()
