from django.contrib import admin
from .models import Candle, UserProfile, Bet, ChartType

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
    list_display = ('user', 'amount', 'direction', 'created_at', 'result')  # Changed 'prediction' to 'direction'
    list_filter = ('direction', 'result', 'created_at')  # Changed 'prediction' to 'direction'
    search_fields = ('user__username',)

@admin.register(ChartType)
class ChartAdmin(admin.ModelAdmin):
    list_display = ('name', 'symbol')
    search_fields = ('name',)