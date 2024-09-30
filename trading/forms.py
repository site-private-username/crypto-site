from django import forms
from .models import Bet, Candle, ChartType, ManualControl
from django.utils import timezone
from datetime import timedelta

class BetForm(forms.ModelForm):
    chart_type = forms.ModelChoiceField(queryset=ChartType.objects.all(), widget=forms.HiddenInput())

    class Meta:
        model = Bet
        fields = ['amount', 'prediction', 'chart_type']

class CandleForm(forms.ModelForm):
    class Meta:
        model = Candle
        fields = ['time', 'open_price', 'close_price', 'min_price', 'max_price']
        widgets = {
            'time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    
    def clean_time(self):
        time = self.cleaned_data['time']
        if time <= timezone.now() + timedelta(minutes=1):
            raise forms.ValidationError("Time must be at least 1 minute in the future.")
        return time

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['time'].input_formats = ['%Y-%m-%dT%H:%M']

class ManualControlForm(forms.ModelForm):
    class Meta:
        model = ManualControl
        fields = ['time', 'value']
        widgets = {
            'time': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control',
                    'min': (timezone.now() - timezone.timedelta(days=1)).strftime('%Y-%m-%dT%H:%M'),
                    'max': (timezone.now() + timezone.timedelta(minutes=1)).strftime('%Y-%m-%dT%H:%M'),
                }
            ),
            'value': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['time'].input_formats = ['%Y-%m-%dT%H:%M']

    def clean_time(self):
        time = self.cleaned_data.get('time')
        if time:
            min_time = timezone.now() - timezone.timedelta(days=1)
            max_time = timezone.now() + timezone.timedelta(minutes=1)
            if time < min_time or time > max_time:
                raise forms.ValidationError("Time must be within the last 24 hours or up to 1 minute in the future.")
        return time