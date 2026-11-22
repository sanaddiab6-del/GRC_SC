"""Regression tests for raw Knox token exposure via Django's exception-reporting filter.

iam/views.py extracts the raw Knox bearer token into local variables (auth_header,
access_token) in SessionTokenView and RevokeOtherSessionsView, with no surrounding
try/except, so an unhandled exception there puts the raw token in the local variables of
that stack frame.

Django's SafeExceptionReporterFilter only redacts a function's local variables when it is
decorated with @sensitive_variables, AND only when `filter.is_active(request)` is true --
which is `settings.DEBUG is False` (see SafeExceptionReporterFilter.is_active: "If DEBUG is
True then your site is not safe anyway"). So this protects local variables only in the path
that matters: a DEBUG=False deployment where something downstream of an unhandled exception
(Django's admin-email error reporting, or a monitoring integration such as Sentry) inspects
the traceback's local variables. It does NOT and cannot protect the interactive DEBUG=True
error page -- Django deliberately never redacts that page's local variables, decorated or
not, and this repository's docker-compose.prod.yml already pins DJANGO_DEBUG=False, with no
ADMINS/mail_admins or Sentry integration configured. So today there is no reachable sink
that would actually display these variables; the decorator is forward-looking hardening for
whenever such an integration is added, verified directly against the redaction mechanism
Django itself uses to decide whether to protect a variable.
"""

import sys

import pytest
from django.test import RequestFactory, override_settings
from django.views.debug import ExceptionReporter

from iam.views import RevokeOtherSessionsView, SessionTokenView

SECRET_TOKEN_MARKER = "totally-not-a-real-secret-marker-value"


def _redacted_vars_for(view_callable, request, function_name):
    """Return the cleansed {name: value} dict for the named function's frame."""
    try:
        view_callable(request)
    except Exception:
        exc_info = sys.exc_info()
    else:
        raise AssertionError("expected the view call to raise")
    reporter = ExceptionReporter(request, *exc_info)
    frames = [
        f
        for f in reporter.get_traceback_data()["frames"]
        if f.get("function") == function_name and "iam" in f.get("filename", "")
    ]
    assert frames, f"no iam/views.py frame found for function {function_name!r}"
    return dict(frames[-1]["vars"])


@pytest.mark.django_db
@override_settings(DEBUG=False)
def test_session_token_view_hides_the_raw_token_from_its_own_frame_when_debug_is_false():
    request = RequestFactory().post(
        "/", HTTP_AUTHORIZATION=f"Token {SECRET_TOKEN_MARKER}"
    )
    frame_vars = _redacted_vars_for(SessionTokenView().post, request, "post")
    assert SECRET_TOKEN_MARKER not in str(frame_vars["access_token"])
    assert SECRET_TOKEN_MARKER not in str(frame_vars["auth_header"])


@override_settings(DEBUG=False)
def test_revoke_other_sessions_view_hides_the_raw_token_from_its_own_frame_when_debug_is_false():
    # No request.user is attached (AuthenticationMiddleware did not run), so
    # `request.user.id` raises AttributeError after auth_header/access_token are set.
    request = RequestFactory().post(
        "/", HTTP_AUTHORIZATION=f"Token {SECRET_TOKEN_MARKER}"
    )
    frame_vars = _redacted_vars_for(RevokeOtherSessionsView().post, request, "post")
    assert SECRET_TOKEN_MARKER not in str(frame_vars["access_token"])
    assert SECRET_TOKEN_MARKER not in str(frame_vars["auth_header"])
