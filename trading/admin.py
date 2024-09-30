from django.contrib import admin
from .models import Candle, UserProfile, Bet

@admin.register(Candle)
class CandleAdmin(admin.ModelAdmin):
    list_display = ('time', 'open_price', 'close_price', 'min_price', 'max_price')
    list_filter = ('time',)
    search_fields = ('time',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance')
    search_fields = ('user__username',)

@admin.register(Bet)
class BetAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'prediction', 'created_at', 'result')
    list_filter = ('prediction', 'result', 'created_at')
    search_fields = ('user__username',)