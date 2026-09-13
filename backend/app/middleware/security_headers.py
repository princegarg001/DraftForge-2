"""Response security headers.

None of these were previously set. They are cheap, and each closes a distinct
class of browser-side attack.
"""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.config import get_settings

settings = get_settings()

# The API serves JSON, not HTML, so its CSP can be maximally restrictive:
# nothing should ever be loaded or executed from an API response.
_API_CSP = (
    "default-src 'none'; "
    "frame-ancestors 'none'; "
    "base-uri 'none'; "
    "form-action 'none'; "
    "sandbox"
)

# Swagger UI and ReDoc need their CDN assets, so the docs routes get a looser
# policy. These routes are disabled in production regardless.
_DOCS_CSP = (
    "default-src 'self'; "
    "img-src 'self' data: https://fastapi.tiangolo.com https://cdn.jsdelivr.net; "
    "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
    "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
    "font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net; "
    "worker-src 'self' blob:; "
    "frame-ancestors 'none'; "
    "base-uri 'self'"
)

_DOCS_PATHS = ("/docs", "/redoc", "/openapi.json")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        path = request.url.path

        is_docs = path.startswith(_DOCS_PATHS)
        response.headers["Content-Security-Policy"] = _DOCS_CSP if is_docs else _API_CSP

        # Stops MIME sniffing turning a JSON response into executable content.
        response.headers["X-Content-Type-Options"] = "nosniff"
        # Defence in depth behind CSP frame-ancestors, for older browsers.
        response.headers["X-Frame-Options"] = "DENY"
        # Keeps tokens in query strings (should any exist) out of Referer.
        response.headers["Referrer-Policy"] = "no-referrer"
        # This API needs none of these capabilities.
        response.headers["Permissions-Policy"] = (
            "accelerometer=(), camera=(), geolocation=(), gyroscope=(), "
            "magnetometer=(), microphone=(), payment=(), usb=()"
        )
        # Prevents cross-origin pages from reading responses via side channels.
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Cross-Origin-Resource-Policy"] = "same-site"

        # Sent only over TLS: a browser ignores HSTS on a plaintext response,
        # and emitting it in local development would pin localhost to https.
        if request.url.scheme == "https" or settings.is_production:
            response.headers["Strict-Transport-Security"] = (
                f"max-age={settings.HSTS_MAX_AGE_SECONDS}; includeSubDomains; preload"
            )

        # Authenticated responses must never be stored by shared caches.
        if "authorization" in request.headers and "Cache-Control" not in response.headers:
            response.headers["Cache-Control"] = "no-store, private"

        # Version disclosure aids targeted exploitation.
        response.headers.pop("Server", None)
        response.headers.pop("X-Powered-By", None)

        return response
