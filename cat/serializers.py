from .models import *
from rest_framework import serializers


class TestEnvironmentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TestEnvironment
        fields = ('name', 'env', 'expire')
