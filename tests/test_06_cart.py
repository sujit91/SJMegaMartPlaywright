import pytest
from playwright.sync_api import Page, expect

from config.settings import BASE_URL
from pages.cart_page import CartPage
from pages.home_page import HomePage
from utils.cart_helper import clear_cart, seed_cart


pytestmark = [pytest.mark.cart, pytest.mark.regression]


@pytest.mark.smoke
def test_empty_cart_page(page: Page):
    clear_cart(page)
    CartPage(page).open()
    expect(page.locator("body")).to_be_visible()


def test_add_product_updates_badge(page: Page):
    clear_cart(page)
    home = HomePage(page)
    home.open()
    home.add_first_product()
    assert home.cart_count() >= 1


def test_seeded_cart_shows_item(page: Page):
    seed_cart(page, 2)
    CartPage(page).open()
    expect(page.locator("#cartItemsList")).to_contain_text("Amul Taaza Milk")


def test_cart_page_loads(page: Page):
    seed_cart(page)
    CartPage(page).open()
    assert "cart.html" in page.url


def test_proceed_to_checkout_link(page: Page):
    seed_cart(page)
    CartPage(page).open()
    expect(page.locator("a[href*='checkout']").first).to_be_visible()


def test_cart_count_after_seed(page: Page):
    seed_cart(page, 3)
    home = HomePage(page)
    home.open()
    assert home.cart_count() >= 3


def test_add_two_products(page: Page):
    clear_cart(page)
    home = HomePage(page)
    home.open()
    home.add_first_product()
    buttons = page.locator(".add-btn")
    if buttons.count() > 1:
        buttons.nth(1).click()
        page.wait_for_timeout(400)
    assert home.cart_count() >= 1


def test_cart_persists_after_reload(page: Page):
    seed_cart(page, 1)
    page.reload()
    assert HomePage(page).cart_count() >= 1


def test_cart_icon_navigates(page: Page):
    HomePage(page).open()
    page.locator("a[href*='cart.html']").first.click()
    page.wait_for_timeout(500)
    assert "cart.html" in page.url


def test_clear_cart_resets_count(page: Page):
    seed_cart(page, 2)
    clear_cart(page)
    HomePage(page).open()
    assert HomePage(page).cart_count() == 0


def test_checkout_from_cart(page: Page):
    seed_cart(page)
    cart = CartPage(page)
    cart.open()
    cart.proceed_to_checkout()
    page.wait_for_timeout(800)
    assert "checkout.html" in page.url or "login.html" in page.url


def test_cart_html_shell(page: Page):
    page.goto(BASE_URL + "cart.html")
    expect(page.locator("body")).to_be_visible()
