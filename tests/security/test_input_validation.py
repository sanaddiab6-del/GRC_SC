"""
Tests for core/input_validation.py — XSS, SQL injection, sanitization, validators.
"""
import pytest
from fastapi import HTTPException


# ─── sanitize_string ─────────────────────────────────────────────────────────

def test_sanitize_string_normal():
    from core.input_validation import sanitize_string

    result = sanitize_string("Hello World")
    assert result == "Hello World"


def test_sanitize_string_html_escape():
    from core.input_validation import sanitize_string

    result = sanitize_string("a < b > c")
    assert "<" not in result or "&lt;" in result


def test_sanitize_string_xss_script_tag():
    from core.input_validation import sanitize_string

    with pytest.raises(HTTPException) as exc_info:
        sanitize_string("<script>alert('xss')</script>")
    assert exc_info.value.status_code == 400


def test_sanitize_string_xss_javascript():
    from core.input_validation import sanitize_string

    with pytest.raises(HTTPException):
        sanitize_string("javascript: void(0)")


def test_sanitize_string_xss_event_handler():
    from core.input_validation import sanitize_string

    with pytest.raises(HTTPException):
        sanitize_string('<img onerror="alert(1)">')


def test_sanitize_string_xss_iframe():
    from core.input_validation import sanitize_string

    with pytest.raises(HTTPException):
        sanitize_string("<iframe src='evil.com'></iframe>")


def test_sanitize_string_too_long():
    from core.input_validation import sanitize_string

    with pytest.raises(HTTPException) as exc_info:
        sanitize_string("x" * 1001, max_length=1000)
    assert exc_info.value.status_code == 400


def test_sanitize_string_non_string():
    from core.input_validation import sanitize_string

    assert sanitize_string(123) == 123  # type: ignore


# ─── validate_no_sql_injection ───────────────────────────────────────────────

def test_sql_injection_union_select():
    from core.input_validation import validate_no_sql_injection

    with pytest.raises(HTTPException):
        validate_no_sql_injection("1 UNION SELECT * FROM users")


def test_sql_injection_drop_table():
    from core.input_validation import validate_no_sql_injection

    with pytest.raises(HTTPException):
        validate_no_sql_injection("DROP TABLE users")


def test_sql_injection_insert():
    from core.input_validation import validate_no_sql_injection

    with pytest.raises(HTTPException):
        validate_no_sql_injection("INSERT INTO users VALUES (1)")


def test_sql_injection_delete():
    from core.input_validation import validate_no_sql_injection

    with pytest.raises(HTTPException):
        validate_no_sql_injection("DELETE FROM users WHERE 1=1")


def test_sql_injection_update():
    from core.input_validation import validate_no_sql_injection

    with pytest.raises(HTTPException):
        validate_no_sql_injection("UPDATE users SET admin=true")


def test_sql_injection_clean_input():
    from core.input_validation import validate_no_sql_injection

    result = validate_no_sql_injection("normal query string")
    assert result == "normal query string"


def test_sql_injection_non_string():
    from core.input_validation import validate_no_sql_injection

    assert validate_no_sql_injection(42) == 42  # type: ignore


# ─── sanitize_dict ────────────────────────────────────────────────────────────

def test_sanitize_dict_normal():
    from core.input_validation import sanitize_dict

    d = {"name": "Test", "count": 5}
    result = sanitize_dict(d)
    assert result["name"] == "Test"
    assert result["count"] == 5


def test_sanitize_dict_nested():
    from core.input_validation import sanitize_dict

    d = {"outer": {"inner": "value"}}
    result = sanitize_dict(d)
    assert result["outer"]["inner"] == "value"


def test_sanitize_dict_list_values():
    from core.input_validation import sanitize_dict

    d = {"tags": ["a", "b", "c"]}
    result = sanitize_dict(d)
    assert result["tags"] == ["a", "b", "c"]


def test_sanitize_dict_xss_in_value():
    from core.input_validation import sanitize_dict

    with pytest.raises(HTTPException):
        sanitize_dict({"name": "<script>alert(1)</script>"})


# ─── validate_uuid ────────────────────────────────────────────────────────────

def test_validate_uuid_valid():
    from core.input_validation import validate_uuid

    assert validate_uuid("550e8400-e29b-41d4-a716-446655440000")


def test_validate_uuid_invalid():
    from core.input_validation import validate_uuid

    assert not validate_uuid("not-a-uuid")
    assert not validate_uuid("12345")


# ─── validate_email ───────────────────────────────────────────────────────────

def test_validate_email_valid():
    from core.input_validation import validate_email

    assert validate_email("user@example.com")
    assert validate_email("first.last@domain.org")


def test_validate_email_invalid():
    from core.input_validation import validate_email

    assert not validate_email("invalid")
    assert not validate_email("@domain.com")
    assert not validate_email("user@")


# ─── validate_saudi_mobile ───────────────────────────────────────────────────

def test_validate_saudi_mobile_valid():
    from core.input_validation import validate_saudi_mobile

    assert validate_saudi_mobile("+966512345678")
    assert validate_saudi_mobile("966512345678")
    assert validate_saudi_mobile("0512345678")


def test_validate_saudi_mobile_invalid():
    from core.input_validation import validate_saudi_mobile

    assert not validate_saudi_mobile("12345")
    assert not validate_saudi_mobile("+1234567890")


# ─── sanitize_filename ───────────────────────────────────────────────────────

def test_sanitize_filename_normal():
    from core.input_validation import sanitize_filename

    assert sanitize_filename("report.pdf") == "report.pdf"


def test_sanitize_filename_special_chars():
    from core.input_validation import sanitize_filename

    result = sanitize_filename("file name (1).pdf")
    assert "/" not in result
    assert "\\" not in result


def test_sanitize_filename_traversal():
    from core.input_validation import sanitize_filename

    with pytest.raises(HTTPException):
        sanitize_filename("../../etc/passwd")


def test_sanitize_filename_forward_slash():
    from core.input_validation import sanitize_filename

    with pytest.raises(HTTPException):
        sanitize_filename("path/to/file")


def test_sanitize_filename_too_long():
    from core.input_validation import sanitize_filename

    with pytest.raises(HTTPException):
        sanitize_filename("a" * 256)


# ─── validate_json_size ──────────────────────────────────────────────────────

def test_validate_json_size_small():
    from core.input_validation import validate_json_size

    assert validate_json_size({"key": "value"}, max_size_kb=1) is True


def test_validate_json_size_too_large():
    from core.input_validation import validate_json_size

    big_data = {"data": "x" * 600_000}
    with pytest.raises(HTTPException) as exc_info:
        validate_json_size(big_data, max_size_kb=500)
    assert exc_info.value.status_code == 413
