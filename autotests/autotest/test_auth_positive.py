from __future__ import annotations

import allure
import pytest

from core.config import Settings
from core.masking import mask_identifier, mask_secret
from ui.pages.login_page import LoginPage


@allure.epic("Авторизация")
@allure.feature("Успешный вход в аккаунт")
@pytest.mark.auth
def test_login_with_email_or_login_success(login_page: LoginPage, settings: Settings) -> None:
    """AUTH-POS-01: Успешная авторизация по основному логину/email и паролю из .env."""
    if not settings.auth_login or not settings.auth_password:
        pytest.skip("Укажите AUTH_LOGIN и AUTH_PASSWORD в файле .env для запуска позитивной проверки входа.")

    allure.dynamic.title("[AUTH-POS-01] Успешная авторизация (логин/email + пароль)")
    allure.dynamic.parameter("ID кейса", "AUTH-POS-01")
    allure.dynamic.parameter("Способ входа", "email / логин + пароль")
    allure.dynamic.parameter("Логин", mask_identifier(settings.auth_login))
    allure.dynamic.parameter("Пароль", mask_secret(settings.auth_password))

    login_page.open_auth()
    try:
        login_page.login(settings.auth_login, settings.auth_password)
        login_page.assert_logged_in()
    finally:
        login_page.logout()


@allure.epic("Авторизация")
@allure.feature("Успешный вход в аккаунт")
@pytest.mark.auth
def test_login_with_phone_success(login_page: LoginPage, settings: Settings) -> None:
    """AUTH-POS-02: Успешная авторизация по телефону и паролю (если AUTH_PHONE задан в .env)."""
    if not settings.auth_phone or not settings.auth_password:
        pytest.skip("Укажите AUTH_PHONE и AUTH_PASSWORD в файле .env, если аккаунт поддерживает вход по телефону.")

    allure.dynamic.title("[AUTH-POS-02] Успешная авторизация (телефон + пароль)")
    allure.dynamic.parameter("ID кейса", "AUTH-POS-02")
    allure.dynamic.parameter("Способ входа", "телефон + пароль")
    allure.dynamic.parameter("Телефон", mask_identifier(settings.auth_phone))
    allure.dynamic.parameter("Пароль", mask_secret(settings.auth_password))

    login_page.open_auth()
    try:
        login_page.login(settings.auth_phone, settings.auth_password)
        login_page.assert_logged_in()
    finally:
        login_page.logout()
