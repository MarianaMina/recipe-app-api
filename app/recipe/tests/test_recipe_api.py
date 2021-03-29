from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status

""" for making our api requests """
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import RecipeSerializer

RECIPES_URL = reverse('recipe:recipe-list')

""" any additional parameter after user will be passed in dictionary params """
def sample_recipe(user, **params):
    """ create and return sample recipe """
    defaults = {
        'title':'Sample recipe',
        'time_minutes':10,
        'price':5.00
    }

    """ any parameter passed after user will be overriden using update """
    defaults.update(params)
    return Recipe.objects.create(user=user, **defaults)

class PublicRecipeApiTests(TestCase):
    """ test unauthenticated recipe Api access """

    def setUp(self):
        self.client = APICLient()

    def test_auth_required(self):
        """ test that authentication is required """
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateRecipeApiTests(TestCase):
    """ test unauthenticated recipe API access """

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@gmail.com',
            'testpass'
        )

    self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """ test retrieving a list of recipes """
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        se;f.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """ test retrieving recipes for user """
        user2 = get_user_model().objectss.create_user(
            'test@gmail.com',
            'password123'
        )
        sample_recipe(user=user2)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data),1)
        self.assertEqual(res.data, serializer.data)
