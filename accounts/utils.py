import requests
from django.conf import settings
from django.core.files.base import ContentFile


def verify_recaptcha_token(captcha_token: str, secret_key: str) -> bool:
    """
    Verifies the reCAPTCHA token using Google's reCAPTCHA API.

    Args:
        captcha_token (str): The token received from the frontend reCAPTCHA widget.
        secret_key (str): Your Google reCAPTCHA secret key.

    Returns:
        bool: True if the token is valid, False otherwise.
    """
    verify_url = "https://www.google.com/recaptcha/api/siteverify"
    data = {
        "secret": secret_key,
        "response": captcha_token,
    }

    try:
        response = requests.post(verify_url, data=data)
        result = response.json()
        return result.get("success", False)
    except Exception as e:
        print(f"Error verifying reCAPTCHA: {e}")
        return False


def download_and_save_profile_photo(profile, profile_photo_url, user_id):
    """
    Download and save profile photo from Google.

    Args:
        profile: Profile instance to save the photo to
        profile_photo_url: URL of the profile photo to download
        user_id: User ID for filename generation

    Returns:
        bool: True if photo was successfully downloaded and saved, False otherwise
    """
    try:
        response = requests.get(profile_photo_url, timeout=10)
        response.raise_for_status()

        file_extension = profile_photo_url.split(".")[-1].split("?")[0]
        if file_extension not in ["jpg", "jpeg", "png", "gif"]:
            file_extension = "jpg"

        filename = f"google_profile_{user_id}.{file_extension}"

        profile.profile_photo.save(filename, ContentFile(response.content), save=True)
    except Exception as e:
        if settings.DEBUG:
            print(f"Failed to download profile photo: {e}")
