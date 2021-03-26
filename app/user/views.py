from django.shortcuts import render
from rest_framework import generics,authentication,permissions
from user.serializers import Serializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from user.serializers import UserSerializer, AuthTokenSerializer

class CreateUserView(generics.CreateAPIView):
    """" Create a new user in the system """
    serializer_class = UserSerializer

class CreateTokenView(ObtainAuthToken):
    """ Create new authentication token for user """
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

class ManageUserView(generics.RetrieveUpdateAPIView):
    """ Manage the authenticated user """
    serializer_class = UserSerializer
    authentication_classes=(authentication.TokenAuthentication)
    permissions_classes=(permissions.IsAuthenticated)

    def getObject(self):
        """ Retrieve and return authenticated user
         get auth. user and assign it to the request """
        return self.request.user