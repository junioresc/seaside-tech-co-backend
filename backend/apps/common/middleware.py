from typing import Callable

from django.http import HttpRequest, HttpResponse


class StoreScopeMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        store_id = request.headers.get("X-Store-ID")
        if store_id:
            request.store_id = store_id  # type: ignore[attr-defined]
        return self.get_response(request)


