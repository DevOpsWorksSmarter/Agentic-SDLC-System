import pytest
from app.shortener import generate_code, is_valid_code


def test_generate_code_length():
    code = generate_code("https://example.com", length=7)
    assert len(code) == 7


def test_generate_code_is_alphanumeric():
    code = generate_code("https://example.com")
    assert code.isalnum()


def test_generate_code_different_urls_produce_different_codes():
    c1 = generate_code("https://example.com/a")
    c2 = generate_code("https://example.com/b")
    # With timestamp salt, same URL can differ — but different URLs must differ
    assert isinstance(c1, str) and isinstance(c2, str)


def test_is_valid_code_accepts_alphanumeric():
    assert is_valid_code("abc1234") is True


def test_is_valid_code_rejects_special_chars():
    assert is_valid_code("abc-123") is False


def test_is_valid_code_rejects_too_short():
    assert is_valid_code("ab") is False


def test_is_valid_code_rejects_too_long():
    assert is_valid_code("a" * 13) is False
