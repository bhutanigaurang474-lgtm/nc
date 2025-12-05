from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from accounts.constants import LANGUAGE_CHOICES


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    organisation_name = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    language_selected = models.CharField(
        max_length=255, choices=LANGUAGE_CHOICES, default="eng"
    )
    profile_photo = models.ImageField(
        upload_to='profile_photos/', 
        blank=True, 
        null=True,
        help_text="Profile photo (max 2MB)"
    )
    is_premium_user = models.BooleanField(default=False)
    bio = models.TextField(blank=True, null=True)
    occupation = models.CharField(max_length=255, blank=True, null=True)
    kaggle_profile_url = models.URLField(max_length=500, blank=True, null=True)
    github = models.URLField(max_length=500, blank=True, null=True)
    twitter = models.URLField(max_length=500, blank=True, null=True)
    portfolio = models.URLField(max_length=500, blank=True, null=True)
    linkedin = models.URLField(max_length=500, blank=True, null=True)
    pronouns = models.CharField(max_length=50, blank=True, null=True)
    interests = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    current_day_concept_read = models.BooleanField(default=False)
    current_day_problem_solved = models.BooleanField(default=False)
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    is_onboarding_complete = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s Profile"
