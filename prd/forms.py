from django import forms

from prd.models import Release


class ReleaseForm(forms.Form):
    def __init__(self, product, *args, **kwargs):
        super(ReleaseForm, self).__init__(*args, **kwargs)
        self.fields['release'] = forms.ChoiceField(
            choices=[(o.id, str(o)) for o in Release.objects.filter(product=product)]
        )
        self.fields['product'] = forms.IntegerField(initial=product.pk)
        self.fields['product'].widget = forms.HiddenInput()


class BuildRevisionForm(forms.Form):
    module = forms.CharField(label='Product module', max_length=20, disabled=True)
    revision = forms.CharField(label="Git revision", max_length=40)

