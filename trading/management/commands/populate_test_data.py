from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from trading.models import Candle, Bet, ChartType, UserProfile, ManualControl
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
            user, _ = User.objects.get_or_create(username=username, email=email)
            user.set_password(password)
            user.save()
            UserProfile.objects.get_or_create(user=user)

        # Create chart types
        chart_types = []
        for name, symbol in [('Bitcoin', 'BTC'), ('Ethereum', 'ETH'), ('Litecoin', 'LTC')]:
            chart_type, _ = ChartType.objects.get_or_create(name=name, symbol=symbol)
            chart_types.append(chart_type)

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
                direction = random.choice(['UP', 'DOWN'])
                entry_price = random.uniform(30000, 40000)
                timeframe = random.choice(['1m', '5m', '15m', '30m', '1h'])
                created_at = timezone.now() - timezone.timedelta(days=random.randint(0, 30))
                chart_type = random.choice(chart_types)
                result = random.choice(['WIN', 'LOSS', 'PENDING'])
                Bet.objects.create(
                    user=user,
                    chart_type=chart_type,
                    amount=amount,
                    direction=direction,
                    entry_price=entry_price,
                    timeframe=timeframe,
                    created_at=created_at,
                    result=result
                )

        # Create test manual controls
        for chart_type in chart_types:
            for i in range(10):
                time = timezone.now() - timezone.timedelta(hours=i)
                value = random.randint(30000, 40000)
                ManualControl.objects.create(
                    chart_type=chart_type,
                    time=time,
                    value=value
                )

        self.stdout.write(self.style.SUCCESS('Successfully populated the database with test data'))