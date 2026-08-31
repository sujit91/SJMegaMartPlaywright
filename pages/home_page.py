from playwright.sync_api import expect

from pages.base_page import BasePage


class HomePage(BasePage):
    SEARCH = "#siteSearch, input[type='search']"
    TABS = ".category-tab"
    DROPDOWN = ".tab-dropdown, .category-dropdown"
    PRODUCTS = ".product-card"
    ADD = ".add-btn"
    CART = "a[href*='cart.html']"

    def open(self) -> None:
        self.goto("index.html")

    def search(self, term: str) -> None:
        self.fill(self.SEARCH, term)
        self.page.locator(self.SEARCH).first.press("Enter")
        self.page.wait_for_timeout(500)

    def open_category(self, slug: str) -> None:
        self.goto(f"index.html?cat={slug}")

    def hover_tab(self, name: str) -> None:
        self.page.get_by_role("link", name=name).first.hover()

    def category_tab(self, tab_key: str):
        return self.page.locator(f".category-tab[data-tab='{tab_key}']")

    def category_tab_item(self, tab_key: str):
        return self.page.locator(f".category-tab-item:has(.category-tab[data-tab='{tab_key}'])")

    def expect_category_nav(self, tab_key: str, href: str | None = None) -> None:
        href = href or f"{tab_key}.html"
        tab = self.category_tab(tab_key)
        expect(tab).to_be_visible()
        item = self.category_tab_item(tab_key)
        (item if item.count() else tab).hover()
        if item.count():
            expect(item.locator(f"a[href='{href}']").first).to_be_visible()
            return
        links = self.page.locator(f"a[href='{href}']")
        assert any(links.nth(i).is_visible() for i in range(links.count())), (
            f"No visible nav link for {href}"
        )

    def add_first_product(self) -> None:
        self.page.locator(self.ADD).first.click()
        self.page.wait_for_timeout(400)

    def product_count(self) -> int:
        return self.page.locator(self.PRODUCTS).count()
