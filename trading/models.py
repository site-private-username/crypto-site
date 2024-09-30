from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

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

class Bet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chart_type = models.ForeignKey(ChartType, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    prediction = models.CharField(max_length=10, choices=[('UP', 'Up'), ('DOWN', 'Down')])
    created_at = models.DateTimeField(auto_now_add=True)
    result = models.CharField(max_length=10, choices=[('WIN', 'Win'), ('LOSS', 'Loss'), ('PENDING', 'Pending')], default='PENDING')

    def __str__(self):
        return f"{self.user.username}'s bet of ${self.amount} on {self.chart_type.symbol} {self.prediction}"