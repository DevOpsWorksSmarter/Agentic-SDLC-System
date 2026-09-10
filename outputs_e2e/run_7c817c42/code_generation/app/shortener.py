import hashlib
import string
import time

_ALPHABET = string.ascii_letters + string.digits  # base62


def generate_code(url: str, length: int = 7) -> str:
    """Deterministic base62 code derived from URL + timestamp salt."""
    salt = str(time.time_ns())
    digest = hashlib.sha256(f"{url}{salt}".encode()).hexdigest()
    num = int(digest[:16], 16)
    code = []
    while num and len(code) < length:
        code.append(_ALPHABET[num % 62])
        num //= 62
    return "".join(reversed(code)).ljust(length, _ALPHABET[0])


def is_valid_code(code: str) -> bool:
    return 4 <= len(code) <= 12 and all(c in _ALPHABET for c in code)
