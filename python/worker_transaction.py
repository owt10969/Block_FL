import pika
import json
import time
from blockchain.blockchain import BlockChain
from blockchain.transaction import Transaction

RABBIT_HOST = "localhost" # TODO: Fetch from config.
RABBIT_QUEUE = "transaction_queue" # TODO: Fetch from config.

try:
    from main import fed_Blockchain # import from main.py
except ImportError:
    fed_Blockchain = None


def callback(ch, method, properties, body):
    """
    收到交易訊息時的處理函式
    """
    # 1. 將 body 反序列化成 dict
    msg = json.loads(body.decode("utf-8"))
    print("[Worker] Received message:", msg)

    # 2. 建立 Transaction 物件
    new_tx = Transaction(
        sender=msg.get("sender", ""),
        receiver=msg.get("receiver", ""),
        amounts=msg.get("amount", 0),
        fee=msg.get("fee", 0),
        message=msg.get("message", ""),
        hash_value="",
        metadata={}
    )
    signature = msg.get("signature", "")

    success, result_message = fed_BlockChain.add_transaction(new_tx, signature)
    print("[Worker] Add transaction result:", success, result_message)

    # 4. 手動回應 RabbitMQ，表示此訊息已成功處理
    ch.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == "__main__":
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBIT_HOST))
    channel = connection.channel()

    channel.queue_declare(queue=RABBIT_QUEUE, durable=True)
    # 設置 prefetch_count = 1，確保 worker 一次只取一筆未 ack 的訊息
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=RABBIT_QUEUE, on_message_callback=callback)

    print("[Worker] Waiting for messages. Press CTRL+C to exit.")
    channel.start_consuming()
