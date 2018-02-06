from django.contrib import admin
from apps.authentication.models import User, UserProfile

admin.site.register(User)
admin.site.register(UserProfile)
# Register your models here.
