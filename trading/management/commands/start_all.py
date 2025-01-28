from django.core.management.base import BaseCommand
import subprocess
import os
import signal
import sys
import time

class Command(BaseCommand):
    help = 'Starts Django server, Celery worker, and Celery beat'

    def handle(self, *args, **options):
        processes = []
        
        try:
            # Start Django server
            django = subprocess.Popen([
                'python', 'manage.py', 'runserver'
            ])
            processes.append(django)
            self.stdout.write('Started Django server')
            
            # Start Celery worker
            worker = subprocess.Popen([
                'celery', '-A', 'crypto_simulation', 'worker', '-l', 'info'
            ])
            processes.append(worker)
            self.stdout.write('Started Celery worker')
            
            # Start Celery beat
            beat = subprocess.Popen([
                'celery', '-A', 'crypto_simulation', 'beat', '-l', 'info'
            ])
            processes.append(beat)
            self.stdout.write('Started Celery beat')
            
            # Keep the command running
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            for process in processes:
                os.kill(process.pid, signal.SIGTERM)
            sys.exit(0)