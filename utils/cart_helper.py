from playwright.sync_api import Page

from config.settings import BASE_URL


def seed_cart(page: Page, qty: int = 1) -> None:
    page.goto(BASE_URL + "index.html", wait_until="domcontentloaded")
    page.evaluate(
        """(qty) => {
          const item = [{ id: 'g16', name: 'Amul Taaza Milk', price: 31, qty }];
          localStorage.setItem('sjCartItems', JSON.stringify(item));
          localStorage.setItem('sjCartCount', String(qty));
        }""",
        qty,
    )
    page.reload(wait_until="domcontentloaded")


def clear_cart(page: Page) -> None:
    page.goto(BASE_URL + "index.html", wait_until="domcontentloaded")
    page.evaluate(
        """() => {
          localStorage.removeItem('sjCartItems');
          localStorage.setItem('sjCartCount', '0');
        }"""
    )
