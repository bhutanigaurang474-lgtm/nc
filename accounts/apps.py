from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"
    
    def ready(self):
        # Make email field unique for User model
        from django.contrib.auth.models import User
        User._meta.get_field('email')._unique = True