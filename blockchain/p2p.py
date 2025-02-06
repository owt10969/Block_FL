# blockchain/p2p.py

import socket
import pickle
import threading

class P2PNetwork:
    """
    A class to represent a Peer-to-Peer (P2P) network for a blockchain.
    Attributes
    ----------
    blockchain : Blockchain
        An instance of the Blockchain class to handle blockchain operations.
    socket_host : str
        The host address for the socket server.
    socket_port : int
        The port number for the socket server.
    Methods
    -------
    start_socket_server():
        Starts the socket server for P2P connections.
    wait_for_socket_connection():
        Waits for and accepts incoming socket connections.
    """
    def __init__(self, blockchain, socket_host, socket_port):
        self.blockchain = blockchain
        self.socket_host = socket_host
        self.socket_port = socket_port
        self.start_socket_server()

    def start_socket_server(self):
        """
        啟動 P2P 連線的 Socket 伺服器。
        """
        t = threading.Thread(target=self.wait_for_socket_connection, daemon=True)
        t.start()

    def wait_for_socket_connection(self):
        """
        等待並接受外部的 Socket 連線。
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.socket_host, self.socket_port))
            s.listen()
            print(f"P2P Server listening on {self.socket_host}:{self.socket_port}...")
            while True:
                conn, address = s.accept()
                client_handler = threading.Thread(
                    target=self.blockchain.receive_socket_message,
                    args=(conn, address),
                    daemon=True
                )
                client_handler.start()
