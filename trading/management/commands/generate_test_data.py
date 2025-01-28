from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from decimal import Decimal
import random
from ...models import ChartType, Bet, PriceStamp, UserProfile
from datetime import timedelta

class Command(BaseCommand):
    help = 'Generates test data for betting system'

    def handle(self, *args, **options):
        # Create test chart type if not exists
        chart_type, created = ChartType.objects.get_or_create(
            name='Bitcoin/US Dollar',
            symbol='BTC-USD'
        )
        self.stdout.write(self.style.SUCCESS(f'{"Created" if created else "Found"} chart type: {chart_type.symbol}'))

        # Create test user if not exists
        username = 'test_user'
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': 'test@example.com',
                'password': 'testpass123'
            }
        )
        if created:
            user.set_password('testpass123')
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Created test user: {username}'))
        
        # Set user balance
        user.userprofile.balance = Decimal('10000.00')
        user.userprofile.save()
        self.stdout.write(self.style.SUCCESS(f'Set balance for {username} to 10000.00'))

        # Create some price stamps
        current_price = Decimal('50000.00')
        for _ in range(10):
            fluctuation = Decimal(str(random.uniform(0.95, 1.05)))
            current_price *= fluctuation
            PriceStamp.objects.create(
                chart_type=chart_type,
                price=current_price,
                time=timezone.now() - timedelta(seconds=random.randint(0, 300))
            )
        self.stdout.write(self.style.SUCCESS('Created 10 price stamps'))

        # Create some pending bets
        amounts = [100, 200, 500, 1000]
        directions = ['UP', 'DOWN']
        timeframes = [1, 2, 3]  # minutes

        # Create 5 bets that will expire soon
        for _ in range(5):
            amount = Decimal(str(random.choice(amounts)))
            direction = random.choice(directions)
            timeframe = random.choice(timeframes)
            
            # Create bet that will expire in 10-30 seconds
            expires_in = random.randint(10, 30)
            
            bet = Bet.objects.create(
                user=user,
                chart_type=chart_type,
                amount=amount,
                direction=direction,
                entry_price=current_price,
                timeframe=timeframe,
                expires_at=timezone.now() + timedelta(seconds=expires_in)
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Created bet {bet.id}: {direction} {amount} expires in {expires_in} seconds'
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'''
                Test data generation complete:
                - User: {username} (password: testpass123)
                - Balance: {user.userprofile.balance}
                - Chart: {chart_type.symbol}
                - Created 10 price stamps
                - Created 5 pending bets
                '''
            )
        )