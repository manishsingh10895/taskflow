import pika, json
import os
from pathlib import Path
from dotenv import load_dotenv
from services.notification.app.handlers import (
    handle_new_task,
    handle_task_deleted,
)

env_path = Path(__file__).resolve().parents[3] / ".env"

load_dotenv(dotenv_path=env_path)

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")


Q = "notification"


def consume_task_created():
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = connection.channel()
    channel.exchange_declare(exchange="notifications", exchange_type="topic")
    channel.queue_declare(queue="notifications.task_created", durable=True)
    channel.queue_bind(
        exchange="notifications",
        queue="notifications.task_created",
        routing_key="task.created",
    )

    def callback(ch, method, properties, body):
        data = json.loads(body)
        print(f" [x] Received {data}")
        handle_new_task(data)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(
        queue="notifications.task_created", on_message_callback=callback
    )
    print(" [*] Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()


def consume_task_deleted():
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = connection.channel()
    channel.exchange_declare(exchange="notifications", exchange_type="topic")
    channel.queue_declare(queue="notifications.task_deleted", durable=True)
    channel.queue_bind(
        exchange="notifications",
        queue="notifications.task_deleted",
        routing_key="task.deleted",
    )

    def callback(ch, method, properties, body):
        data = json.loads(body)
        print(f" [x] Received {data}")
        handle_task_deleted(data)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(
        queue="notifications.task_deleted", on_message_callback=callback
    )
    print(" [*] Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()


