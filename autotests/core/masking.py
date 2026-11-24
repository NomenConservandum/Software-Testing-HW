from __future__ import annotations

import re
from typing import Iterable

_EMAIL_RE = re.compile(r"([A-Za-z0-9._%+-]{1,})@([A-Za-z0-9.-]+\.[A-Za-z]{2,})")
_PHONE_RE = re.compile(r"(\+?\d[\d\s\-()]{6,}\d)")
_TOKEN_RE = re.compile(
    r"((?:PHPSESSID|sessid|token|cookie|password|USER_PASSWORD)\s*[:=]\s*)([^\s;,&]+)",
    re.IGNORECASE,
)


def mask_secret(value: str | None) -> str:
    """Полностью скрывает пароль или токен."""
    if not value:
        return "<empty>"
    return "*" * max(6, min(len(value), 12))


def mask_email(email: str | None) -> str:
    """Маскирует локальную часть и часть домена email."""
    if not email:
        return "<empty>"
    if "@" not in email:
        return mask_identifier(email)
    local, domain = email.split("@", 1)
    masked_local = f"{local[0]}***" if local else "***"
    return f"{masked_local}@{domain}"


def mask_phone(phone: str | None) -> str:
    """Оставляет только код/начало и 2 последние цифры номера телефона."""
    if not phone:
        return "<empty>"
    digits = re.sub(r"\D", "", phone)
    if len(digits) <= 4:
        return "***"
    prefix = "+" if phone.strip().startswith("+") else ""
    return f"{prefix}{digits[:2]}{'*' * (len(digits) - 4)}{digits[-2:]}"


def mask_identifier(value: str | None) -> str:
    """Универсальное маскирование логина (email, телефон или текстовый логин)."""
    if value is None or value == "":
        return "<empty>"
    if "@" in value:
        return mask_email(value)
    digits = re.sub(r"\D", "", value)
    if len(digits) >= 7:
        return mask_phone(value)
    if len(value) <= 2:
        return "*" * len(value)
    return f"{value[0]}***{value[-1]}"


def mask_text(text: str, extra_secrets: Iterable[str] = ()) -> str:
    """Маскирует известные секреты, email, телефоны и токены в произвольной строке."""
    if not text:
        return text
    result = text
    for secret in sorted({s for s in extra_secrets if s and len(s) >= 2}, key=len, reverse=True):
        if secret in result:
            replacement = mask_identifier(secret) if ("@" in secret or re.search(r"\d{7,}", secret)) else mask_secret(secret)
            result = result.replace(secret, replacement)

    result = _TOKEN_RE.sub(lambda m: f"{m.group(1)}{mask_secret(m.group(2))}", result)
    result = _EMAIL_RE.sub(lambda m: mask_email(m.group(0)), result)
    result = _PHONE_RE.sub(lambda m: mask_phone(m.group(0)), result)
    return result
