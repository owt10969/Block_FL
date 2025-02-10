import pika
import json

RABBIT_HOST = "localhost"   # 或 Docker container host, 亦可放到設定檔
RABBIT_QUEUE = "transaction_queue"  # 自訂佇列名稱

def get_connection():
    """
    建立並回傳 RabbitMQ 連線
    """
    return pika.BlockingConnection(pika.ConnectionParameters(host=RABBIT_HOST))

def send_transaction_message(tx_data):
    """
    將交易相關資料發送到 RabbitMQ 佇列
    tx_data 預期是一個 dict，包含交易所需欄位
    """
    connection = get_connection()
    channel = connection.channel()
    # 建立 / 宣告佇列（確保存在）
    channel.queue_declare(queue=RABBIT_QUEUE, durable=True)

    # 將 dict 轉成 JSON，再發送
    message_body = json.dumps(tx_data)
    channel.basic_publish(
        exchange='',
        routing_key=RABBIT_QUEUE,
        body=message_body,
        properties=pika.BasicProperties(
            delivery_mode=2  # 設為 2 代表持久化
        )
    )

    connection.close()