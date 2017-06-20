from .models import *
from rest_framework import serializers


class DBInstanceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DBInstance
        fields = ['host', 'sid', 'port', 'login', 'passwd', 'sys_user', 'sys_passwd', 'weight']


class WEBInstanceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = WEBInstance
        fields = ['host', 'port', 'target_server', 'login', 'passwd']


class STLNInstanceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = STLNInstance
        fields = fields = ['host', 'port', 'user', 'passwd']


class EnvironmentSerializer(serializers.HyperlinkedModelSerializer):
    dbinstances = DBInstanceSerializer(many=True, read_only=True)
    webinstances = WEBInstanceSerializer(many=True, read_only=True)
    stlninstances = STLNInstanceSerializer(many=True, read_only=True)

    class Meta:
        model = Environment
        fields = ('name', 'is_active', 'dbinstances', 'webinstances', 'stlninstances')
