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

    def add_first_product(self) -> None:
        self.page.locator(self.ADD).first.click()
        self.page.wait_for_timeout(400)

    def product_count(self) -> int:
        return self.page.locator(self.PRODUCTS).count()
