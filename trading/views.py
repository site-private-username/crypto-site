from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Sum

from .models import Candle, Bet, UserProfile, ChartType
from django.db import transaction
import json
from django.utils import timezone
from .forms import BetForm, CandleForm


def home(request):
    return render(request, 'trading/home.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                UserProfile.objects.get_or_create(user=user)  # Use get_or_create instead of create
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'trading/register.html', {'form': form})

@login_required
def dashboard(request):
    chart_types = ChartType.objects.all()
    selected_chart_type = request.GET.get('chart_type')
    
    if selected_chart_type:
        chart_type = ChartType.objects.get(id=selected_chart_type)
    else:
        chart_type = chart_types.first()
    
    candles = Candle.objects.filter(chart_type=chart_type).order_by('-time')[:30]
    
    # Подготовка данных для графика
    chart_data = {
        'labels': [],
        'open': [],
        'close': [],
        'high': [],
        'low': []
    }
    
    for candle in reversed(candles):
        chart_data['labels'].append(candle.time.isoformat())
        chart_data['open'].append(float(candle.open_price))
        chart_data['close'].append(float(candle.close_price))
        chart_data['high'].append(float(candle.max_price))
        chart_data['low'].append(float(candle.min_price))
    
    if request.method == 'POST':
        if 'place_bet' in request.POST:
            bet_form = BetForm(request.POST)
            if bet_form.is_valid():
                bet = bet_form.save(commit=False)
                bet.user = request.user
                bet.chart_type = chart_type
                if bet.amount <= request.user.userprofile.balance:
                    request.user.userprofile.balance -= bet.amount
                    request.user.userprofile.save()
                    bet.save()
                    return redirect('dashboard')
    else:
        bet_form = BetForm(initial={'chart_type': chart_type.id})
    
    # Получение последних ставок пользователя
    user_bets = Bet.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    context = {
        'chart_types': chart_types,
        'selected_chart_type': chart_type,
        'candles': candles,
        'bet_form': bet_form,
        'chart_data': json.dumps(chart_data),
        'current_price': candles.first().close_price if candles else 0,
        'user_bets': user_bets,
    }
    return render(request, 'trading/dashboard.html', context)

@login_required
def profile(request):
    user_profile = request.user.userprofile
    bets = Bet.objects.filter(user=request.user).order_by('-created_at')[:5]
    context = {
        'user_profile': user_profile,
        'recent_bets': bets,
    }
    return render(request, 'trading/profile.html', context)

@login_required
def trade_history(request):
    bets = Bet.objects.filter(user=request.user).order_by('-created_at')
    total_profit = bets.filter(result='WIN').aggregate(Sum('amount'))['amount__sum'] or 0
    total_loss = bets.filter(result='LOSS').aggregate(Sum('amount'))['amount__sum'] or 0
    context = {
        'bets': bets,
        'total_profit': total_profit,
        'total_loss': total_loss,
    }
    return render(request, 'trading/trade_history.html', context)


@login_required
def admin_panel(request):
    chart_types = ChartType.objects.all()
    selected_chart_type = request.GET.get('chart_type')
    
    if selected_chart_type:
        chart_type = ChartType.objects.get(id=selected_chart_type)
    else:
        chart_type = chart_types.first()
    
    candles = Candle.objects.filter(chart_type=chart_type).order_by('-time')[:30]
    last_candle = candles.first()  # Get the most recent candle
    
    # Подготовка данных для графика
    chart_data = {
        'labels': [],
        'open': [],
        'close': [],
        'high': [],
        'low': []
    }
    
    for candle in reversed(candles):
        chart_data['labels'].append(candle.time.isoformat())
        chart_data['open'].append(float(candle.open_price))
        chart_data['close'].append(float(candle.close_price))
        chart_data['high'].append(float(candle.max_price))
        chart_data['low'].append(float(candle.min_price))
    
    if request.method == 'POST':
        if 'add_candle' in request.POST:
            candle_form = CandleForm(request.POST)
            if candle_form.is_valid():
                candle = candle_form.save(commit=False)
                candle.chart_type = chart_type
                candle.save()
                return redirect('admin_panel')
    else:
        bet_form = BetForm()
        candle_form = CandleForm()
    
    context = {
        'chart_types': chart_types,
        'selected_chart_type': chart_type,
        'candles': candles,
        'bet_form': bet_form,
        'candle_form': candle_form,
        'chart_data': json.dumps(chart_data),
        'current_price': last_candle.close_price if last_candle else 0,
        'last_candle': last_candle,  # Add the last candle to the context
    }
    return render(request, 'trading/admin_panel.html', context)