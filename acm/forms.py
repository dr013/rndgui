from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(label='BPC Login', max_length=20, required=True)
    password = forms.CharField(label='BPC Password', required=True, widget=forms.PasswordInput)
    is_ldap = forms.BooleanField(initial=True, required=False)
