from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _parse_bool(value: str | None, default: bool) -> bool:
    if value is None or not value.strip():
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


@dataclass(frozen=True)
class Settings:
    """Настройки стенда и запуска автотестов, загружаемые из .env и окружения."""

    base_url: str
    catalog_path: str
    auth_login: str
    auth_password: str
    auth_phone: str
    browser: str
    browser_executable_path: str
    headless: bool
    timeout_ms: int
    log_level: str
    search_query: str
    product_url: str
    expected_product_name: str
    expected_product_article: str
    expected_product_price: int
    e2e_submit_order: bool

    @property
    def catalog_url(self) -> str:
        return f"{self.base_url.rstrip('/')}/{self.catalog_path.lstrip('/')}"

    @property
    def target_product_url(self) -> str:
        if self.product_url.startswith("http"):
            return self.product_url
        return f"{self.base_url.rstrip('/')}/{self.product_url.lstrip('/')}"

    @property
    def sensitive_values(self) -> tuple[str, ...]:
        """Возвращает непустые секреты, подлежащие обязательному маскированию."""
        return tuple(
            v for v in (self.auth_password, self.auth_login, self.auth_phone) if v and len(v) >= 2
        )


def load_settings(env_path: Path | None = None) -> Settings:
    """Читает конфигурацию из .env (если файл существует) и переменных окружения."""
    target_env = env_path or (PROJECT_ROOT / ".env")
    if target_env.exists():
        load_dotenv(target_env, override=False)

    return Settings(
        base_url=os.getenv("BASE_URL", "https://www.udacha-market.ru").rstrip("/"),
        catalog_path=os.getenv("CATALOG_PATH", "/catalog/napolnye_pokrytiya/linoleum/"),
        auth_login=os.getenv("AUTH_LOGIN", "").strip(),
        auth_password=os.getenv("AUTH_PASSWORD", ""),
        auth_phone=os.getenv("AUTH_PHONE", "").strip(),
        browser=os.getenv("BROWSER", "chromium").strip().lower() or "chromium",
        browser_executable_path=os.getenv("BROWSER_EXECUTABLE_PATH", "/usr/bin/chromium").strip(),
        headless=_parse_bool(os.getenv("HEADLESS"), default=True),
        timeout_ms=int(os.getenv("TIMEOUT_MS", "15000")),
        log_level=os.getenv("LOG_LEVEL", "INFO").strip().upper() or "INFO",
        search_query=os.getenv("SEARCH_QUERY", "Avanta Karuzo 4").strip(),
        product_url=os.getenv(
            "PRODUCT_URL",
            "/catalog/napolnye_pokrytiya/linoleum/linoleum_2_0m/482839/",
        ).strip(),
        expected_product_name=os.getenv(
            "EXPECTED_PRODUCT_NAME",
            "Линолеум 2,0м Avanta Karuzo 4",
        ).strip(),
        expected_product_article=os.getenv("EXPECTED_PRODUCT_ARTICLE", "14823").strip(),
        expected_product_price=int(os.getenv("EXPECTED_PRODUCT_PRICE", "450")),
        e2e_submit_order=_parse_bool(os.getenv("E2E_SUBMIT_ORDER"), default=False),
    )
