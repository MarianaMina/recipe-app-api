from django.shortcuts import render
from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import isAuthenticated
from core.models import Tag
from recipe import serializers

class TagViewSet(viewsets.GenericViewSet,
                 mixins.ListModelMixin,
                 mixins.CreateModelMixin):
    """ manage tags in db """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (isAuthenticated,)
    queryset=Tag.objects.all()
    serializer_class=serializers.TagSerializer

    def get_queryset(self):
        """ return object for current authenticate user only """
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """ Create a new tag """
        serializer.save(user=self.request.user)
