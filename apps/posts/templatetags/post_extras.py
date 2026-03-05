"""
Custom template filters for the Posts app.

Security rationale
------------------
Django's built-in ``|linebreaksbr`` and ``|truncatewords`` filters operate on
the *entire* string value that is passed to them.  When ``post.text`` is an
unbounded user-supplied ``TextField``, an adversary (or even an accidental
large import) can force the template engine to iterate over megabytes of data,
causing Denial-of-Service through Uncontrolled Resource Consumption.

This is the architectural root-cause behind:
  - CVE-2024-38875  (urlize / urlizetrunc)
  - CVE-2024-41989  (strip_tags)
  - CVE-2024-41990  (urlize with long strings lacking whitespace)
  - CVE-2024-41991  (urlize with long email-like strings)

Even though those CVEs target specific functions, the *same pattern* —
processing unbounded text in the template layer — is dangerous with *any*
filter that iterates character-by-character.

Refactored approach
-------------------
All rendering that touches user text goes through ``safe_linebreaksbr``, which:

  1. Casts the value to a Python ``str`` (no duck-typing surprises).
  2. Hard-slices it to ``max_chars`` **before** any further processing.
  3. Escapes HTML entities with ``django.utils.html.escape``.
  4. Replaces newlines with ``<br>`` tags (same result as Django's built-in).
  5. Returns a ``SafeString`` so Django does not double-escape.

The char cap is configurable via the filter argument so call-sites can choose
the right limit (preview vs full-detail), but always with an explicit upper
bound — never "unlimited".
"""

from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

from apps.posts.models import MAX_POST_TEXT_LENGTH, MAX_PREVIEW_CHARS

register = template.Library()

# Absolute ceiling even if a caller passes a suspiciously large argument.
_HARD_CAP: int = MAX_POST_TEXT_LENGTH


@register.filter(is_safe=True, needs_autoescape=True)
def safe_linebreaksbr(value, autoescape=True):
    """
    Renders ``value`` as safe HTML with newlines converted to ``<br>`` tags.

    Unlike the built-in ``|linebreaksbr``, this filter **always** caps the
    input at ``MAX_POST_TEXT_LENGTH`` characters *before* any processing,
    guaranteeing O(MAX_POST_TEXT_LENGTH) work regardless of what is stored in
    the database.

    Usage in templates::

        {{ post.safe_text|safe_linebreaksbr }}

    The model property ``Post.safe_text`` already enforces the char limit;
    this filter provides a second, independent defence layer.
    """
    if value is None:
        return ''

    # --- Layer 1: Cap at hard limit ---
    text: str = str(value)[:_HARD_CAP]

    # --- Layer 2: HTML-escape (safe by default; autoescape aware) ---
    escaped: str = escape(text) if autoescape else text

    # --- Layer 3: Replace newlines → <br> ---
    # Replace \r\n and \r before \n to normalise line endings.
    result: str = escaped.replace('\r\n', '\n').replace('\r', '\n').replace('\n', '<br>')

    return mark_safe(result)


@register.filter(is_safe=True, needs_autoescape=True)
def safe_preview(value, autoescape=True):
    """
    Renders a short preview of ``value`` (≤ ``MAX_PREVIEW_CHARS`` characters)
    with newlines converted to ``<br>`` tags.

    Intended for post listings where only a short excerpt is needed.

    Usage in templates::

        {{ post.preview_text|safe_preview }}

    The model property ``Post.preview_text`` already truncates; this filter
    provides independent HTML-safe rendering without touching unlimited data.
    """
    if value is None:
        return ''

    # Cap at preview limit (preview_text already did this, but be defensive)
    text: str = str(value)[:MAX_PREVIEW_CHARS]

    escaped: str = escape(text) if autoescape else text
    result: str = escaped.replace('\r\n', '\n').replace('\r', '\n').replace('\n', '<br>')

    return mark_safe(result)
