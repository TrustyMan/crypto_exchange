from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.urls import reverse, reverse_lazy
from apps.authentication.views import RegistrationView, ConfirmSignUpView, TwoFactorAuthenticationView

app_name = 'auth'
urlpatterns = [
    url(r'^signup/', RegistrationView.as_view(), name='signup'),
    url(r'^login/$', auth_views.LoginView.as_view(template_name='authentication/login.html'),
        name='login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    url(r'email-confirmation/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', ConfirmSignUpView.as_view(
    ), name="email_confirmation"),
    url(r'^password_reset/$', auth_views.PasswordResetView.as_view(template_name='authentication/password_reset_confirm.html',
                                                                   email_template_name='authentication/password_reset_email.html', success_url='done'), name='password_reset'),
    url(r'^password_reset/done/$', auth_views.PasswordResetDoneView.as_view(
        template_name='authentication/password_reset_done.html'), name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.PasswordResetCompleteView.as_view(),
        name='password_reset_complete'),
    url(r'^password_change/$', auth_views.PasswordChangeView.as_view(
        template_name='authentication/password_change_form.html', success_url='done'), name='password_change'),
    url(r'^password_change/done/$',
        auth_views.PasswordChangeDoneView.as_view(template_name='authentication/password_change_done.html'), name='password_change_done'),
    url(r'otp/$',TwoFactorAuthenticationView.as_view(), name='otp'),

]
