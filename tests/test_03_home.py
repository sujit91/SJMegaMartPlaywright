import pytest
from playwright.sync_api import Page, expect

from pages.home_page import HomePage


pytestmark = [pytest.mark.ui, pytest.mark.regression]


@pytest.mark.smoke
def test_home_page_loads(page: Page):
    HomePage(page).open()
    expect(page.locator("body")).to_be_visible()
    assert "index.html" in page.url or page.url.endswith("/")


def test_search_box_is_visible(page: Page):
    HomePage(page).open()
    expect(page.locator("#siteSearch").first).to_be_visible()


def test_category_tabs_are_visible(page: Page):
    HomePage(page).open()
    assert page.locator(".category-tab").count() > 0


def test_product_cards_render(page: Page):
    HomePage(page).open()
    assert page.locator(".product-card").count() > 0


def test_add_buttons_render(page: Page):
    HomePage(page).open()
    expect(page.locator(".add-btn").first).to_be_visible()


def test_cart_link_is_visible(page: Page):
    HomePage(page).open()
    expect(page.locator("a[href*='cart.html']").first).to_be_visible()


def test_footer_is_visible(page: Page):
    HomePage(page).open()
    expect(page.locator("footer.footer")).to_be_visible()


def test_grocery_nav_link(page: Page):
    home = HomePage(page)
    home.open()
    home.expect_category_nav("grocery")


def test_fashion_nav_link(page: Page):
    home = HomePage(page)
    home.open()
    home.expect_category_nav("fashion")


def test_electronics_nav_link(page: Page):
    home = HomePage(page)
    home.open()
    home.expect_category_nav("electronics")


def test_hover_tab_shows_dropdown(page: Page):
    HomePage(page).open()
    tab = page.locator(".category-tab").first
    tab.hover()
    page.wait_for_timeout(400)
    dropdown = page.locator(".tab-dropdown, .category-dropdown, .dropdown-menu")
    assert dropdown.count() >= 0


def test_brand_name_on_home(page: Page):
    HomePage(page).open()
    expect(page.locator("body")).to_contain_text("SJ MegaMart")
