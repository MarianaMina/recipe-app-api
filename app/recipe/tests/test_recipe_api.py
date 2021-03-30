import tempfile
import os

from PIL import Image

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status

""" for making our api requests """
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse('recipe:recipe-list')

def image_upload_url(recipe_id):
    """ return URL for recipe image upload """
    return reverse('recipe:recipe-upload-image', args=[recipe_id])

def detail_url(recipe_id):
    """ return recipe detail URL"""
    """ test single argument in the URL """
    return reverse("recipe:recipe-detail", args=[recipe_id])

def sample_tag(user, name='Main course'):
    """ create and return a sample tag"""
    return Tag.objects.create(user=user, name=name)

def sample_ingredient(user, name='Cinammon'):
    """ create and return a sample ingredient """
    return Ingredient.objects.create(user=user, name=name)

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

    def test_view_recipe_detail(self):
        """ test viewing a recipe detail """
        recipe = sample_recipe(user=self.user)
        # way adding item many to many
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        # return url for specific detail
        url = detail_url(recipe.id)
        # retrieve url
        res = self.client.get(url)

        # serialize single recipe
        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_recipe(self):
        """ test creating recipe """
        payload = {
            'title': 'Chocolate cheesecake',
            'time_minutes': 30,
            'price':5.00
        }
        res = self.client.post(RECIPES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # get id of created object
        recipe = Recipe.objects.get(id=res.data['id'])

        # loop through each key in dictionary
        for key in payload.keys():
            self.assertEqual(payload[key],getattr(recipe,key))

    def test_create_recipe_with_tags(self):
        """ test creating a recipe with tags """
        tag1 = sample_tag(user=self.user, name='Vegan')
        tag2 = sample_tag(user=self.user, name='Dessert')
        payload = {
            'title':'Avocado line cheesecake',
            'tags': [tag1.id, tag2.id],
            'time_minutes': 60,
            'price':20.00
        }
        res = self.client.post(RECIPES_URL, payload)
        recipe = Recipe.objects.get(id=res.data['id'])
        tags=recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """ Test creating recipe with ingredients"""
        ingredient1 = sample_ingredient(user=self.user, name='Prawns')
        ingredient2 = sample_ingredient(user=self.user,name='Ginger')
        payload = {
            'title' : 'Thai prawn red curry',
            'ingredients': [ingredient1.id,ingredient2.id],
            'time_minutes':20,
            'price':7.00
        }
        res = self.client.post(RECIPES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(),2)
        self.assertIn(ingredient1,ingredients)
        self.assertIn(ingredient2,ingredients)

    def test_partial_update_recipe(self):
        """ test updating a recipe with patch """
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user,name='Curry')

        payload = {'title': 'chicken tikka', 'tags':[new_tag.id]}
        url = detail_url(recipe.id)
        self.client.patch(url,payload)

        # refresh recipe details from our db
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        tags=recipe.tags.all()
        self.assertEqual(len(tags),1)
        self.assertIn(new_tag, tags)

    def test_full_update_recipe(self):
        """ Test updating a recipe with put -- updates whole if we ommit a field will not exist """
        recipe = sample_recipe(user=self.name)
        recipe.tags.add(sample_tag(user=self.user))
        payload = {
            'title':'Spaghetti carbonara',
            'time_minutes':25,
            'price':5.00
        }
        url = detail_url(recipe.id)
        self.client.put(url,payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        self.assertEqual(recipe.price, payload['price'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags),0)

class RecipeImageUploadTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@gmail.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)
        self.recipe = sample_recipe(user=self.user)

    def tearDown(self):
        """ delete images after test """
        self.recipe.image.delete()

    def test_upload_image_to_recipe(self):
        """ test uploading image to recipe """
        url = image_upload_url(self.recipe.id)
        # create temp file with ext jpg, with image and upload it through API
        # after exit will automatically remove it
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB',(10, 10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            res = self.client.post(url, {'image':ntf}, format='multipart')
        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """ test uploading an invalid image """
        url = image_upload_url(self.recipe.id)
        res = self.client.post(url, {'image': 'notimage'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_recipes_by_tags(self):
        """ test returning recipes with specific tags """
        recipe1 = sample_recipe(user=self.user, title='thai vegetable curry')
        recipe2 = sample_recipe(user=self.user, title='aubergine with tahini')
        tag1=sample_tag(user=self.user, name='Vegan')
        tag2=sample_tag(user=self.user, name='Vegetarian')
        recipe1.tags.add(tag1)
        recipe2.tags.add(tag2)
        recipe3=sample_recipe(user=self.user, title='fish and chips')

        res=self.client.get(
            RECIPES_URL,
            # pass parameters
            {'tags':f'{tag1.id}, {tag2.id}'}
        )

        serializer1 = RecipeSerializer(recip1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_recipes_by_ingredients(self):
        """ test returning recipes with specific ingredients """
        recipe1 = sample_recipe(user=self.user, title='Posh beans on toast')
        recipe2 = sample_recipe(user=self.user, title='Chicken cacciatore')
        ingredient1 = sample_ingredient(user=self.user, name='Feta cheese')
        ingredient2 = sample_ingredient(user=self.user, name='Chicken')
        recipe1.ingredients.add(ingredient1)
        recipe2.ingredients.add(ingredient2)
        recipe3 = sample_recipe(user=self.user, title='steak and mushrooms')

        res = self.client.get(
            RECIPES_URL,
            {'ingredients':f'{ingredient1.id},{ingredient2.id}'}
        )

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)



