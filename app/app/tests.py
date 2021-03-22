from django.test import TestCase

from app.calc import add, subtract

class CalcTests(TestCase):

    def test_add_numbers(self):
        self.assertEqual(add(3, 8), 11)

    def test_substract_numbers(self):
        self.assertEqual(subtract(8, 3), 5)
