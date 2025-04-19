echo "[+] Starting Django..."
python manage.py runserver 0.0.0.0:8000 &

echo "[+] Starting Celery worker..."
celery -A crypto_simulation worker --loglevel=info &

echo "[+] Starting Celery beat..."
celery -A crypto_simulation beat --loglevel=info &

echo "[+] Starting RabbitMQ listener..."
python manage.py start_rabbit_listener &


wait -n