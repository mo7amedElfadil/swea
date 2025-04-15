"""Email validation utilities."""

import re

import dns.resolver
from flask_babel import gettext as _

from app.extensions import DISPOSABLE_DOMAINS


def has_mx_records(domain: str) -> bool:
    """
    Check if the domain has valid MX records.
    """
    try:
        answers = dns.resolver.resolve(domain, "MX")
        return bool(answers)
    except (
        dns.resolver.NoAnswer,
        dns.resolver.NXDOMAIN,
        dns.resolver.Timeout,
    ):
        return False


def validate_email(email: str) -> None:
    """
    Validate an email address:
    - Check format
    - Ensure it's not a disposable email
    - Verify MX records

    Raises:
        ValueError: If the email is invalid.
    """
    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    if not re.match(email_regex, email):
        raise ValueError(_("Invalid email format"))

    domain = email.split("@")[-1].lower()

    if domain in DISPOSABLE_DOMAINS:
        raise ValueError(_("Disposable email addresses are not allowed"))

    if not has_mx_records(domain):
        raise ValueError(_("Email domain does not have valid MX records"))
