from __future__ import annotations

from dataclasses import dataclass
from faker import Faker

from core.config import Settings

_fake = Faker("ru_RU")


@dataclass(frozen=True)
class ProductExpectation:
    """Ожидаемые параметры целевого товара раздела "Линолеум"."""

    search_query: str
    product_url: str
    name: str
    article: str
    price: int
    quantity: int = 1


@dataclass(frozen=True)
class CheckoutCustomerData:
    """Тестовые данные покупателя для этапа оформления заказа."""

    full_name: str
    email: str
    phone: str
    city_zip: str
    address: str
    comment: str


def get_product_expectation(settings: Settings) -> ProductExpectation:
    return ProductExpectation(
        search_query=settings.search_query,
        product_url=settings.target_product_url,
        name=settings.expected_product_name,
        article=settings.expected_product_article,
        price=settings.expected_product_price,
        quantity=1,
    )


def generate_checkout_customer(settings: Settings) -> CheckoutCustomerData:
    """Генерирует безопасные изолированные контактные данные покупателя через Faker."""
    email = settings.auth_login if "@" in settings.auth_login else f"qa.{_fake.user_name()}@example.org"
    phone = settings.auth_phone or "+7 900 000-00-01"
    return CheckoutCustomerData(
        full_name="Тестовый Покупатель Автотест",
        email=email,
        phone=phone,
        city_zip="352430",
        address="г. Курганинск, ул. Тестовая, д. 1",
        comment="Автотест UI (заказ сформирован для проверки, не выполнять)",
    )
