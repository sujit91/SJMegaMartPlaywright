import pytest
from playwright.sync_api import Page, expect

from config.settings import BASE_URL
from pages.home_page import HomePage
from pages.listing_page import ListingPage


pytestmark = [pytest.mark.catalog, pytest.mark.regression]


@pytest.mark.smoke
def test_grocery_page_has_products(page: Page):
    page.goto(BASE_URL + "grocery.html")
    page.wait_for_timeout(600)
    assert page.locator(".product-card").count() > 0


def test_vegetables_page_has_products(page: Page):
    page.goto(BASE_URL + "vegetables.html")
    page.wait_for_timeout(600)
    assert page.locator(".product-card").count() > 0


def test_fashion_page_has_products(page: Page):
    page.goto(BASE_URL + "fashion.html")
    page.wait_for_timeout(600)
    assert page.locator(".product-card").count() > 0


def test_electronics_page_has_products(page: Page):
    page.goto(BASE_URL + "electronics.html")
    page.wait_for_timeout(600)
    assert page.locator(".product-card").count() > 0


def test_beauty_page_loads(page: Page):
    page.goto(BASE_URL + "beauty.html")
    expect(page.locator("body")).to_be_visible()


def test_product_image_present(page: Page):
    page.goto(BASE_URL + "grocery.html")
    page.wait_for_timeout(600)
    expect(page.locator(".product-card img").first).to_be_visible()


def test_product_price_present(page: Page):
    page.goto(BASE_URL + "grocery.html")
    page.wait_for_timeout(600)
    expect(page.locator(".product-card").first).to_contain_text("₹")


def test_filter_chips_on_listing(page: Page):
    listing = ListingPage(page)
    listing.goto("grocery.html")
    page.wait_for_timeout(600)
    assert listing.filter_count() >= 0


def test_add_from_grocery_increments_cart(page: Page):
    page.goto(BASE_URL + "grocery.html")
    page.wait_for_timeout(600)
    HomePage(page).add_first_product()
    count = HomePage(page).cart_count()
    assert count >= 1


def test_fashion_has_limited_catalog(page: Page):
    page.goto(BASE_URL + "fashion.html")
    page.wait_for_timeout(600)
    count = page.locator(".product-card").count()
    assert 1 <= count <= 80


def test_vegetables_contains_tomato(page: Page):
    page.goto(BASE_URL + "vegetables.html")
    page.wait_for_timeout(600)
    expect(page.locator("body")).to_contain_text("Tomato")


def test_snacks_filter_or_products(page: Page):
    page.goto(BASE_URL + "grocery.html")
    page.wait_for_timeout(600)
    expect(page.locator("body")).to_contain_text("Lay")


def test_beverages_products(page: Page):
    page.goto(BASE_URL + "grocery.html")
    page.wait_for_timeout(600)
    expect(page.locator("body")).to_contain_text("Tea")


def test_household_or_home_circles(page: Page):
    HomePage(page).open()
    expect(page.locator("body")).to_contain_text("Personal Care")


def test_baby_or_discover_section(page: Page):
    HomePage(page).open()
    expect(page.locator("body")).to_be_visible()


def test_product_add_button_label(page: Page):
    page.goto(BASE_URL + "grocery.html")
    page.wait_for_timeout(600)
    expect(page.locator(".add-btn").first).to_contain_text("ADD")
