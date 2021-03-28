from rest_framework import serializer_class
from core.models import Tag

class TagSerializer(serializer.ModelSerializer):
    """" Serializer for tag object """
    class Meta:
        model = Tag
        fields=('id','name')
        read_only_fields=('id',)