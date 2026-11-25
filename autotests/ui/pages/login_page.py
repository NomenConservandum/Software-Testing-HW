from __future__ import annotations

import allure
from playwright.sync_api import Page

from core.config import Settings
from core.logger import get_logger
from ui.base_element import BaseElement
from ui.base_page import BasePage

log = get_logger("autotests.ui.login")


class LoginPage(BasePage):
    """Page Object страницы авторизации (/auth/)."""

    PATH = "/auth/"

    def __init__(self, page: Page, settings: Settings) -> None:
        super().__init__(page, settings)
        self.auth_form = BaseElement(page, "#auth-page-form", "Форма авторизации")
        self.login_input = BaseElement(page, "#USER_LOGIN_POPUP", "Поле логина (email/телефон)")
        self.password_input = BaseElement(page, "#USER_PASSWORD_POPUP", "Поле пароля")
        self.submit_button = BaseElement(
            page,
            "#auth-page-form button[type='submit'][name='Login1']",
            "Кнопка "Войти"",
        )
        self.client_error_label = BaseElement(
            page,
            "#auth-page-form label.error:visible",
            "Ошибка клиентской валидации поля",
        )
        self.server_error_alert = BaseElement(
            page,
            ".alert-danger:visible, font.errortext:visible, .errortext:visible",
            "Серверное сообщение об ошибке входа",
        )
        self.logout_link = BaseElement(
            page,
            "a[href*='logout=yes']:visible",
            "Ссылка выхода из аккаунта",
        )

    @allure.step("Открыть страницу авторизации /auth/")
    def open_auth(self) -> "LoginPage":
        self.open(self.PATH)
        self.auth_form.wait_visible()
        return self

    @allure.step("Выполнить попытку входа")
    def login(self, login_value: str, password_value: str) -> "LoginPage":
        self.login_input.fill(login_value, mask_kind="identifier")
        self.password_input.fill(password_value, mask_kind="secret")
        self.submit_button.click()
        return self

    @allure.step("Дождаться сообщения об ошибке (источник: {source})")
    def get_error_text(self, source: str) -> str:
        if source == "client":
            self.client_error_label.wait_visible()
            texts = [el.inner_text().strip() for el in self.client_error_label.locator.all() if el.is_visible()]
            combined = "; ".join(t for t in texts if t)
            log.info("Получена клиентская ошибка валидации: %s", combined)
            return combined

        self.server_error_alert.wait_visible()
        text = self.server_error_alert.get_text()
        log.info("Получена серверная ошибка входа: %s", text)
        return text

    @allure.step("Подтвердить, что авторизованная сессия не создана")
    def assert_guest_session(self) -> None:
        assert "/auth/" in self.page.url, f"Ожидалось нахождение на /auth/, текущий URL: {self.page.url}"
        assert self.auth_form.is_visible(), "Форма входа должна оставаться открытой при отказе"
        assert not self.is_user_logged_in(), "Гость не должен отображаться как авторизованный пользователь"

    @allure.step("Подтвердить успешный вход в личный кабинет")
    def assert_logged_in(self) -> None:
        self.page.wait_for_load_state("domcontentloaded")
        if "/auth/" in self.page.url and self.server_error_alert.is_visible():
            err = self.server_error_alert.get_text()
            raise AssertionError(f"Вход завершился ошибкой сайта: {err}")

        self.page.goto(f"{self.settings.base_url}/personal/", wait_until="domcontentloaded")
        assert "/auth/" not in self.page.url and not self.auth_form.is_visible(), (
            f"После успешного входа /personal/ не должен перенаправлять на форму входа (URL={self.page.url})"
        )
        assert self.is_user_logged_in(), "В шапке должен отображаться профиль авторизованного пользователя"
