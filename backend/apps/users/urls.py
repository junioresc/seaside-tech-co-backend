from django.urls import path

from .views import CookieTokenObtainPairView, CookieTokenRefreshView, MeAvatarView

urlpatterns = [
    path("auth/login/", CookieTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", CookieTokenRefreshView.as_view(), name="token_refresh"),
    path("users/me/avatar/", MeAvatarView.as_view(), name="me-avatar"),
]
