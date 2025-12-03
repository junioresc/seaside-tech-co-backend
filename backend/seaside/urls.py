from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


def health(_request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health, name="health"),
    path("api/v1/", include("apps.users.urls")),
    path("api/v1/", include("apps.products.urls")),
    path("api/v1/", include("apps.repairs.urls")),
    path("api/v1/", include("apps.appointments.urls")),
    path("api/v1/", include("apps.payments.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]
