
from rest_framework.decorators import action
from rest_framework import status, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db import transaction
import decimal
from django.db.models import Sum
from django.utils import timezone
from .serializers import (
    UserSerializer, UserProfileSerializer, ChartTypeSerializer,
    CandleSerializer, BetSerializer, ManualControlSerializer, CompletedBetSerializer
)
from .models import Candle, Bet, UserProfile, ChartType, ManualControl, CompletedBet


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'register': reverse('register', request=request, format=format),
        'login': reverse('login', request=request, format=format),
        'profile': reverse('profile', request=request, format=format),
        'chart-types': reverse('chart-type-list', request=request, format=format),
        'candles': reverse('candle-list', request=request, format=format),
        'bets': reverse('bet-list', request=request, format=format),
        'manual-controls': reverse('manual-control-list', request=request, format=format),
    })




class RegisterView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            })
        return Response(
            {'error': 'Invalid credentials'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )

class ChartTypeViewSet(ModelViewSet):
    queryset = ChartType.objects.all()
    serializer_class = ChartTypeSerializer
    permission_classes = [permissions.IsAuthenticated]

class CandleViewSet(ModelViewSet):
    serializer_class = CandleSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        chart_type_id = self.request.query_params.get('chart_type')
        interval = self.request.query_params.get('interval', '5s')  # по умолчанию 5s

        if not chart_type_id:
            return Candle.objects.none()

        # базовая выборка по активу
        queryset = Candle.objects.filter(chart_type_id=chart_type_id).order_by('-time')

        if interval == '5s':
            return queryset[:30]  # обычный режим

        # поддерживаемые интервалы
        interval_map = {
            '10s': 10,
            '30s': 30,
            '1m': 60,
            '2m': 120,
            '5m': 300,
        }

        if interval not in interval_map:
            return queryset.none()  # неподдерживаемый

        base_interval = 5  # ты генерируешь свечи каждые 5 секунд
        target_interval = interval_map[interval]
        group_size = target_interval // base_interval

        raw_candles = list(queryset[:group_size * 30])
        raw_candles = list(reversed(raw_candles))

        aggregated = []
        for i in range(0, len(raw_candles), group_size):
            group = raw_candles[i:i+group_size]
            if len(group) < group_size:
                break

            candle = {
                'open_price': group[0].open_price,
                'close_price': group[-1].close_price,
                'min_price': min(c.min_price for c in group),
                'max_price': max(c.max_price for c in group),
                'time': group[-1].time,
                'chart_type': group[-1].chart_type.id,
            }
            aggregated.append(candle)

        # сериализуем как будто это обычные Candle
        return Candle.objects.none()  # "обманываем DRF", вернём вручную

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if queryset.model != Candle:  # агрегированные свечи
            return Response(queryset, status=status.HTTP_200_OK)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class BetViewSet(ModelViewSet):
    serializer_class = BetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Bet.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        with transaction.atomic():
            bet = serializer.save(user=self.request.user)
            self.request.user.userprofile.balance -= bet.amount
            self.request.user.userprofile.save()

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        bets = self.get_queryset()
        total_profit = bets.filter(result='WIN').aggregate(Sum('amount'))['amount__sum'] or 0
        total_loss = bets.filter(result='LOSS').aggregate(Sum('amount'))['amount__sum'] or 0
        
        return Response({
            'total_profit': total_profit,
            'total_loss': total_loss,
            'total_bets': bets.count(),
            'pending_bets': bets.filter(result='PENDING').count()
        })

class CompletedBetViewSet(ModelViewSet):
    serializer_class = CompletedBetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CompletedBet.objects.filter(user=self.request.user).order_by('-created_at')


class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user.userprofile)
        return Response(serializer.data)

class ManualControlViewSet(ModelViewSet):
    serializer_class = ManualControlSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        chart_type_id = self.request.query_params.get('chart_type')
        queryset = ManualControl.objects.all()
        if chart_type_id:
            queryset = queryset.filter(chart_type_id=chart_type_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save()


class BetViewSet(ModelViewSet):
    serializer_class = BetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        print(self.request.user, "PIZDA")
        return Bet.objects.filter(user=self.request.user).order_by('-created_at')

    
    @action(detail=False, methods=['post'])
    def place(self, request):
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            with transaction.atomic():
                user_profile = request.user.userprofile
                amount = serializer.validated_data['amount']

                # Проверяем баланс
                if user_profile.balance < amount:
                    return Response({
                        'error': 'Insufficient balance',
                        'detail': f'Your current balance ({user_profile.balance}) is less than the bet amount ({amount})'
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Создаем ставку
                bet = serializer.save()
                
                # Обновляем баланс пользователя
                user_profile.balance -= amount
                user_profile.save()

                # Получаем свежий сериализатор для ответа
                response_serializer = self.get_serializer(bet)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                'error': 'Failed to place bet',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        bets = self.get_queryset()
        total_profit = bets.filter(result='WIN').aggregate(Sum('amount'))['amount__sum'] or 0
        total_loss = bets.filter(result='LOSS').aggregate(Sum('amount'))['amount__sum'] or 0
        
        return Response({
            'total_profit': str(total_profit),
            'total_loss': str(total_loss),
            'total_bets': bets.count(),
            'pending_bets': bets.filter(result='PENDING').count()
        })