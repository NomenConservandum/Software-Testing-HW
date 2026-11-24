from __future__ import annotations

import allure
import pytest
from playwright.sync_api import sync_playwright

from core.browser import create_isolated_context, create_page, launch_browser
from core.config import Settings, load_settings
from core.logger import get_logger, read_recent_logs, setup_logger
from core.masking import mask_text
from ui.pages.cart_page import CartPage
from ui.pages.catalog_page import CatalogPage
from ui.pages.login_page import LoginPage

log = get_logger("autotests.conftest")


@pytest.fixture(scope="session")
def settings() -> Settings:
    cfg = load_settings()
    setup_logger(cfg.log_level, secrets=cfg.sensitive_values)
    log.info("Инициализация тестов: стенд=%s, браузер=%s, headless=%s", cfg.base_url, cfg.browser, cfg.headless)
    return cfg


@pytest.fixture(scope="session")
def browser(settings: Settings):
    with sync_playwright() as pw:
        br = launch_browser(pw, settings)
        try:
            yield br
        finally:
            log.info("Закрытие браузера после завершения тестовой сессии")
            br.close()


@pytest.fixture(scope="function")
def page(browser, settings: Settings, request):
    context = create_isolated_context(browser, settings)
    pw_page = create_page(context, settings)
    request.node._pw_page = pw_page
    request.node._settings = settings

    try:
        yield pw_page
    finally:
        log.debug("Закрытие изолированного контекста браузера после теста %s", request.node.name)
        context.close()


@pytest.fixture
def login_page(page, settings: Settings) -> LoginPage:
    return LoginPage(page, settings)


@pytest.fixture
def catalog_page(page, settings: Settings) -> CatalogPage:
    return CatalogPage(page, settings)


@pytest.fixture
def cart_page(page, settings: Settings) -> CartPage:
    return CartPage(page, settings)


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when not in {"setup", "call"} or not report.failed:
        return

    pw_page = getattr(item, "_pw_page", None)
    cfg = getattr(item, "_settings", None)
    secrets = cfg.sensitive_values if cfg else ()

    if call.excinfo is not None:
        safe_err = mask_text(str(call.excinfo.getrepr(style="short")), secrets)
        allure.attach(safe_err, name="Диагностика ошибки", attachment_type=allure.attachment_type.TEXT)

    if pw_page is not None:
        try:
            allure.attach(pw_page.url, name="URL в момент сбоя", attachment_type=allure.attachment_type.TEXT)
            png_bytes = pw_page.screenshot(full_page=True)
            allure.attach(png_bytes, name="Скриншот при падении", attachment_type=allure.attachment_type.PNG)
        except Exception as exc:
            reason = f"Скриншот недоступен: {mask_text(str(exc), secrets)}"
            log.warning(reason)
            allure.attach(reason, name="Причина отсутствия скриншота", attachment_type=allure.attachment_type.TEXT)
    else:
        allure.attach(
            "Скриншот недоступен: страница Playwright не была создана на момент падения.",
            name="Причина отсутствия скриншота",
            attachment_type=allure.attachment_type.TEXT,
        )

    recent_logs = read_recent_logs(60)
    if recent_logs:
        allure.attach(recent_logs, name="Лог выполнения (маскированный)", attachment_type=allure.attachment_type.TEXT)
