from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta

class ChartType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    symbol = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name

class Candle(models.Model):
    chart_type = models.ForeignKey(ChartType, on_delete=models.CASCADE)
    time = models.DateTimeField()
    open_price = models.FloatField()
    close_price = models.FloatField()
    min_price = models.FloatField()
    max_price = models.FloatField()

    def __str__(self):
        return f"{self.chart_type.symbol} Candle at {self.time}"


class PriceStamp(models.Model):
    chart_type = models.ForeignKey(ChartType, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=20, decimal_places=8)
    time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.chart_type.symbol} - {self.price}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00)

    def __str__(self):
        return f"{self.user.username}'s profile"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

# models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Bet(models.Model):
    DIRECTION_CHOICES = [('UP', 'Up'), ('DOWN', 'Down')]
    RESULT_CHOICES = [('WIN', 'Win'), ('LOSS', 'Loss'), ('PENDING', 'Pending')]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chart_type = models.ForeignKey('ChartType', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    direction = models.CharField(max_length=4, choices=DIRECTION_CHOICES)
    entry_price = models.DecimalField(max_digits=20, decimal_places=8)
    timeframe = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    result = models.CharField(
        max_length=7, 
        choices=RESULT_CHOICES, 
        default='PENDING'
    )

    def __str__(self):
        return f"{self.user.username}'s {self.direction} bet of ${self.amount} on {self.chart_type.symbol}"

    def save(self, *args, **kwargs):
        if not self.expires_at:
            time_delta = timedelta(minutes=self.timeframe)
            future_time = timezone.now() + time_delta
            self.expires_at = future_time
        super().save(*args, **kwargs)

class CompletedBet(models.Model):
    RESULT_CHOICES = [('WIN', 'Win'), ('LOSS', 'Loss')]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chart_type = models.ForeignKey(ChartType, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    direction = models.CharField(max_length=4, choices=Bet.DIRECTION_CHOICES)
    entry_price = models.DecimalField(max_digits=20, decimal_places=8)
    closing_price = models.DecimalField(max_digits=20, decimal_places=8)
    result = models.CharField(max_length=4, choices=RESULT_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s {self.result} bet on {self.chart_type.symbol}"



class ManualControl(models.Model):
    chart_type = models.ForeignKey(ChartType, on_delete=models.CASCADE)
    time = models.DateTimeField(validators=[
        MinValueValidator(limit_value=timezone.now() - timezone.timedelta(days=1)),
        MaxValueValidator(limit_value=timezone.now() + timezone.timedelta(minutes=1))
    ])
    value = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-time']

    def __str__(self):
        return f"{self.chart_type.name} - {self.time}: {self.value}"