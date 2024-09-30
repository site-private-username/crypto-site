from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from trading.models import Candle, Bet, ChartType
from decimal import Decimal
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Populate the database with test data'

    def handle(self, *args, **kwargs):
        # Create test users
        for i in range(5):
            username = f'testuser{i}'
            email = f'testuser{i}@example.com'
            password = 'testpassword'
            User.objects.create_user(username=username, email=email, password=password)

        # Create chart types
        chart_types = [
            ChartType.objects.create(name='Bitcoin', symbol='BTC'),
            ChartType.objects.create(name='Ethereum', symbol='ETH'),
            ChartType.objects.create(name='Litecoin', symbol='LTC')
        ]

        # Create test candles for each chart type
        for chart_type in chart_types:
            for i in range(50):
                time = timezone.now() - timezone.timedelta(hours=i)
                open_price = random.uniform(30000, 40000)
                close_price = random.uniform(30000, 40000)
                min_price = min(open_price, close_price) - random.uniform(0, 1000)
                max_price = max(open_price, close_price) + random.uniform(0, 1000)
                Candle.objects.create(
                    chart_type=chart_type,
                    time=time,
                    open_price=open_price,
                    close_price=close_price,
                    min_price=min_price,
                    max_price=max_price
                )

        # Create test bets
        users = User.objects.all()
        for user in users:
            for _ in range(10):
                amount = Decimal(random.uniform(10, 100)).quantize(Decimal('0.01'))
                prediction = random.choice(['UP', 'DOWN'])
                result = random.choice(['WIN', 'LOSS', 'PENDING'])
                created_at = timezone.now() - timezone.timedelta(days=random.randint(0, 30))
                chart_type = random.choice(chart_types)
                Bet.objects.create(
                    user=user,
                    chart_type=chart_type,
                    amount=amount,
                    prediction=prediction,
                    result=result,
                    created_at=created_at
                )

        self.stdout.write(self.style.SUCCESS('Successfully populated the database with test data'))