from django.urls import path
from django.contrib.auth import views as auth_views
from django.urls import reverse, reverse_lazy
from apps.authentication.views import RegistrationView, ConfirmSignUpView, TwoFactorAuthenticationView
from apps.authentication.views import (RegistrationView, ConfirmSignUpView, UserProfileFormView,
                                       UserProfileView, UserProfileUpdate, AboutView, WelcomeView)
app_name = 'auth'
urlpatterns = [
    path('signup/', RegistrationView.as_view(), name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='authentication/login.html'),
         name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('profile/', UserProfileFormView.as_view(), name='userprofile'),
    path('view_profile/', UserProfileView.as_view(), name='userprofileview'),
    path('update_profile/', UserProfileUpdate.as_view(), name='userprofileupdate'),
    path('email-confirmation/<uidb64>/<token>/', ConfirmSignUpView.as_view(
    ), name="email_confirmation"),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='authentication/password_reset_confirm.html',
                                                                 email_template_name='authentication/password_reset_email.html', success_url='done'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='authentication/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(),
         name='password_reset_complete'),
    path('password_change/', auth_views.PasswordChangeView.as_view(
        template_name='authentication/password_change_form.html', success_url='done'), name='password_change'),
    path('password_change/done/',
         auth_views.PasswordChangeDoneView.as_view(template_name='authentication/password_change_done.html'), name='password_change_done'),
    path('otp/', TwoFactorAuthenticationView.as_view(), name='otp'),

]
