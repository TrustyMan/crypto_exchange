from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.crypto import get_random_string


class User(AbstractUser):
    first_name = models.CharField(max_length=200, blank=True, default="")
    last_name = models.CharField(max_length=200, blank=True, default="")
    phone_number = models.CharField(max_length=20, blank=True, default="")
    two_factor_status = models.BooleanField()


class UserProfile(models.Model):
    """User Profile"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    country = models.CharField(max_length=128, help_text='Country of Permanent Residence')
    state = models.CharField(max_length=128, help_text='State of Permanent Residence')
    city = models.CharField(max_length=128, help_text='City of Permanent Residence')
    landmark = models.CharField(
        max_length=128, help_text='Enter a landmark closest to you')
    address_line_1 = models.CharField(
        max_length=128, help_text='House name/Flat No')
    address_line_2 = models.CharField(
        max_length=128, help_text='Street Name/No')
    address_line_3 = models.CharField(
        max_length=128, help_text='Locality Name')
    pincode = models.CharField(max_length=128, null=False, help_text='pincode/zipcode of your area')

    def __str__(self):
        return self.user.email