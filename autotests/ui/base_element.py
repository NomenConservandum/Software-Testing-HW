from __future__ import annotations

from playwright.sync_api import Locator, Page, TimeoutError as PlaywrightTimeoutError

from core.logger import get_logger
from core.masking import mask_identifier, mask_secret

log = get_logger("autotests.ui")


class BaseElement:
    """Базовая обёртка над Playwright Locator с явными ожиданиями, скроллом и маскированием логов."""

    def __init__(self, page: Page, selector: str, name: str, timeout_ms: int | None = None) -> None:
        self.page = page
        self.selector = selector
        self.name = name
        self.timeout_ms = timeout_ms

    @property
    def locator(self) -> Locator:
        return self.page.locator(self.selector)

    def wait_visible(self, timeout_ms: int | None = None) -> Locator:
        target = self.locator.first
        timeout = timeout_ms or self.timeout_ms
        try:
            if timeout is not None:
                target.wait_for(state="visible", timeout=timeout)
            else:
                target.wait_for(state="visible")
            return target
        except PlaywrightTimeoutError as exc:
            log.error("Элемент '%s' (%s) не стал видимым за %s мс", self.name, self.selector, timeout)
            raise AssertionError(
                f"Таймаут ожидания видимости элемента '{self.name}' ({self.selector}) на странице {self.page.url}"
            ) from exc

    def wait_hidden(self, timeout_ms: int | None = None) -> None:
        target = self.locator.first
        timeout = timeout_ms or self.timeout_ms
        try:
            if timeout is not None:
                target.wait_for(state="hidden", timeout=timeout)
            else:
                target.wait_for(state="hidden")
        except PlaywrightTimeoutError as exc:
            log.warning("Элемент '%s' (%s) остался видимым после ожидания", self.name, self.selector)
            raise AssertionError(f"Элемент '{self.name}' не скрылся") from exc

    def click(self, timeout_ms: int | None = None, *, position: dict[str, float] | None = None) -> None:
        target = self.wait_visible(timeout_ms=timeout_ms)
        target.scroll_into_view_if_needed()
        log.info("Клик по элементу: %s", self.name)
        log.debug("Локатор клика '%s': %s", self.name, self.selector)
        kwargs: dict = {"timeout": timeout_ms or self.timeout_ms}
        if position is not None:
            kwargs["position"] = position
        target.click(**kwargs)

    def fill(self, value: str, *, mask_kind: str | None = None, timeout_ms: int | None = None) -> None:
        target = self.wait_visible(timeout_ms=timeout_ms)
        target.scroll_into_view_if_needed()
        if mask_kind == "secret":
            logged = mask_secret(value)
        elif mask_kind == "identifier":
            logged = mask_identifier(value)
        else:
            logged = value
        log.info("Заполнение поля '%s': %s", self.name, logged)
        log.debug("Локатор поля '%s': %s", self.name, self.selector)
        target.fill(value)

    def press(self, key: str) -> None:
        target = self.wait_visible()
        log.info("Нажатие клавиши '%s' в элементе '%s'", key, self.name)
        target.press(key)

    def get_text(self, timeout_ms: int | None = None) -> str:
        target = self.wait_visible(timeout_ms=timeout_ms)
        text = target.inner_text().strip()
        log.debug("Текст элемента '%s': %s", self.name, text)
        return text

    def get_attribute(self, attr: str) -> str | None:
        target = self.wait_visible()
        return target.get_attribute(attr)

    def is_visible(self) -> bool:
        try:
            return self.locator.first.is_visible()
        except Exception:
            return False

    def count(self) -> int:
        return self.locator.count()
