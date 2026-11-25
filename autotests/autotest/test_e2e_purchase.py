from __future__ import annotations

import allure
import pytest

from core.config import Settings
from core.data.order_data import generate_checkout_customer, get_product_expectation
from core.masking import mask_identifier
from ui.pages.cart_page import CartPage
from ui.pages.catalog_page import CatalogPage
from ui.pages.login_page import LoginPage


@allure.epic("Сквозной сценарий")
@allure.feature("Покупка товара из раздела "Линолеум"")
@pytest.mark.e2e
def test_e2e_purchase_flow(
    login_page: LoginPage,
    catalog_page: CatalogPage,
    cart_page: CartPage,
    settings: Settings,
) -> None:
    """E2E-01: Вход -> поиск товара -> карточка -> корзина -> оформление заказа."""
    if not settings.auth_login or not settings.auth_password:
        pytest.skip("Укажите AUTH_LOGIN и AUTH_PASSWORD в файле .env для прохождения сквозного сценария с авторизацией.")

    product_exp = get_product_expectation(settings)
    customer = generate_checkout_customer(settings)

    allure.dynamic.title("[E2E-01] Полный путь покупки линолеума после авторизации")
    allure.dynamic.parameter("ID кейса", "E2E-01")
    allure.dynamic.parameter("Покупатель", mask_identifier(settings.auth_login))
    allure.dynamic.parameter("Товар", product_exp.name)
    allure.dynamic.parameter("Артикул", product_exp.article)
    allure.dynamic.parameter("Отправка заказа", str(settings.e2e_submit_order))

    login_page.open_auth()
    order_submitted = False
    try:
        # 1. Вход
        login_page.login(settings.auth_login, settings.auth_password)
        login_page.assert_logged_in()

        # Предусловие чистоты корзины авторизованного аккаунта
        cart_page.clear_if_not_empty()

        # 2. Поиск
        catalog_page.open_linoleum_catalog()
        catalog_page.search_product(product_exp.search_query)

        # 3. Карточка товара
        product_page = catalog_page.open_product_from_results(product_exp.name)
        product_page.verify_product_details(
            expected_name=product_exp.name,
            expected_article=product_exp.article,
            expected_price=product_exp.price,
        )

        # 4. Корзина
        product_page.add_to_cart()
        basket = product_page.go_to_basket()
        basket.verify_item_and_total(
            expected_name=product_exp.name,
            expected_qty=product_exp.quantity,
            expected_total=product_exp.price * product_exp.quantity,
        )

        # 5-6. Оформление и подтверждение заказа
        checkout = basket.proceed_to_checkout()
        checkout.select_pickup_and_cod()
        checkout.fill_customer_form(customer)
        order_number = checkout.submit_or_verify_ready(
            submit_enabled=settings.e2e_submit_order,
            expected_price=product_exp.price * product_exp.quantity,
        )
        if settings.e2e_submit_order:
            assert order_number is not None and order_number != "UNKNOWN"
            allure.dynamic.parameter("Номер заказа", order_number)
            order_submitted = True
    finally:
        if not order_submitted:
            cart_page.clear_if_not_empty()
        login_page.logout()
