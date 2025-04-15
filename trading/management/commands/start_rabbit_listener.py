from django.core.management.base import BaseCommand
import json
from kombu import Connection, Queue, Consumer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

class Command(BaseCommand):
    help = 'Запуск rabbit listener и трансляция сообщений в WebSocket'

    def handle(self, *args, **options):
        channel_layer = get_channel_layer()

        def handle_message(body, message):
            data = json.loads(body)
            print("[RabbitMQ] Получено:", data)

            async_to_sync(channel_layer.group_send)(
                "prices",
                {
                    "type": "send_price",
                    "data": data
                }
            )
            message.ack()

        print("[RabbitMQ] Слушатель запущен")
        with Connection("amqp://guest:guest@localhost//") as conn:
            queue = Queue("price_updates", durable=True)
            with Consumer(conn, queues=queue, callbacks=[handle_message], accept=["json"]):
                while True:
                    conn.drain_events()