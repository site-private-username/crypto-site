import time

def continuous_price_generation(self):
    DEFAULT_SYMBOL = 'BTC-USD'
    DEFAULT_NAME = 'Bitcoin/US Dollar'
    
    chart_type, created = ChartType.objects.get_or_create(
        name=DEFAULT_NAME,
        defaults={'symbol': DEFAULT_SYMBOL}
    )
    
    last_entry = PriceStamp.objects.filter(chart_type=chart_type).order_by('-time').first()
    current_price = last_entry.price if last_entry else Decimal('100.00000000')
    
    price_stamps = []  # Список для хранения PriceStamp
    
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
        
        async_to_sync(self.channel_layer.group_send)(
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
        
        # Добавляем новый PriceStamp в список
        price_stamps.append(stamp)
        
        # Если накопилось 5 PriceStamp, создаем свечу и очищаем список
        if len(price_stamps) == 5:
            self.create_candle_from_price_stamps(chart_type, price_stamps)
            price_stamps = []  # Очищаем список
        
        # Пауза 1 секунда
        time.sleep(1)

@transaction.atomic
def create_candle_from_price_stamps(self, chart_type, price_stamps):
    # Извлечение цен и времени
    prices = [price_stamp.price for price_stamp in price_stamps]
    times = [price_stamp.time for price_stamp in price_stamps]
    
    # Вычисление цен открытия, закрытия, минимальной и максимальной
    open_price = prices[-1]  # Первый PriceStamp из 5
    close_price = prices[0]  # Последний PriceStamp из 5
    min_price = min(prices)
    max_price = max(prices)
    
    # Создание свечи
    Candle.objects.create(
        chart_type=chart_type,
        time=times[-1],  # Время первого PriceStamp из 5
        open_price=open_price,
        close_price=close_price,
        min_price=min_price,
        max_price=max_price
    )
    
    
    self.stdout.write(self.style.SUCCESS(
        f"Created a new candle for {chart_type.symbol} with open: {open_price}, close: {close_price}, min: {min_price}, max: {max_price}"
    ))