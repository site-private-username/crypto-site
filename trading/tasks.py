from celery import shared_task
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
from .models import Bet, PriceStamp
import logging

logger = logging.getLogger(__name__)

@shared_task
def process_bets():
    print("\n=== Starting bet processing... ===")
    now = timezone.now()
    
    # Get all pending bets that have expired
    pending_bets = Bet.objects.filter(
        result='PENDING',
        expires_at__lte=now
    ).select_related('user__userprofile', 'chart_type')
    
    print(f"Found {pending_bets.count()} pending bets to process")
    
    for bet in pending_bets:
        try:
            with transaction.atomic():
                # Get the latest price for the chart type
                latest_price = PriceStamp.objects.filter(
                    chart_type=bet.chart_type
                ).order_by('-time').first()
                
                if not latest_price:
                    print(f"No price found for bet {bet.id}, skipping...")
                    continue
                
                closing_price = latest_price.price
                entry_price = bet.entry_price
                
                # Determine if bet is won or lost
                if bet.direction == 'UP':
                    is_win = closing_price > entry_price
                else:  # direction is DOWN
                    is_win = closing_price < entry_price
                
                # Update bet result
                bet.result = 'WIN' if is_win else 'LOSS'
                
                # Calculate and update user balance
                user_profile = bet.user.userprofile
                if is_win:
                    # Win gives 2x the bet amount (original bet + profit)
                    profit = bet.amount * Decimal('2.0')
                    user_profile.balance += profit
                    print(f"Bet {bet.id} WON: User {bet.user.username} wins {profit}. "
                          f"Entry: {entry_price}, Close: {closing_price}")
                else:
                    # Loss has already been deducted when placing the bet
                    print(f"Bet {bet.id} LOST: User {bet.user.username} loses {bet.amount}. "
                          f"Entry: {entry_price}, Close: {closing_price}")
                
                user_profile.save()
                bet.save()
                
                print(f"Processed bet {bet.id} for user {bet.user.username}")
                print(f"New balance for {bet.user.username}: {user_profile.balance}")
                
        except Exception as e:
            logger.error(f"Error processing bet {bet.id}: {str(e)}")
            print(f"Error processing bet {bet.id}: {str(e)}")
    
    print("=== Bet processing completed ===\n")