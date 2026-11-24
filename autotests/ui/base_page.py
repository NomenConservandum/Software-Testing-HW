from __future__ import annotations

from playwright.sync_api import Page

from core.config import Settings
from core.logger import get_logger
from ui.base_element import BaseElement

log = get_logger("autotests.ui.page")


class BasePage:
    """Базовый Page Object с общей навигацией, поиском и контролем сессии в шапке."""

    PATH: str = "/"

    def __init__(self, page: Page, settings: Settings) -> None:
        self.page = page
        self.settings = settings
        self.search_input = BaseElement(page, "#title-search-input", "Поле поиска в шапке")
        self.header_personal_link = BaseElement(
            page,
            "header a.personal-link[href*='/personal/']:visible",
            "Кнопка личного кабинета / входа в шапке",
        )
        self.header_basket_link = BaseElement(
            page,
            "header a.basket-link[href*='/basket/']:visible",
            "Иконка корзины в шапке",
        )

    def open(self, path: str | None = None) -> "BasePage":
        target = path if path is not None else self.PATH
        url = target if target.startswith("http") else f"{self.settings.base_url}{target}"
        log.info("Переход на страницу: %s", url)
        self.page.goto(url, wait_until="domcontentloaded")
        return self

    def search(self, query: str) -> None:
        """Выполняет поиск товара через строку поиска в шапке."""
        self.search_input.fill(query)
        self.search_input.press("Enter")
        self.page.wait_for_load_state("domcontentloaded")

    def is_user_logged_in(self) -> bool:
        """Проверяет, что шапка больше не показывает 'ВОЙТИ' как для гостя."""
        if self.header_personal_link.count() == 0:
            return False
        text = self.header_personal_link.get_text().strip().lower()
        log.debug("Статус ссылки кабинета в шапке: '%s'", text)
        return text != "войти" and bool(text)

    def logout(self) -> None:
        """Возвращает сессию в исходное гостевое состояние через Bitrix logout."""
        log.info("Сброс авторизованной сессии (logout)")
        self.page.goto(f"{self.settings.base_url}/?logout=yes", wait_until="domcontentloaded")
