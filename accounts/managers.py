from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """Create and return a 'User' with an email and password."""
        if not email:
            raise ValueError(_("The Email field must be set"))
        email = self.normalize_email(email)
        # Automatically set username if not provided
        if "username" not in extra_fields or not extra_fields["username"]:
            extra_fields["username"] = email.split("@")[0]  # Set username from email
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser with an email and password."""
        first_name = extra_fields.pop("first_name", None)
        last_name = extra_fields.pop("last_name", None)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if not first_name or not last_name:
            raise ValueError(_("Superuser must have a first name and a last name."))

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))

        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        if "username" not in extra_fields or not extra_fields["username"]:
            extra_fields["username"] = email.split("@")[0]

        return self.create_user(
            email, password, first_name=first_name, last_name=last_name, **extra_fields
        )
