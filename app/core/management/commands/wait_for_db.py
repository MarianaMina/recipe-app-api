import time

from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """" django command to pause execution until db is available"""

    def handle(self, *args, **options):
        """ Handle the command """
        self.stdout.write('Waiting for db')
        db_conn=None
        while not db_conn:
            try:
                db_conn = connections['default']
            except OperationalError:
                self.stdout.write('db unavailable')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('Database available'))
