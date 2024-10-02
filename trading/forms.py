from django import forms
from .models import Bet, Candle, ChartType, ManualControl
from django.utils import timezone
from datetime import timedelta

class BetForm(forms.ModelForm):
    chart_type = forms.ModelChoiceField(queryset=ChartType.objects.all(), widget=forms.HiddenInput())
    duration = forms.IntegerField(
        min_value=1,
        max_value=60,
        initial=5,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Duration in minutes'})
    )
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Bet amount'})
    )

    class Meta:
        model = Bet
        fields = ['amount', 'duration', 'chart_type']

    def clean_duration(self):
        duration = self.cleaned_data['duration']
        return timezone.now() + timezone.timedelta(minutes=duration)

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.duration = self.cleaned_data['duration']
        if commit:
            instance.save()
        return instance
        
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