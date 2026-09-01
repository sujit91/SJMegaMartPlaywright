import re

from playwright.sync_api import Page, expect

from config.settings import BASE_URL, DEFAULT_TIMEOUT


class BasePage:
    def __init__(self, page: Page):
        self.page = page
        self.timeout = DEFAULT_TIMEOUT



    def goto(self, path: str = "") -> None:
        url = path if path.startswith("http") else f"{BASE_URL}{path.lstrip('/')}"
        self.page.goto(url, wait_until="domcontentloaded")
        self.page.wait_for_timeout(400)

    def click(self, selector: str) -> None:
        self.page.locator(selector).first.click()

    def fill(self, selector: str, value: str) -> None:
        loc = self.page.locator(selector).first
        loc.fill("")
        loc.fill(value)

    def text(self, selector: str) -> str:
        return self.page.locator(selector).first.inner_text()

    def is_visible(self, selector: str) -> bool:
        return self.page.locator(selector).first.is_visible()

    def expect_visible(self, selector: str) -> None:
        expect(self.page.locator(selector).first).to_be_visible(timeout=self.timeout)

    def expect_url_contains(self, fragment: str) -> None:
        expect(self.page).to_have_url(re.compile(re.escape(fragment)), timeout=self.timeout)

    def cart_count(self) -> int:
        loc = self.page.locator(".cart-count").first
        if loc.count() == 0:
            return 0
        raw = (loc.inner_text() or "0").strip()
        return int(raw) if raw.isdigit() else 0

    def auth_label(self) -> str:
        loc = self.page.locator(".auth-label").first
        if loc.count() == 0:
            return ""
        return loc.inner_text().strip()
