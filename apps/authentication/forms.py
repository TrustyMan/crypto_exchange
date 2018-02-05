from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _

from .users import UserModel
from .users import UsernameField

User = UserModel()


class RegistrationForm(UserCreationForm):
    """
    Form for registering a new user account.

    """
    required_css_class = 'required'
    email = forms.EmailField(label=_("E-mail"))

    class Meta:
        model = User
        fields = (UsernameField(), "email", "first_name", "last_name")
    
    def clean_username(self):
        username = self.cleaned_data.get('username', '').lower()
        if User.objects.filter(**{UsernameField(): username}).exists():
            raise forms.ValidationError(_('A user with that username already exists.'))

        return username

    def clean_email(self):
        """
        Validate that the supplied email address is unique for the
        site.

        """
        if User.objects.filter(email__iexact=self.cleaned_data['email']):
            raise forms.ValidationError(_("This email address is already in use. Please supply a different email address."))
        return self.cleaned_data['email']



class ResendActivationForm(forms.Form):
    required_css_class = 'required'
    email = forms.EmailField(label=_("E-mail"))