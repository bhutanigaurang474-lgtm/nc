import os

from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from google.auth.transport import requests
from google.oauth2 import id_token
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import Profile

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="User with this email already exists",
            )
        ],
    )
    username = serializers.CharField(
        required=False,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="User with this username already exists",
            )
        ],
    )
    password = serializers.CharField(required=True, write_only=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    phone_number = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )

    class Meta:
        model = User
        fields = (
            "username",
            "password",
            "email",
            "phone_number",
            "first_name",
            "last_name",
        )


class LoginRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    recaptcha = serializers.CharField(required=True, write_only=True)


class LoginResponseSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField()


class GoogleAuthSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)

    def validate(self, data):
        token = data.get("token")
        try:
            # Verify the token with Google's API
            idinfo = id_token.verify_oauth2_token(
                token, requests.Request(), GOOGLE_CLIENT_ID
            )

            # Check if the token's audience matches your app
            if idinfo["aud"] != GOOGLE_CLIENT_ID:
                raise serializers.ValidationError("Invalid Google token.")

            # Extract user information
            data["email"] = idinfo["email"]
            data["first_name"] = idinfo.get("given_name", "")
            data["last_name"] = idinfo.get("family_name", "")
            data["profile_photo_url"] = idinfo.get("picture", "")
            return data
        except ValueError as e:
            raise serializers.ValidationError(f"Invalid Google token: {str(e)}")


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist")
        return value


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True
    )  # The email for resetting the password
    token = serializers.CharField(required=True)  # Token from the email link
    new_password = serializers.CharField(
        required=True, write_only=True, min_length=8
    )  # New password

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Invalid email")
        return value

    def validate(self, data):
        """
        Validate token
        """
        email = data.get("email")
        token = data.get("token")

        user = User.objects.get(email=email)
        token_generator = PasswordResetTokenGenerator()

        if not token_generator.check_token(user, token):
            raise serializers.ValidationError({"token": "Invalid or expired token"})

        return data


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)


class OnboardingSerializer(serializers.ModelSerializer):
    organisation_name = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    address = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    language_selected = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    occupation = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    pronouns = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    date_of_birth = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = Profile
        fields = (
            "organisation_name",
            "address",
            "language_selected",
            "occupation",
            "pronouns",
            "date_of_birth",
        )


class UserDetailSerializer(serializers.ModelSerializer):
    profile_photo = serializers.ImageField(required=False, allow_null=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Profile
        fields = [
            "first_name",
            "last_name",
            "phone_number",
            "organisation_name",
            "address",
            "language_selected",
            "profile_photo",
            "is_premium_user",
            "bio",
            "occupation",
            "kaggle_profile_url",
            "github",
            "twitter",
            "portfolio",
            "linkedin",
            "pronouns",
            "interests",
            "date_of_birth",
        ]

    def validate_profile_photo(self, value):
        """
        Validate profile photo file size and type
        """
        if value:
            # Check file size (2MB = 2 * 1024 * 1024 bytes)
            max_size = 2 * 1024 * 1024
            if value.size > max_size:
                raise serializers.ValidationError(
                    "Profile photo size should not exceed 2MB."
                )

            # Check file type
            allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/gif"]
            if value.content_type not in allowed_types:
                raise serializers.ValidationError(
                    "Only JPEG, PNG, and GIF images are allowed."
                )

        return value

    def to_representation(self, instance):
        """
        Override to include first_name and last_name from User model
        """
        representation = super().to_representation(instance)
        # Add User model fields
        representation["first_name"] = instance.user.first_name
        representation["last_name"] = instance.user.last_name
        return representation

    def save(self, **kwargs):
        """
        Override save to exclude first_name and last_name from Profile save
        These fields will be handled separately in the view for User model
        """
        # Remove User fields from validated_data before saving to Profile
        validated_data = self.validated_data.copy()
        validated_data.pop("first_name", None)
        validated_data.pop("last_name", None)

        # Update instance with Profile fields only
        for attr, value in validated_data.items():
            setattr(self.instance, attr, value)
        self.instance.save()

        return self.instance
