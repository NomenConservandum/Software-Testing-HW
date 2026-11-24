from __future__ import annotations

from dataclasses import dataclass
from faker import Faker

from core.config import Settings

_fake = Faker("ru_RU")
_fake.seed_instance(20261124)


@dataclass(frozen=True)
class AuthCase:
    """Один самостоятельно выполняемый параметризованный набор проверки авторизации."""

    case_id: str
    title: str
    error_class: str
    identifier_type: str
    login: str
    password: str
    expected_error: str
    error_source: str  # "client" (label.error) | "server" (.alert-danger)


def build_negative_auth_cases(settings: Settings) -> list[AuthCase]:
    """Формирует 7 негативных наборов по всем требуемым классам ошибок (<= 10 с позитивными)."""
    existing_or_isolated_login = settings.auth_login or f"qa.target.{_fake.user_name()}@example.org"
    wrong_password = f"Wrong_{_fake.password(length=10)}"
    if settings.auth_password:
        wrong_case_password = settings.auth_password.swapcase()
        if wrong_case_password == settings.auth_password:
            wrong_case_password = f"{settings.auth_password}!"
    else:
        wrong_case_password = "qatest_wrong_case_42"

    nonexistent_email = f"absent.{_fake.user_name()}.{_fake.random_int(1000, 9999)}@example.org"
    nonexistent_phone = f"+7900{_fake.random_int(1000000, 9999999)}"
    sample_password = f"Qa_{_fake.password(length=8)}"

    return [
        AuthCase(
            case_id="AUTH-NEG-01",
            title="Отказ при пустом идентификаторе",
            error_class="пустой идентификатор",
            identifier_type="empty",
            login="",
            password=sample_password,
            expected_error="Заполните это поле",
            error_source="client",
        ),
        AuthCase(
            case_id="AUTH-NEG-02",
            title="Отказ при пустом пароле",
            error_class="пустой пароль",
            identifier_type="email",
            login=existing_or_isolated_login,
            password="",
            expected_error="Заполните это поле",
            error_source="client",
        ),
        AuthCase(
            case_id="AUTH-NEG-03",
            title="Отказ при некорректном формате логина",
            error_class="неверный формат",
            identifier_type="invalid_format",
            login="invalid@@format login!",
            password=sample_password,
            expected_error="Неверный логин или пароль",
            error_source="server",
        ),
        AuthCase(
            case_id="AUTH-NEG-04",
            title="Отказ при несуществующем email",
            error_class="несуществующий аккаунт",
            identifier_type="email",
            login=nonexistent_email,
            password=sample_password,
            expected_error="Неверный логин или пароль",
            error_source="server",
        ),
        AuthCase(
            case_id="AUTH-NEG-05",
            title="Отказ при несуществующем телефоне",
            error_class="несуществующий аккаунт",
            identifier_type="phone",
            login=nonexistent_phone,
            password=sample_password,
            expected_error="Неверный логин или пароль",
            error_source="server",
        ),
        AuthCase(
            case_id="AUTH-NEG-06",
            title="Отказ при неверном пароле",
            error_class="неверный пароль",
            identifier_type="login",
            login=existing_or_isolated_login,
            password=wrong_password,
            expected_error="Неверный логин или пароль",
            error_source="server",
        ),
        AuthCase(
            case_id="AUTH-NEG-07",
            title="Отказ при неверном регистре пароля",
            error_class="неверный пароль (регистр)",
            identifier_type="login",
            login=existing_or_isolated_login,
            password=wrong_case_password,
            expected_error="Неверный логин или пароль",
            error_source="server",
        ),
    ]
