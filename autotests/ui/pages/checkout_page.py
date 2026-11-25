from __future__ import annotations

import re

import allure
from playwright.sync_api import Page

from core.config import Settings
from core.data.order_data import CheckoutCustomerData
from core.logger import get_logger
from ui.base_element import BaseElement
from ui.base_page import BasePage

log = get_logger("autotests.ui.checkout")


class CheckoutPage(BasePage):
    """Page Object страницы оформления заказа (/order/)."""

    PATH = "/order/"

    def __init__(self, page: Page, settings: Settings) -> None:
        super().__init__(page, settings)
        self.order_root = BaseElement(page, "#bx-soa-order", "Форма оформления заказа")
        self.pickup_delivery_option = BaseElement(
            page,
            "#bx-soa-delivery .bx-soa-pp-company-item:has-text('Самовывоз')",
            "Способ получения "Самовывоз"",
        )
        self.cod_payment_option = BaseElement(
            page,
            "#bx-soa-paysystem .bx-soa-pp-company-item:has-text('Наложенный платеж')",
            "Способ оплаты "Наложенный платеж"",
        )
        self.zip_input = BaseElement(page, "#zipProperty:visible", "Поле "Индекс"")
        self.full_name_input = BaseElement(page, "#soa-property-1:visible", "Поле "Ф.И.О."")
        self.email_input = BaseElement(page, "#soa-property-2:visible", "Поле "E-Mail"")
        self.phone_input = BaseElement(page, "#soa-property-3:visible", "Поле "Телефон"")
        self.address_input = BaseElement(page, "#soa-property-7:visible", "Поле "Адрес доставки"")
        self.comment_input = BaseElement(page, "#orderDescription:visible", "Поле "Комментарии к заказу"")
        self.personal_data_checkbox = BaseElement(
            page,
            "#licenses_order",
            "Чекбокс согласия на обработку персональных данных",
        )
        self.personal_data_label = BaseElement(
            page,
            "label[for='licenses_order']:visible",
            "Метка согласия на обработку персональных данных",
        )
        self.offer_checkbox = BaseElement(
            page,
            "#offer_order",
            "Чекбокс согласия с публичной офертой",
        )
        self.offer_label = BaseElement(
            page,
            "label[for='offer_order']:visible",
            "Метка согласия с публичной офертой",
        )
        self.submit_order_button = BaseElement(
            page,
            "#bx-soa-order a[data-save-button='true']:visible",
            "Кнопка "Оформить заказ"",
        )
        self.order_confirmation = BaseElement(
            page,
            "#bx-soa-order .sale_order_full_table, #bx-soa-order:has-text('Заказ сформирован'), #bx-soa-order:has-text('Ваш заказ')",
            "Подтверждение созданного заказа",
        )

    def wait_loaded(self) -> None:
        self.order_root.wait_visible()
        self.submit_order_button.wait_visible()

    @allure.step("Выбрать получение "Самовывоз" и оплату "Наложенный платеж"")
    def select_pickup_and_cod(self) -> "CheckoutPage":
        if self.pickup_delivery_option.is_visible():
            self.pickup_delivery_option.click()
            self.page.wait_for_load_state("networkidle")
        if self.cod_payment_option.is_visible():
            self.cod_payment_option.click()
            self.page.wait_for_load_state("networkidle")
            cls = self.cod_payment_option.get_attribute("class") or ""
            assert "bx-selected" in cls, f"Не удалось выбрать оплату "Наложенный платеж" (class={cls})"
        return self

    @allure.step("Заполнить данные покупателя и отметить обязательные согласия")
    def fill_customer_form(self, customer: CheckoutCustomerData) -> "CheckoutPage":
        if self.zip_input.is_visible() and not self.zip_input.locator.first.input_value().strip():
            self.zip_input.fill(customer.city_zip)
        if self.full_name_input.is_visible():
            self.full_name_input.fill(customer.full_name)
        if self.email_input.is_visible():
            self.email_input.fill(customer.email, mask_kind="identifier")
        if self.phone_input.is_visible():
            self.phone_input.fill(customer.phone, mask_kind="identifier")
        if self.address_input.is_visible():
            self.address_input.fill(customer.address)
        if self.comment_input.is_visible():
            self.comment_input.fill(customer.comment)

        for checkbox, label in (
            (self.personal_data_checkbox, self.personal_data_label),
            (self.offer_checkbox, self.offer_label),
        ):
            if checkbox.count() > 0:
                inp = checkbox.locator.first
                if not inp.is_checked():
                    # Внутри <label> находится ссылка <a>; клик по левому краю попадает в сам чекбокс
                    label.click(position={"x": 5, "y": 10})
                    assert inp.is_checked(), f"Не удалось отметить согласие: {checkbox.name}"
        return self

    @allure.step("Завершить оформление заказа (E2E_SUBMIT_ORDER={submit_enabled})")
    def submit_or_verify_ready(self, *, submit_enabled: bool, expected_price: int) -> str | None:
        self.submit_order_button.wait_visible()
        if not submit_enabled:
            log.info(
                "E2E_SUBMIT_ORDER=false: форма полностью заполнена, кнопка "Оформить заказ" активна; отправка заказа пропущена"
            )
            return None

        self.submit_order_button.click()
        self.order_confirmation.wait_visible(timeout_ms=20000)
        text = self.order_confirmation.get_text()
        match = re.search(r"№\s*([A-Za-z0-9_-]+)", text)
        order_number = match.group(1) if match else "UNKNOWN"
        assert match is not None, f"На странице подтверждения не найден номер заказа: {text[:300]}"
        log.info("Заказ успешно создан, номер заказа: %s (сумма %s ₽)", order_number, expected_price)
        return order_number
