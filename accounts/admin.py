from django.contrib import admin
from django.contrib.auth.models import User
from .models import Profile

# Simple approach - just register Profile separately
admin.site.register(Profile)
