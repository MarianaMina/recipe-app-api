from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models


def sample_user(email='test@gmail.com', password='testpass'):
    """ Create sample user """
    return get_user_model().objects.create_user(email, password)

class ModelTests(TestCase):
    def test_create_user_with_email_successful(self):
        """ test creating new user with a email successful """
        email = 'test@gmail.com'
        password = 'Testpass@123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """ test the email for a new user is normalized """
        email = "test@gmail.com"
        user = get_user_model().objects.create_user(email, 'test123')
        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """ test creating user with no email raises error """
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def test_create_new_superuser(self):
        """ test creates new superuser """
        user = get_user_model().objects.create_superuser(
            'test@gmail.com',
            'test123'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """ Test the tag string representation """
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='vegan'
        )
        self.assertEqual(str(tag),tag.name)

    def test_ingredient_str(self):
        """ Test the ingredient test representation """
        ingredient = models.Ingredient.objects.create(
            user = sample_user(),
            name='Cucumber'
        )

        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        """ Test recipe string representation """
        recipe = models.Recipe.objects.create(
            user = sample_user(),
            title='Steak and mushroom sauce',
            time_minutes=5,
            price=5.00
        )

    # generate unique id
    @patch('uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """ test image is saved in the correct location """
        uuid = 'test-uuid'
        # when call uuid4 function will replace with the below instead
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None,'myimage.jpg')

        exp_path = f'upload/recipe/{uuid}.jpg'

        self.assertEqual(file_path, exp_path)