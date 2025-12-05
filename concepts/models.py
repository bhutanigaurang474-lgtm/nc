from django.contrib.auth.models import User
from django.db import models

from ncore.models import Slugged, Tagged


class Concept(Tagged, Slugged, models.Model):
    LEVEL_CHOICES = [
        ("Easy", "Easy"),
        ("Medium", "Medium"),
        ("Hard", "Hard"),
    ]
    CONCEPT_CHOICES = [
        ("ML", "Machine Learning"),
        ("DL", "Deep Learning"),
    ]

    description = models.TextField()
    one_liner_desc = models.CharField(max_length=255)
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES)
    last_updated_timestamp = models.DateTimeField(auto_now=True)
    creation_timestamp = models.DateTimeField(auto_now_add=True)
    preview_image_url = models.CharField(max_length=1000)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    concept_type = models.CharField(
        max_length=255, choices=CONCEPT_CHOICES, default="ML"
    )
    saved_by = models.ManyToManyField(
        User,
        related_name="saved_by_users",
        blank=True,
    )

    def __str__(self):
        return self.slug


class ConceptsRead(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    concept = models.ForeignKey(
        Concept, on_delete=models.CASCADE, related_name="concepts_read"
    )
    read_timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "concept")

    def __str__(self):
        return f"{self.user.username} - {self.concept.title}"
