import uuid

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import IntegrityError, models
from django.template.defaultfilters import slugify
from django.utils.translation import gettext_lazy as _

from ncore.utils import base_concrete_model, get_unique_slug


class Tag(models.Model):
    name = models.CharField(max_length=255, unique=True)


class Tagged(models.Model):
    tags = models.ManyToManyField(Tag, blank=True)

    def get_tags_list(self):
        return list(self.tags.values_list("name", flat=True))

    def set_tags_list(self, tags_list):
        """Sets tags from a list."""
        self.tags.set(
            [Tag.objects.get_or_create(name=tag.strip())[0] for tag in tags_list]
        )

    class Meta:
        abstract = True


class Slugged(models.Model):
    """
    Abstract model that handles auto-generating slugs.
    """

    title = models.CharField(_("Title"), max_length=255, default="")
    slug = models.CharField(
        _("URL"), max_length=255, unique=True, db_index=True, blank=True
    )

    class Meta:
        abstract = True
        ordering = ("title",)

    def _str_(self):
        return self.title

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.title:
            slug = self.get_slug()
            if not slug:
                raise ValidationError(
                    "Please enter a valid title/name, it must contain at least one character"
                )

    def save(self, *args, **kwargs):  # pylint: disable=W0221
        """
        Create a unique slug by appending an index.
        """
        update_slug = kwargs.pop("update_slug", False)
        concrete_model = base_concrete_model(Slugged, self)

        new_slug = False
        if not self.slug or update_slug:
            new_slug = True

        # XXX: Remove this once you have verified that kwargs never contains
        # update key.
        kwargs.pop("update", False)

        retry = 0
        max_retry = 3
        while retry < max_retry:
            try:
                if new_slug:
                    self.slug = get_unique_slug(
                        concrete_model, self.get_slug(), self.id
                    )
                super(Slugged, self).save(*args, **kwargs)
                break
            except IntegrityError as e:
                print(e)
                retry += 1

    def get_slug(self):
        """
        Allows subclasses to implement their own slug creation logic.
        """

        # If we have already defined slug, return slug as it is
        if self.slug:
            return self.slug

        slug = ""
        # if title is None, slugify returns 'none' as string.
        if self.title is not None:
            slug = slugify(self.title)

        # For titles like !@#$!@#$, slugify returns an empty string.
        if slug == "":
            slug = str(uuid.uuid1())[:7]
        return slug[:256]


class GenericRelation(models.Model):
    """
    Abstract model that provides generic foreign key functionality.
    Allows models to reference any other model through content_type and object_id.
    """

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

    def clean(self):
        if not self.content_type or not self.object_id:
            raise ValidationError("Content object must be specified.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
