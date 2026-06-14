import pika
import json

# RabbitMQ 连接配置
RABBITMQ_HOST = "localhost"
QUEUE_NAME = "library.events"

# 模拟多种业务事件
test_events = [
    {"event_type": "search.books", "payload": {"query": "Python编程", "category": "计算机"}},
    {"event_type": "search.books", "payload": {"query": "三国演义", "category": "文学"}},
    {"event_type": "auth.login_success", "payload": {"reader_id": "001"}},
    {"event_type": "search.books", "payload": {"query": "数据结构", "category": "计算机"}},
    {"event_type": "auth.login_failed", "payload": {"reader_id": "002"}},
]

def send_message():
    try:
        # 建立连接
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        channel = connection.channel()

        # 声明持久队列（和项目配置保持一致）
        channel.queue_declare(queue=QUEUE_NAME, durable=True)

        print("===== 开始发送测试消息 =====")
        for idx, event in enumerate(test_events, 1):
            # 转为 JSON 字符串
            msg_body = json.dumps(event, ensure_ascii=False)
            # 发送持久化消息
            channel.basic_publish(
                exchange="",
                routing_key=QUEUE_NAME,
                body=msg_body,
                properties=pika.BasicProperties(delivery_mode=2)  # 消息持久化
            )
            print(f"第{idx}条消息已发送: {event}")

        print("===== 所有消息发送完成 =====")
        connection.close()

    except Exception as e:
        print(f"发送消息失败：{str(e)}")

if __name__ == "__main__":
    send_message()