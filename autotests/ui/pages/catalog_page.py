from __future__ import annotations

import allure
from playwright.sync_api import Page

from core.config import Settings
from core.logger import get_logger
from ui.base_element import BaseElement
from ui.base_page import BasePage
from ui.pages.product_page import ProductPage

log = get_logger("autotests.ui.catalog")


class CatalogPage(BasePage):
    """Page Object раздела каталога и поисковой выдачи."""

    def __init__(self, page: Page, settings: Settings) -> None:
        super().__init__(page, settings)
        self.PATH = settings.catalog_path
        self.product_titles = BaseElement(
            page,
            ".catalog_item_wrapp .item-title a",
            "Ссылки товаров в результатах каталога/поиска",
        )

    @allure.step("Открыть раздел каталога "Линолеум"")
    def open_linoleum_catalog(self) -> "CatalogPage":
        self.open(self.settings.catalog_path)
        self.product_titles.wait_visible()
        return self

    @allure.step("Найти товар по запросу "{query}"")
    def search_product(self, query: str) -> "CatalogPage":
        self.search(query)
        self.product_titles.wait_visible()
        return self

    @allure.step("Проверить наличие товара "{expected_name}" в выдаче и открыть карточку")
    def open_product_from_results(self, expected_name: str) -> ProductPage:
        matching = self.page.locator(
            f".catalog_item_wrapp .item-title a:has-text('{expected_name}')"
        )
        assert matching.count() > 0, (
            f"Товар '{expected_name}' не найден в результатах поиска на {self.page.url}"
        )
        link = BaseElement(
            self.page,
            f".catalog_item_wrapp .item-title a:has-text('{expected_name}')",
            f"Карточка товара '{expected_name}'",
        )
        link.click()
        self.page.wait_for_load_state("domcontentloaded")
        product_page = ProductPage(self.page, self.settings)
        product_page.title.wait_visible()
        log.info("Открыта карточка товара: %s", self.page.url)
        return product_page
