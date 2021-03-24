from unittest import patch
from django.core.management import call_command
from django.db.utils import OperationalError

from django.test import TestCase

class CommandTests(TestCase):
    def test_wait_for_db_ready(self):
        """ test waiting for db when db is available """
        with patch('django.db.utils.ConnectionHandler.__getItem__') as gi:
            gi.return_value=True
            call_command('wait_for_db')
            self.assertEqual(gi.call_count,1)

    @patch('time_sleep', return_value=True)
    def test_wait_for_db(self):
        """ test waiting for db """
        with patch('django.db.utils.ConnectionHandler.__getItem__') as gi:
            gi.side_effect=[OperationalError]*5+[True]
            call_command('wait_for_db')
            self.assertEqual(gi.call_count,6)
