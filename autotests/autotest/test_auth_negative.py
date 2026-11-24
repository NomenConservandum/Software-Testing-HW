from __future__ import annotations

import allure
import pytest

from core.config import load_settings
from core.data.auth_cases import AuthCase, build_negative_auth_cases
from core.masking import mask_identifier, mask_secret
from ui.pages.login_page import LoginPage

_NEGATIVE_CASES = build_negative_auth_cases(load_settings())


@allure.epic("Авторизация")
@allure.feature("Негативные проверки входа")
@pytest.mark.auth
@pytest.mark.parametrize("case", _NEGATIVE_CASES, ids=[c.case_id for c in _NEGATIVE_CASES])
def test_login_negative(login_page: LoginPage, case: AuthCase) -> None:
    """Параметризованные проверки отказа входа по классам ошибок (суммарно с позитивными <= 10)."""
    allure.dynamic.story(f"Класс ошибки: {case.error_class}")
    allure.dynamic.title(f"[{case.case_id}] {case.title}")
    allure.dynamic.parameter("ID кейса", case.case_id)
    allure.dynamic.parameter("Вид идентификатора", case.identifier_type)
    allure.dynamic.parameter("Класс ошибки", case.error_class)
    allure.dynamic.parameter("Входной логин", mask_identifier(case.login))
    allure.dynamic.parameter("Пароль", mask_secret(case.password))
    allure.dynamic.parameter("Ожидаемая ошибка", case.expected_error)

    login_page.open_auth()
    login_page.login(case.login, case.password)

    actual_error = login_page.get_error_text(case.error_source)
    assert case.expected_error in actual_error, (
        f"[{case.case_id}] Ожидалась ошибка '{case.expected_error}', получено '{actual_error}'"
    )
    login_page.assert_guest_session()
