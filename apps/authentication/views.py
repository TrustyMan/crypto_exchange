import random

from twilio.rest import Client

from django.utils import six
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.template import RequestContext
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.module_loading import import_string
from django.utils.encoding import force_bytes, force_text
from django.shortcuts import redirect, render_to_response, render
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.views.decorators.debug import sensitive_post_parameters
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic import TemplateView, View, FormView, UpdateView, DetailView


from apps.authentication.models import User, UserProfile
from apps.authentication.forms import ResendActivationForm, RegistrationForm, UserProfileForm

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
            confirm_url = self.request.scheme+"://"+self.request.META['HTTP_HOST']+".io"+\
            reverse('auth:email_confirmation', kwargs={'uidb64': urlsafe_base64_encode(force_bytes(new_user.pk)).decode("utf-8"),'token': token})
            html_message = "Click the link to verify email address <a href='"+confirm_url+"'>Verify</a>"
            try:
                send_mail('Confrim Registration',
                          '',
                          settings.DEFAULT_FROM_EMAIL,
                          [new_user.email],
                          html_message=html_message,
                          fail_silently=False
                          )
            except:
                pass
            return render_to_response('authentication/success.html')
        else:
            return redirect(reverse('signup'))

class TwoFactorAuthenticationView(TemplateView):
    """
    Enabling 2FA.
    This will set a otp-verified in session when user enters the correct otp.
    """
    template_name = "authentication/otp.html"

    def dispatch(self,request,*args,**kwargs):
        if not self.request.user.phone_number and not self.request.method == "POST":
            return render(self.request,"authentication/mobile.html")
        elif self.request.user.phone_number and not self.request.method == "POST":
            pin =  self._get_pin()
            self.request.session['otp'] = pin
            self.send_otp(pin,self.request.user.phone_number)
            return render(self.request,"authentication/otp.html")
        else:
            return self.post(self,request,args,kwargs)

    def post(self,request,*args,**kwargs):
        number = self.request.POST.get('phone_number')
        if number:
            User.objects.filter(id = self.request.user.id).update(phone_number=number)
            pin =  self._get_pin()
            self.request.session['otp'] = pin
            try:
                self.send_otp(pin,number)
            except:
                User.objects.filter(id = self.request.user.id).update(phone_number='')
                return render(self.request,"authentication/mobile.html",{"error":"Please Check the Phone Number"})
            return render(self.request,"authentication/otp.html")
        else:
            if self.request.POST.get('otp') == self.request.session['otp']:
                del self.request.session['otp']
                self.request.session['otp-verified'] = True
                device = self.request.META['HTTP_USER_AGENT']
                ip = self.request.META['REMOTE_ADDR']
                AccessLog.objects.create(user= self.request.user, device=device, ip=ip)
                return redirect(reverse('welcome'))
            else:
                pin = self._get_pin()
                self.request.session['otp'] = pin
                self.send_otp(pin,self.request.user.phone_number)
                return render(self.request,"authentication/otp.html")

    def send_otp(self,pin,number):
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
                                body="Your verification code is %s" % pin,
                                to=number,
                                from_=settings.TWILIO_FROM_NUMBER,
                            )

    def _get_pin(self,length=5):
        """ Return a numeric PIN with length digits """
        return str(random.sample(range(10**(length-1), 10**length), 1)[0])


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    """ Overriding default Password reset token generator for email confirmation"""

    def _make_hash_value(self, user, timestamp):
        return (six.text_type(user.pk) + six.text_type(timestamp)) + six.text_type(user.is_active)


account_activation_token = AccountActivationTokenGenerator()


class ConfirmSignUpView(View):
    """ Confirming sign up via link provided in email"""
    template_name = 'authentication/email_verified.html'

    def get(self, request, *args, **kwargs):
        """ Ckecking token and conforming account activation"""
        pk = force_text(urlsafe_base64_decode(kwargs.get('uidb64')))
        token = kwargs.get('token')
        user = get_object_or_404(User, pk=pk)
        if account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            return render(request, self.template_name, {'error': False})
        else:
            return render(request, self.template_name, {'error': True})


class UserProfileFormView(FormView):
    form_class = UserProfileForm
    template_name = 'authentication/userprofile.html'
    success_url = reverse_lazy('coins:home')

    def form_valid(self, form):
        temp_form = form.save(commit=False)
        temp_form.user = self.request.user
        temp_form.save()
        messages.add_message(self.request, messages.SUCCESS,
                             'Success!. Profile Updated')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR,
                             'Error. Please recheck form')

        return self.render_to_response(self.get_context_data(form=form))


class UserProfileView(DetailView):
    model = UserProfile
    context_object_name = 'userprofile'
    template_name = 'authentication/user_profile_view.html'

    def dispatch(self, request, *args, **kwargs):
        try:
            self.object = self.request.user.userprofile
        except:
            return redirect('auth:userprofile')

        self.get_object()
        return super(UserProfileView, self).get(request, *args, **kwargs)

    def get_object(self):
        return self.request.user.userprofile


class UserProfileUpdate(UpdateView):
    model = UserProfile
    fields = ('address_line_1', 'address_line_2', 'address_line_3',
              'landmark', 'city', 'state', 'country', 'pincode')

    template_name = 'authentication/userprofile.html'
    success_url = reverse_lazy('auth:userprofileview')

    def get_object(self):
        return self.request.user.userprofile

class WelcomeView(View):
    template_name = 'welcome.html'

    def get(self,request,*args,**kwargs):
        if self.request.user.two_factor_status:
            return redirect(reverse('auth:otp'))
        else:
            return render(request,self.template_name)
