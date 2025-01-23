from django.core.management.base import BaseCommand
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from trading.models import PriceStamp, ChartType
from decimal import Decimal, ROUND_HALF_UP
import random
import time
class Command(BaseCommand):
    help = "Generates and broadcasts a single price or checks channel content"

    def add_arguments(self, parser):
        parser.add_argument(
            '--check-channel',
            action='store_true',
            help='Check content of prices channel'
        )
        parser.add_argument(
            '--generate-once',
            action='store_true',
            help='Generate and send single price update'
        )

    def handle(self, *args, **options):
        channel_layer = get_channel_layer()

        if options['check_channel']:
            # Get channel content (for debugging)
            groups = channel_layer.groups if hasattr(channel_layer, 'groups') else {}
            self.stdout.write("Current channel groups:")
            self.stdout.write(str(groups))
            
            if "prices" in groups:
                self.stdout.write("\nChannels in 'prices' group:")
                self.stdout.write(str(groups["prices"]))
            else:
                self.stdout.write("\nNo 'prices' group found")

        elif options['generate_once']:
            # Generate single price update
            DEFAULT_SYMBOL = 'BTC-USD'
            DEFAULT_NAME = 'Bitcoin/US Dollar'
            
            chart_type, created = ChartType.objects.get_or_create(
                name=DEFAULT_NAME,
                defaults={'symbol': DEFAULT_SYMBOL}
            )
            
            last_entry = PriceStamp.objects.filter(chart_type=chart_type).order_by('-time').first()
            current_price = last_entry.price if last_entry else Decimal('100.00000000')
            
            # Generate new price
            fluctuation = Decimal(str(random.uniform(0.95, 1.05)))
            new_price = (current_price * fluctuation).quantize(
                Decimal('0.00000000'),
                rounding=ROUND_HALF_UP
            )
            
            # Create record
            stamp = PriceStamp.objects.create(
                chart_type=chart_type,
                price=new_price
            )
            
            # Send update
            async_to_sync(channel_layer.group_send)(
                "prices",
                {
                    "type": "price_update",
                    "data": {
                        "price": str(new_price),
                        "time": stamp.time.isoformat(),
                        "symbol": chart_type.symbol
                    }
                }
            )
            
            self.stdout.write(self.style.SUCCESS(
                f"Generated and sent price: {new_price} for {chart_type.symbol}"
            ))
        
        else:
            # Original continuous generation logic
            try:
                DEFAULT_SYMBOL = 'BTC-USD'
                DEFAULT_NAME = 'Bitcoin/US Dollar'
                
                chart_type, created = ChartType.objects.get_or_create(
                    name=DEFAULT_NAME,
                    defaults={'symbol': DEFAULT_SYMBOL}
                )
                
                last_entry = PriceStamp.objects.filter(chart_type=chart_type).order_by('-time').first()
                current_price = last_entry.price if last_entry else Decimal('100.00000000')
                
                while True:
                    fluctuation = Decimal(str(random.uniform(0.95, 1.05)))
                    new_price = (current_price * fluctuation).quantize(
                        Decimal('0.00000000'),
                        rounding=ROUND_HALF_UP
                    )
                    
                    stamp = PriceStamp.objects.create(
                        chart_type=chart_type,
                        price=new_price
                    )
                    
                    async_to_sync(channel_layer.group_send)(
                        "prices",
                        {
                            "type": "price_update",
                            "data": {
                                "price": str(new_price),
                                "time": stamp.time.isoformat(),
                                "symbol": chart_type.symbol
                            }
                        }
                    )
                    current_price = new_price
                    time.sleep(1)
                    
            except KeyboardInterrupt:
                self.stdout.write("Stopped price generation")