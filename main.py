import threading

def auto_mining_loop(blockchain, miner_address):
    while True:
        blockchain.mine_block(miner_address)
        blockchain.adjust_difficulty()
        # 視需求 sleep 幾秒，或判斷有無 pending tx 再挖

def main():
    fed_Blockchain = BlockChain()
    p2p = P2PNetwork(fed_Blockchain, "127.0.0.1", 5000)

    # 用多執行緒背景挖礦
    miner_thread = threading.Thread(
        target=auto_mining_loop, 
        args=(fed_Blockchain, "DefaultMinerAddress"), 
        daemon=True
    )
    miner_thread.start()

    app.run(port=8000, debug=True)
