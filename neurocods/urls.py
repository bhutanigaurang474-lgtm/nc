from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.contrib.auth.decorators import login_required
from neurocods.permissions import IsSuperUser
from rest_framework.authentication import SessionAuthentication
from django.conf.urls.static import static
from django.http import JsonResponse
from django.conf import settings


schema_view = get_schema_view(
    openapi.Info(
        title="Neurocods API",
        default_version="v1",
        description="API documentation for Neurocods",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="neurocods@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[IsSuperUser],
    authentication_classes=[SessionAuthentication],
)

def home(request):
    return JsonResponse({"status": "ok", "message": "Backend is running"})

urlpatterns = [
    path("", home),
    path(
        "api-docs/",
        login_required(schema_view.with_ui("swagger", cache_timeout=0)),
        name="schema-swagger-ui",
    ),
    path("admin/", admin.site.urls),
    path("user/", include("accounts.urls")),
    path("problems/", include(("problems.urls"))),
    path("courses/", include(("courses.urls"))),
    path("concepts/", include(("concepts.urls"))),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
