from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    AuthenticatedUserViewSet,
    DashboardViewSet,
    PublicAuthViewSet,
)

# Create router instances
public_router = DefaultRouter()
authenticated_router = DefaultRouter()
dashboard_router = DefaultRouter()

# Register viewsets with routers
public_router.register(r"", PublicAuthViewSet, basename="public-auth")
authenticated_router.register(
    r"", AuthenticatedUserViewSet, basename="authenticated-user"
)
dashboard_router.register(r"", DashboardViewSet, basename="dashboard")

urlpatterns = [
    # Public authentication endpoints
    path("", include(public_router.urls)),
    # Authenticated endpoints
    path("", include(authenticated_router.urls)),
    # Dashboard endpoints
    path("dashboard/", include(dashboard_router.urls)),
    # JWT token refresh
    path("generate-access-token/", TokenRefreshView.as_view(), name="token_refresh"),
]
