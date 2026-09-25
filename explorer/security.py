"""Password hashing and input validation helpers (standard library only)."""

from __future__ import annotations

import base64
import hashlib
import hmac
import re
import secrets

# scrypt parameters: N=2^14, r=8, p=1 -> ~16 MiB, well under a second.
_N, _R, _P, _DKLEN = 2**14, 8, 1, 32
_PREFIX = "scrypt"

USERNAME_RE = re.compile(r"^[A-Za-z0-9_.-]{3,32}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD_LEN = 8


def hash_password(password: str) -> str:
    """Return a self-describing hash string safe to store in the database."""
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=_N, r=_R, p=_P, dklen=_DKLEN)
    b64 = lambda b: base64.b64encode(b).decode()  # noqa: E731
    return f"{_PREFIX}${_N}${_R}${_P}${b64(salt)}${b64(digest)}"


def verify_password(password: str, stored: str) -> bool:
    """Constant-time check of ``password`` against a value from ``hash_password``."""
    try:
        prefix, n, r, p, salt_b64, digest_b64 = stored.split("$")
        if prefix != _PREFIX:
            return False
        salt = base64.b64decode(salt_b64)
        expected = base64.b64decode(digest_b64)
        actual = hashlib.scrypt(
            password.encode(), salt=salt, n=int(n), r=int(r), p=int(p), dklen=len(expected)
        )
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(actual, expected)


def validate_signup(username: str, email: str, password: str, confirm: str) -> list[str]:
    """Return a list of human-readable problems; empty means the input is valid."""
    errors = []
    if not USERNAME_RE.match(username):
        errors.append("Username must be 3–32 characters: letters, digits, dot, dash or underscore.")
    if not EMAIL_RE.match(email):
        errors.append("Enter a valid email address.")
    if len(password) < MIN_PASSWORD_LEN:
        errors.append(f"Password must be at least {MIN_PASSWORD_LEN} characters.")
    if password != confirm:
        errors.append("Passwords do not match.")
    return errors
