from rest_framework_simplejwt.token_blacklist.models import (
    OutstandingToken,
    BlacklistedToken,
)
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils.deprecation import MiddlewareMixin


class MaxRefreshTokenMiddleware:
    MAX_SESSIONS = 4  # Maximum allowed sessions per user

    @staticmethod
    def check_and_manage_sessions(user):
        # Get all non-blacklisted tokens for the user
        active_tokens = OutstandingToken.objects.filter(
            user=user, blacklistedtoken__isnull=True
        ).order_by("created_at")
        if active_tokens.count() >= MaxRefreshTokenMiddleware.MAX_SESSIONS:
            # Blacklist the oldest token to enforce the limit
            oldest_token = active_tokens.first()
            if oldest_token:
                BlacklistedToken.objects.create(token=oldest_token)


# Middlewares.py


class SwaggerAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Check if request is coming from Swagger UI
        if request.META.get("HTTP_USER_AGENT", "").startswith("Swagger"):
            # Use SessionAuthentication for Swagger
            session_auth = SessionAuthentication()
            try:
                request.user = session_auth.authenticate(request)[0]
            except AuthenticationFailed:
                request.user = None
        else:
            # Use JWTAuthentication for other requests
            jwt_auth = JWTAuthentication()
            try:
                user = jwt_auth.authenticate(request)
                if user is not None:
                    request.user = user[0]
            except AuthenticationFailed:
                request.user = None
