from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import Profile
from accounts.utils import download_and_save_profile_photo, verify_recaptcha_token


class PublicAuthViewSetTests(APITestCase):
    """Test cases for PublicAuthViewSet endpoints"""

    def setUp(self):
        """Set up test data"""
        self.user_data = {
            "email": "test@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
            "phone_number": "1234567890",
        }
        self.login_data = {
            "email": "test@example.com",
            "password": "testpass123",
            "captchaToken": "valid_token",
        }
        self.google_auth_data = {"token": "valid_google_token"}
        self.forgot_password_data = {"email": "test@example.com"}
        self.reset_password_data = {
            "email": "test@example.com",
            "token": "valid_reset_token",
            "new_password": "newpass123",
        }

    @patch("accounts.views.verify_recaptcha_token")
    def test_register_success(self, mock_recaptcha):
        """Test successful user registration"""
        mock_recaptcha.return_value = True

        url = reverse("public-auth-register")
        response = self.client.post(url, self.user_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("message", response.data)
        self.assertTrue(User.objects.filter(email=self.user_data["email"]).exists())

    def test_register_invalid_data(self):
        """Test registration with invalid data"""
        url = reverse("public-auth-register")
        invalid_data = {"email": "invalid_email"}
        response = self.client.post(url, invalid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("accounts.views.verify_recaptcha_token")
    def test_login_success(self, mock_recaptcha):
        """Test successful login using user created from registration"""
        mock_recaptcha.return_value = True

        # First register a user
        register_url = reverse("public-auth-register")
        register_response = self.client.post(
            register_url, self.user_data, format="json"
        )
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)

        # Now test login with the same user
        url = reverse("public-auth-login")
        response = self.client.post(url, self.login_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("refresh", response.data)
        self.assertIn("access", response.data)

    @patch("accounts.views.verify_recaptcha_token")
    def test_login_invalid_captcha(self, mock_recaptcha):
        """Test login with invalid captcha"""
        mock_recaptcha.return_value = False

        url = reverse("public-auth-login")
        response = self.client.post(url, self.login_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid CAPTCHA", response.data["message"])

    @patch("accounts.views.verify_recaptcha_token")
    def test_login_invalid_credentials(self, mock_recaptcha):
        """Test login with invalid credentials"""
        mock_recaptcha.return_value = True

        url = reverse("public-auth-login")
        response = self.client.post(url, self.login_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("accounts.serializers.GoogleAuthSerializer.validate")
    def test_google_auth_success(self, mock_validate):
        """Test successful Google authentication"""
        mock_validate.return_value = {
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "profile_photo_url": "https://example.com/photo.jpg",
        }

        url = reverse("public-auth-google-auth")
        response = self.client.post(url, self.google_auth_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("refresh", response.data)
        self.assertIn("access", response.data)
        self.assertIn("is_new_user", response.data)

    def test_forgot_password_success(self):
        """Test successful forgot password"""
        User.objects.create_user(
            username="testuser",
            email=self.forgot_password_data["email"],
            password="testpass123",
        )

        url = reverse("public-auth-forgot-password")
        response = self.client.post(url, self.forgot_password_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Password reset email sent", response.data["message"])

    def test_forgot_password_user_not_found(self):
        """Test forgot password with non-existent user"""
        url = reverse("public-auth-forgot-password")
        response = self.client.post(url, self.forgot_password_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("django.contrib.auth.tokens.PasswordResetTokenGenerator.check_token")
    def test_reset_password_success(self, mock_check_token):
        """Test successful password reset"""
        mock_check_token.return_value = True
        User.objects.create_user(
            username="testuser",
            email=self.reset_password_data["email"],
            password="oldpass123",
        )

        url = reverse("public-auth-reset-password")
        response = self.client.post(url, self.reset_password_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Password reset successful", response.data["message"])

    def test_reset_password_invalid_token(self):
        """Test password reset with invalid token"""
        User.objects.create_user(
            username="testuser",
            email=self.reset_password_data["email"],
            password="oldpass123",
        )

        url = reverse("public-auth-reset-password")
        response = self.client.post(url, self.reset_password_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AuthenticatedUserViewSetTests(APITestCase):
    """Test cases for AuthenticatedUserViewSet endpoints"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.profile = Profile.objects.create(user=self.user)

        # Get JWT token for authentication
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

        self.logout_data = {"refresh": str(refresh)}
        self.onboarding_data = {
            "organisation_name": "Test Org",
            "address": "Test Address",
            "language_selected": "en",
            "occupation": "Developer",
            "pronouns": "they/them",
            "date_of_birth": "1990-01-01",
        }
        self.user_detail_data = {
            "bio": "Test bio",
            "occupation": "Software Engineer",
            "github": "https://github.com/testuser",
            "linkedin": "https://linkedin.com/in/testuser",
        }

    def test_logout_success(self):
        """Test successful logout"""
        url = reverse("authenticated-user-logout")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.post(url, self.logout_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Successfully logged out", response.data["message"])

    def test_logout_invalid_token(self):
        """Test logout with invalid token"""
        url = reverse("authenticated-user-logout")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        invalid_data = {"refresh": "invalid_token"}

        response = self.client.post(url, invalid_data, format="json")

        # The view should handle the invalid token and return 400
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_complete_onboarding_success(self):
        """Test successful onboarding completion"""
        url = reverse("authenticated-user-complete-onboarding")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.post(url, self.onboarding_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Onboarding completed successfully", response.data["message"])

    def test_get_user_detail_success(self):
        """Test successful user detail retrieval"""
        url = reverse("authenticated-user-user-detail")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["email"], self.user.email)

    def test_update_user_detail_success(self):
        """Test successful user detail update"""
        url = reverse("authenticated-user-update-user-detail")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.patch(url, self.user_detail_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("User details updated successfully", response.data["message"])

    def test_get_header_data_success(self):
        """Test successful header data retrieval"""
        url = reverse("authenticated-user-header-data")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("first_name", response.data)
        self.assertIn("email", response.data)
        self.assertEqual(response.data["email"], self.user.email)

    def test_unauthenticated_access(self):
        """Test that unauthenticated users cannot access protected endpoints"""
        url = reverse("authenticated-user-logout")
        response = self.client.post(url, self.logout_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UtilsTests(TestCase):
    """Test cases for utility functions"""

    @patch("requests.post")
    def test_verify_recaptcha_token_success(self, mock_post):
        """Test successful reCAPTCHA verification"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True}
        mock_post.return_value = mock_response

        result = verify_recaptcha_token("valid_token", "secret_key")

        self.assertTrue(result)
        mock_post.assert_called_once()

    @patch("requests.post")
    def test_verify_recaptcha_token_failure(self, mock_post):
        """Test failed reCAPTCHA verification"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": False}
        mock_post.return_value = mock_response

        result = verify_recaptcha_token("invalid_token", "secret_key")

        self.assertFalse(result)

    @patch("requests.post")
    def test_verify_recaptcha_token_exception(self, mock_post):
        """Test reCAPTCHA verification with exception"""
        mock_post.side_effect = Exception("Network error")

        # The function should catch the exception and return False
        result = verify_recaptcha_token("token", "secret_key")

        self.assertFalse(result)

    @patch("requests.get")
    def test_download_and_save_profile_photo_success(self, mock_get):
        """Test successful profile photo download"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"fake_image_content"
        mock_get.return_value = mock_response

        profile = MagicMock()
        profile.profile_photo.save = MagicMock()

        download_and_save_profile_photo(profile, "https://example.com/photo.jpg", 1)

        mock_get.assert_called_once_with("https://example.com/photo.jpg", timeout=10)
        profile.profile_photo.save.assert_called_once()

    @patch("requests.get")
    def test_download_and_save_profile_photo_failure(self, mock_get):
        """Test profile photo download failure"""
        mock_get.side_effect = Exception("Network error")

        profile = MagicMock()
        profile.profile_photo.save = MagicMock()

        download_and_save_profile_photo(profile, "https://example.com/photo.jpg", 1)

        mock_get.assert_called_once()
        profile.profile_photo.save.assert_not_called()


class SerializerTests(TestCase):
    """Test cases for serializers"""

    def test_register_serializer_valid_data(self):
        """Test RegisterSerializer with valid data"""
        from accounts.serializers import RegisterSerializer

        data = {
            "email": "test@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
            "phone_number": "1234567890",
        }

        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_register_serializer_invalid_email(self):
        """Test RegisterSerializer with invalid email"""
        from accounts.serializers import RegisterSerializer

        data = {
            "email": "invalid_email",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
        }

        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_forgot_password_serializer_user_exists(self):
        """Test ForgotPasswordSerializer with existing user"""
        from accounts.serializers import ForgotPasswordSerializer

        User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        data = {"email": "test@example.com"}
        serializer = ForgotPasswordSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_forgot_password_serializer_user_not_exists(self):
        """Test ForgotPasswordSerializer with non-existent user"""
        from accounts.serializers import ForgotPasswordSerializer

        data = {"email": "nonexistent@example.com"}
        serializer = ForgotPasswordSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)


class ModelTests(TestCase):
    """Test cases for models"""

    def test_profile_creation(self):
        """Test Profile model creation"""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        profile = Profile.objects.create(user=user)

        self.assertEqual(profile.user, user)
        self.assertFalse(profile.is_premium_user)
        self.assertEqual(profile.current_streak, 0)
        self.assertEqual(profile.longest_streak, 0)

    def test_profile_user_relationship(self):
        """Test Profile-User relationship"""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        profile = Profile.objects.create(user=user)

        # Test reverse relationship
        self.assertEqual(user.profile, profile)
