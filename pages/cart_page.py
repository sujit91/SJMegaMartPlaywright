from pages.base_page import BasePage


class CartPage(BasePage):
    ITEMS = "#cartItemsList .cart-item, .cart-item"
    EMPTY = ".empty-state, .cart-empty"
    CHECKOUT = "a.primary-btn, a[href*='checkout']"
    QTY_PLUS = ".qty-plus, button[data-qty='plus']"
    QTY_MINUS = ".qty-minus, button[data-qty='minus']"

    def open(self) -> None:
        self.goto("cart.html")

    def item_count(self) -> int:
        return self.page.locator(self.ITEMS).count()

    def proceed_to_checkout(self) -> None:
        self.page.locator(self.CHECKOUT).first.click()
