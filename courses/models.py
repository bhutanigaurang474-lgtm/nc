from django.db import models
from django.contrib.auth.models import User
from ncore.models import Slugged


# Create your models here.
class Course(Slugged, models.Model):
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    followers = models.ManyToManyField(
        User,
        related_name="followed_courses",
        blank=True,
    )
    likes = models.ManyToManyField(
        User,
        related_name="liked_courses",
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
