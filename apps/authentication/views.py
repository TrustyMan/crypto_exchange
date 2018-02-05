import random

from django.conf import settings
from django.shortcuts import redirect, render_to_response, render
from django.utils.decorators import method_decorator
from django.utils.module_loading import import_string
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic.base import TemplateView, View
from django.views.generic.edit import FormView
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.utils import six
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.shortcuts import get_object_or_404
from django.template import RequestContext

from apps.authentication.forms import ResendActivationForm, RegistrationForm
from apps.authentication.models import User


class RegistrationView(FormView):
    """
    User registration view.

    """
    form_class = RegistrationForm
    success_url = None
    template_name = 'authentication/signup.html'

    def form_valid(self, form):
        new_user = form.save()
        if new_user:
            new_user.is_active = False
            new_user.save()
            token = account_activation_token.make_token(new_user)
            confirm_url = self.request.scheme+"://"+self.request.META['HTTP_HOST']+\
            reverse('email_confirmation', kwargs={'uidb64': urlsafe_base64_encode(force_bytes(new_user.pk)).decode("utf-8"),'token': token})
            html_message = "Click the link to verify email address <a href='"+confirm_url+"'>Verify</a>"
            try:
                send_mail('Confrim Registration',
                    '',
                    settings.DEFAULT_FROM_EMAIL,
                    [new_user.email],
                    html_message = html_message,
                    fail_silently=False
                    )
            except:
                pass
            return render_to_response('authentication/success.html')
        else:
            return redirect(reverse('signup'))



class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    """ Overriding default Password reset token generator for email confirmation"""
    def _make_hash_value(self, user, timestamp):
        return (six.text_type(user.pk) + six.text_type(timestamp)) +  six.text_type(user.is_active)

account_activation_token = AccountActivationTokenGenerator()

class ConfirmSignUpView(View):
    """ Confirming sign up via link provided in email"""
    template_name = 'authentication/email_verified.html'

    def get(self, request, *args, **kwargs):
        """ Ckecking token and conforming account activation"""
        pk = force_text(urlsafe_base64_decode( kwargs.get('uidb64')))
        token = kwargs.get('token')
        user = get_object_or_404(User, pk=pk)
        if account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            return render(request, self.template_name, {'error': False})
        else:
            return render(request,self.template_name, {'error': True})



