"""Typed exception hierarchy for SaavnKit."""
from __future__ import annotations


class SaavnError(Exception):
    """Base for every SaavnKit error."""


class NetworkError(SaavnError):
    """Transport / connectivity failure."""


class APIError(SaavnError):
    """JioSaavn API returned a non-OK response."""
    def __init__(self, message: str, *, status: int | None = None, url: str | None = None):
        super().__init__(message)
        self.status = status
        self.url = url


class RateLimitError(APIError):
    """Rate limit hit (HTTP 429 or local bucket empty)."""


class NotFoundError(APIError):
    """Requested resource does not exist."""


class GeoBlockedError(APIError):
    """Content is not available in the current region."""


class ParseError(SaavnError):
    """Response body could not be parsed / had unexpected shape."""


class AuthError(SaavnError):
    """Missing / invalid credentials for an optional integration (Spotify, YouTube)."""


class DownloadError(SaavnError):
    """Something went wrong while downloading or tagging a track."""


__all__ = [
    "SaavnError", "NetworkError", "APIError", "RateLimitError",
    "NotFoundError", "GeoBlockedError", "ParseError", "AuthError",
    "DownloadError",
]
