from __future__ import annotations

import re

import allure
from playwright.sync_api import Page

from core.config import Settings
from core.logger import get_logger
from ui.base_element import BaseElement
from ui.base_page import BasePage
from ui.pages.cart_page import CartPage

log = get_logger("autotests.ui.product")


class ProductPage(BasePage):
    """Page Object карточки товара."""

    def __init__(self, page: Page, settings: Settings) -> None:
        super().__init__(page, settings)
        self.title = BaseElement(page, "h1", "Наименование товара (H1)")
        self.article = BaseElement(
            page,
            ".catalog_detail .article:visible",
            "Блок артикула товара",
        )
        self.price = BaseElement(
            page,
            ".catalog_detail .price[data-value]:visible",
            "Цена товара",
        )
        self.add_to_cart_button = BaseElement(
            page,
            ".catalog_detail .to-cart:visible",
            "Кнопка "В корзину"",
        )
        self.in_cart_link = BaseElement(
            page,
            ".catalog_detail a.in-cart",
            "Кнопка/ссылка "В корзине"",
        )

    @allure.step("Проверить данные карточки товара")
    def verify_product_details(self, expected_name: str, expected_article: str, expected_price: int) -> None:
        actual_name = self.title.get_text()
        assert expected_name in actual_name, (
            f"Неверное наименование товара: ожидалось '{expected_name}', получено '{actual_name}'"
        )

        article_text = self.article.get_text()
        assert expected_article in article_text, (
            f"Неверный артикул: ожидался '{expected_article}', получено '{article_text}'"
        )

        raw_price = self.price.get_attribute("data-value") or self.price.get_text()
        digits = re.sub(r"\D", "", str(raw_price))
        actual_price = int(digits) if digits else 0
        assert actual_price == expected_price, (
            f"Неверная цена товара: ожидалось {expected_price}, получено {actual_price}"
        )
        log.info(
            "Карточка подтверждена: '%s', артикул %s, цена %s ₽",
            actual_name,
            expected_article,
            actual_price,
        )

    @allure.step("Добавить товар в корзину")
    def add_to_cart(self) -> "ProductPage":
        if self.in_cart_link.is_visible():
            log.warning("Товар уже находился в корзине перед добавлением")
            return self
        self.add_to_cart_button.click()
        self.in_cart_link.wait_visible()
        log.info("Товар добавлен в корзину, отобразился индикатор "В корзине"")
        return self

    @allure.step("Перейти в корзину")
    def go_to_basket(self) -> CartPage:
        self.in_cart_link.click()
        self.page.wait_for_load_state("domcontentloaded")
        cart_page = CartPage(self.page, self.settings)
        cart_page.wait_loaded()
        return cart_page
