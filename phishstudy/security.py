"""Security primitives: password hashing, sessions, CSRF and rate limiting.

Everything here uses the Python standard library only.

Design notes (also used in the project report):

* Passwords are never stored. We keep ``pbkdf2_hmac('sha256', ...)`` with a
  per-account random salt and 260,000 iterations, encoded as ``iter$salt$hash``.
* Comparison uses :func:`hmac.compare_digest` to avoid timing leaks.
* Sessions are random 256-bit tokens kept server-side and sent as an
  ``HttpOnly`` + ``SameSite=Lax`` cookie. Only the hash of a token is stored.
* Every state-changing request must carry a per-session CSRF token.
* Login attempts are rate-limited per (client, username) pair.
"""
from __future__ import annotations

import hashlib
import hmac
import secrets
import time

PBKDF2_ITERATIONS = 260_000
SESSION_TTL_SECONDS = 8 * 60 * 60          # 8 hours
LOGIN_WINDOW_SECONDS = 15 * 60
LOGIN_MAX_ATTEMPTS = 8


# --------------------------------------------------------------------- passwords
def hash_password(password: str, *, iterations: int = PBKDF2_ITERATIONS) -> str:
    """Return ``iterations$salt$hash`` for *password*."""
    if not isinstance(password, str) or not password:
        raise ValueError("password must be a non-empty string")
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), iterations)
    return f"{iterations}${salt}${digest.hex()}"


def verify_password(password: str, encoded: str) -> bool:
    """Constant-time verification of *password* against an encoded hash."""
    try:
        iterations_s, salt, expected = encoded.split("$", 2)
        iterations = int(iterations_s)
    except (AttributeError, ValueError):
        return False
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), iterations)
    return hmac.compare_digest(digest.hex(), expected)


# --------------------------------------------------------------------- sessions
def new_token(nbytes: int = 32) -> str:
    return secrets.token_urlsafe(nbytes)


def token_fingerprint(token: str) -> str:
    """Sessions are looked up by SHA-256 so a database leak cannot be replayed."""
    return hashlib.sha256(token.encode()).hexdigest()


# --------------------------------------------------------------------- throttling
class LoginThrottle:
    """Small in-process sliding-window limiter for login attempts.

    A real deployment would use Redis or the database; for a single-process
    teaching application an in-memory table is sufficient and easy to audit.
    """

    def __init__(self, max_attempts: int = LOGIN_MAX_ATTEMPTS,
                 window: int = LOGIN_WINDOW_SECONDS) -> None:
        self.max_attempts = max_attempts
        self.window = window
        self._hits: dict[str, list[float]] = {}

    def _key(self, client: str, username: str) -> str:
        return f"{client}|{username.lower()}"

    def _prune(self, key: str, now: float) -> list[float]:
        hits = [t for t in self._hits.get(key, []) if now - t < self.window]
        if hits:
            self._hits[key] = hits
        else:
            self._hits.pop(key, None)
        return hits

    def blocked(self, client: str, username: str) -> int:
        """Return seconds until the next attempt is allowed (0 = allowed)."""
        now = time.time()
        hits = self._prune(self._key(client, username), now)
        if len(hits) < self.max_attempts:
            return 0
        return max(1, int(self.window - (now - hits[0])))

    def fail(self, client: str, username: str) -> None:
        now = time.time()
        key = self._key(client, username)
        self._prune(key, now)
        self._hits.setdefault(key, []).append(now)

    def reset(self, client: str, username: str) -> None:
        self._hits.pop(self._key(client, username), None)
