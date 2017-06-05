from django.forms import ModelForm
from .models import *


class EnvForm(ModelForm):
    class Meta:
        model = Environment
        fields = ['name', 'is_active']
