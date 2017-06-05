from django.forms import ModelForm
from django.contrib.contenttypes.forms import generic_inlineformset_factory
from .models import *


class EnvForm(ModelForm):
    class Meta:
        model = Environment
        fields = ['name', 'is_active']

DBInstanceFormSet = generic_inlineformset_factory(DBInstance, extra=1, can_delete=False)
WEBInstanceFormSet = generic_inlineformset_factory(WEBInstance, extra=1, can_delete=False)
STLNInstanceFormSet = generic_inlineformset_factory(STLNInstance, extra=1, can_delete=False)
