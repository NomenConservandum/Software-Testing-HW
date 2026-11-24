from __future__ import annotations

import re

import allure
from playwright.sync_api import Page

from core.config import Settings
from core.logger import get_logger
from ui.base_element import BaseElement
from ui.base_page import BasePage
from ui.pages.checkout_page import CheckoutPage

log = get_logger("autotests.ui.cart")


class CartPage(BasePage):
    """Page Object страницы корзины (/basket/)."""

    PATH = "/basket/"

    def __init__(self, page: Page, settings: Settings) -> None:
        super().__init__(page, settings)
        self.item_rows = BaseElement(
            page,
            "#basket-item-table tr[data-entity='basket-item']",
            "Позиция товара в корзине",
        )
        self.item_name_link = BaseElement(
            page,
            ".basket-item-info-name-link",
            "Название товара в корзине",
        )
        self.quantity_input = BaseElement(
            page,
            "input[data-entity='basket-item-quantity-field']",
            "Поле количества товара",
        )
        self.total_price = BaseElement(
            page,
            "[data-entity='basket-total-price']:visible",
            "Итоговая сумма корзины",
        )
        self.clear_button = BaseElement(
            page,
            ".remove_all_basket:visible",
            "Кнопка «Очистить» корзину",
        )
        self.checkout_button = BaseElement(
            page,
            "[data-entity='basket-checkout-button']:visible",
            "Кнопка «Перейти к оформлению»",
        )

    @allure.step("Открыть корзину /basket/")
    def open_cart(self) -> "CartPage":
        self.open(self.PATH)
        self.page.wait_for_load_state("networkidle")
        return self

    def wait_loaded(self) -> None:
        self.page.wait_for_load_state("networkidle")
        self.item_rows.wait_visible()

    @allure.step("Проверить товар, количество и итоговую сумму в корзине")
    def verify_item_and_total(self, expected_name: str, expected_qty: int, expected_total: int) -> None:
        assert self.item_rows.count() >= 1, "Корзина не содержит товарных позиций"
        actual_name = self.item_name_link.get_text()
        assert expected_name in actual_name, (
            f"В корзине ожидался товар '{expected_name}', получено '{actual_name}'"
        )

        qty_val = int(self.quantity_input.get_attribute("value") or "0")
        assert qty_val == expected_qty, (
            f"Неверное количество в корзине: ожидалось {expected_qty}, получено {qty_val}"
        )

        total_text = self.total_price.get_text()
        digits = re.sub(r"\D", "", total_text)
        actual_total = int(digits) if digits else 0
        assert actual_total == expected_total, (
            f"Неверный итог корзины: ожидалось {expected_total} ₽, получено '{total_text}'"
        )
        log.info("Корзина проверена: '%s', кол-во=%s, сумма=%s ₽", actual_name, qty_val, actual_total)

    @allure.step("Очистить корзину (возврат состояния)")
    def clear_if_not_empty(self) -> None:
        self.open(self.PATH)
        self.page.wait_for_load_state("networkidle")
        if self.item_rows.count() > 0 and self.clear_button.is_visible():
            log.info("Очистка корзины после теста")
            self.clear_button.click()
            self.item_rows.wait_hidden()

    @allure.step("Перейти к оформлению заказа")
    def proceed_to_checkout(self) -> CheckoutPage:
        self.checkout_button.click()
        self.page.wait_for_load_state("networkidle")
        checkout = CheckoutPage(self.page, self.settings)
        checkout.wait_loaded()
        return checkout
