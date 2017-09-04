from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

class RegisterForm(forms.Form):
    username = forms.fields.CharField(required=True, max_length=20 )
    email = forms.fields.EmailField(required=True, )
    pwd1 = forms.fields.CharField(required=True, min_length=8, label="Password", widget=forms.PasswordInput)
    pwd2 = forms.fields.CharField(required=True, min_length=8, label="Confirm Password", widget=forms.PasswordInput)

    def clean_pwd2(self):
        pwd1 = self.cleaned_data.get("pwd1")
        pwd2 = self.cleaned_data.get("pwd2")
        if pwd1 != pwd2:
            raise forms.ValidationError("different.")
        return pwd2

    def clean_username(self):
        un = self.cleaned_data.get('username')
        try:
            user = User.objects.filter(username=un)[0:1].get()
        except ObjectDoesNotExist:
            user = None
        if user is not None:
            raise forms.ValidationError('用户名已存在')
        return un

class LoginForm(forms.Form):
    username = forms.CharField(required=True, max_length=20, strip=True)
    password = forms.CharField(widget=forms.PasswordInput)
