echo "[+] Starting Daphne (ASGI server for Django)..."
daphne -b 0.0.0.0 -p 8000 crypto_simulation.asgi:application &

echo "[+] Starting Celery worker..."
celery -A crypto_simulation worker --loglevel=info &

echo "[+] Starting Celery beat..."
celery -A crypto_simulation beat --loglevel=info &

echo "[+] Starting RabbitMQ listener..."
python manage.py start_rabbit_listener &

wait -n
