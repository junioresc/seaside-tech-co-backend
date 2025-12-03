from io import BytesIO

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from PIL import Image
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

REFRESH_COOKIE_NAME = "refresh"


def set_refresh_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        REFRESH_COOKIE_NAME,
        refresh_token,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="Lax",
        max_age=7 * 24 * 3600,
        path="/api/v1/auth/",
    )


class CookieTokenObtainPairView(TokenObtainPairView):
    def post(self, request: Request, *args, **kwargs) -> Response:
        response = super().post(request, *args, **kwargs)
        refresh = response.data.get("refresh")
        if refresh:
            set_refresh_cookie(response, refresh)
            # Do not expose refresh in body when cookie is set
            response.data.pop("refresh", None)
        return response


class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request: Request, *args, **kwargs) -> Response:
        if not request.data.get("refresh"):
            cookie_refresh = request.COOKIES.get(REFRESH_COOKIE_NAME)
            if cookie_refresh:
                request.data["refresh"] = cookie_refresh
        response = super().post(request, *args, **kwargs)
        new_refresh = response.data.get("refresh")
        if new_refresh:
            set_refresh_cookie(response, new_refresh)
            response.data.pop("refresh", None)
        return response


class MeAvatarView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    MAX_SIZE = 5 * 1024 * 1024  # 5MB
    ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}

    def post(self, request: Request) -> Response:
        file = request.FILES.get("avatar")
        if not file:
            return Response({"detail": "avatar file is required"}, status=400)
        if file.size > self.MAX_SIZE:
            return Response({"detail": "file too large"}, status=400)
        content_type = getattr(file, "content_type", "")
        if content_type not in self.ALLOWED_CONTENT_TYPES:
            return Response({"detail": "unsupported file type"}, status=400)

        profile = request.user.profile  # type: ignore[attr-defined]
        # Delete old files if present
        if profile.avatar:
            try:
                default_storage.delete(profile.avatar.name)
            except Exception:
                pass
        if getattr(profile, "avatar_thumb", None):
            try:
                default_storage.delete(profile.avatar_thumb.name)
            except Exception:
                pass

        # Save main avatar
        profile.avatar.save(file.name, file, save=False)

        # Generate thumbnail (256x256, maintaining aspect)
        file.seek(0)
        image = Image.open(file)
        image = image.convert("RGB") if image.mode in ("RGBA", "P") else image
        image.thumbnail((256, 256))
        thumb_buffer = BytesIO()
        image.save(thumb_buffer, format="JPEG", quality=85, optimize=True)
        thumb_content = ContentFile(thumb_buffer.getvalue())
        thumb_name = f"thumb_{file.name.rsplit('.', 1)[0]}.jpg"
        profile.avatar_thumb.save(thumb_name, thumb_content, save=False)

        profile.save(update_fields=["avatar", "avatar_thumb"])
        return Response(
            {"avatar_url": profile.avatar.url, "avatar_thumb_url": profile.avatar_thumb.url},
            status=200,
        )

    def delete(self, request: Request) -> Response:
        profile = request.user.profile  # type: ignore[attr-defined]
        if profile.avatar:
            try:
                default_storage.delete(profile.avatar.name)
            except Exception:
                pass
            profile.avatar = None
        if getattr(profile, "avatar_thumb", None):
            try:
                default_storage.delete(profile.avatar_thumb.name)
            except Exception:
                pass
            profile.avatar_thumb = None
        profile.save(update_fields=["avatar", "avatar_thumb"])
        return Response(status=204)
