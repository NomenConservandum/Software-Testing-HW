from __future__ import annotations

from pathlib import Path

from playwright.sync_api import Browser, BrowserContext, Page, Playwright

from core.config import Settings
from core.logger import get_logger

log = get_logger("autotests.browser")


def launch_browser(playwright: Playwright, settings: Settings) -> Browser:
    """Запускает браузер Playwright с fallback на системный executable_path при необходимости."""
    browser_type = getattr(playwright, settings.browser, playwright.chromium)
    launch_kwargs: dict = {"headless": settings.headless}

    exec_path = settings.browser_executable_path
    if exec_path and Path(exec_path).exists():
        launch_kwargs["executable_path"] = exec_path
        log.debug("Запуск браузера %s через путь: %s (headless=%s)", settings.browser, exec_path, settings.headless)
    else:
        log.debug("Запуск встроенного браузера Playwright %s (headless=%s)", settings.browser, settings.headless)

    return browser_type.launch(**launch_kwargs)


def create_isolated_context(browser: Browser, settings: Settings) -> BrowserContext:
    """Создаёт чистый BrowserContext для изоляции cookies, сессии и корзины между тестами."""
    context = browser.new_context(
        viewport={"width": 1440, "height": 900},
        locale="ru-RU",
    )
    context.set_default_timeout(settings.timeout_ms)
    context.set_default_navigation_timeout(settings.timeout_ms)
    return context


def create_page(context: BrowserContext, settings: Settings) -> Page:
    page = context.new_page()
    page.set_default_timeout(settings.timeout_ms)
    return page
