import os

from django.core.management.base import BaseCommand
import json
from kombu import Connection, Queue, Consumer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone
from decimal import Decimal
from trading.models import PriceStamp, ChartType, Candle
from collections import defaultdict, deque

# chart_symbol → очередь последних 5 цен
price_buffer = defaultdict(lambda: deque(maxlen=5))

class Command(BaseCommand):
    help = 'Запуск rabbit listener и трансляция сообщений в WebSocket'

    def handle(self, *args, **options):
        channel_layer = get_channel_layer()

        def handle_message(body, message):
            data = json.loads(body)
            print("[RabbitMQ] Получено:", data)

            if data.get("type") == "message":
                try:
                    symbol = data["chart_type"]
                    price = Decimal(data["price"])
                    now = timezone.now()
                    chart = ChartType.objects.get(symbol=symbol)

                    # Сохраняем PriceStamp
                    PriceStamp.objects.create(
                        chart_type=chart,
                        price=price,
                        time=now
                    )

                    # Добавляем в буфер
                    buf = price_buffer[symbol]
                    buf.append((price, now))

                    # Если 5 цен — создаём свечу и очищаем буфер
                    if len(buf) == 5:
                        prices, times = zip(*buf)
                        Candle.objects.create(
                            chart_type=chart,
                            time=times[-1],  # Время свечи — последняя цена
                            open_price=prices[0],
                            close_price=prices[-1],
                            min_price=min(prices),
                            max_price=max(prices)
                        )
                        print(f"[Candle] Создана свеча для {symbol} с ценами: {prices}")

                        buf.clear()  # Очищаем буфер

                except Exception as e:
                    print(f"[ERROR] Ошибка при обработке: {e}")

            # WebSocket
            async_to_sync(channel_layer.group_send)(
                "prices",
                {
                    "type": "send_price",
                    "data": data
                }
            )

            message.ack()

        print("[RabbitMQ] Слушатель запущен")
        rabbit_url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672//")
        with Connection(rabbit_url) as conn:
            queue = Queue("price_updates", durable=True)
            with Consumer(conn, queues=queue, callbacks=[handle_message], accept=["json"]):
                while True:
                    conn.drain_events()