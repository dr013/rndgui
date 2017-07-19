from django import forms
from .models import Release, Product


class ReleaseForm(forms.Form):
    def __init__(self, product, *args, **kwargs):
        super(ReleaseForm, self).__init__(*args, **kwargs)
        self.fields['release'] = forms.ChoiceField(
            choices=[(o.id, str(o)) for o in Release.objects.filter(product=product)]
        )
        self.fields['product'] = forms.IntegerField(initial=product.pk)
        self.fields['product'].widget = forms.HiddenInput()


class ProductForm(forms.ModelForm):
    # def __init__(self, *args, **kwargs):
    #     super(ProductForm, self).__init__(*args, **kwargs)
    #     lst_all = jira_project_list()
    #     lst_used = Product.objects.values_list('jira', flat=True)
    #     choose = [(x[0], "{name}".format(name=x[1], key=x[0])) for x in lst_all if x[0] not in lst_used]
    #     choose.insert(0, ('', '----'))
    #
    #     self.fields['jira'] = forms.ChoiceField(choices=choose, initial=self.initial['jira'])

    class Meta:
        model = Product
        fields = ['title', 'wiki_url', 'specification_repo', 'jira', 'inst', 'owner']
