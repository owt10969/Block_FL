# main.py

import sys
from blockchain.blockchain import BlockChain

def main():
    blockchain = BlockChain()
    blockchain.start()

if __name__ == '__main__':
    main()
