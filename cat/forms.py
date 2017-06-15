from django import forms
from .models import Release


class ReleaseForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(ReleaseForm, self).__init__(*args, **kwargs)
        self.fields['release'] = forms.ChoiceField(
            choices=[(o.id, str(o)) for o in Release.objects.all()]
        )
