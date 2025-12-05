from django.urls import include, path
from rest_framework.routers import DefaultRouter

from problems.views import (
    AuthenticatedProblemsViewSet,
    PublicProblemsViewSet,
)

# Create router instances
public_router = DefaultRouter()
authenticated_router = DefaultRouter()

# Register viewsets with routers
public_router.register(r"", PublicProblemsViewSet, basename="public-problems")
authenticated_router.register(
    r"", AuthenticatedProblemsViewSet, basename="authenticated-problems"
)

urlpatterns = [
    # Public problem endpoints
    path("", include(public_router.urls)),
    # Authenticated problem endpoints
    path("", include(authenticated_router.urls)),
]
