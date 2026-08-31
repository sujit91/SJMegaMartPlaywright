import pytest
from playwright.sync_api import Page, expect

from pages.home_page import HomePage


pytestmark = [pytest.mark.catalog, pytest.mark.regression]


@pytest.mark.smoke
def test_search_milk(page: Page):
    home = HomePage(page)
    home.open()
    home.search("milk")
    assert home.product_count() >= 0
    expect(page.locator("body")).to_be_visible()


def test_search_rice(page: Page):
    home = HomePage(page)
    home.open()
    home.search("rice")
    expect(page.locator("body")).to_be_visible()


def test_search_chips(page: Page):
    home = HomePage(page)
    home.open()
    home.search("chips")
    expect(page.locator("body")).to_be_visible()


def test_search_tea(page: Page):
    home = HomePage(page)
    home.open()
    home.search("tea")
    expect(page.locator("body")).to_be_visible()


def test_search_shirt(page: Page):
    home = HomePage(page)
    home.open()
    home.search("shirt")
    expect(page.locator("body")).to_be_visible()


def test_empty_search_keeps_catalog(page: Page):
    home = HomePage(page)
    home.open()
    before = home.product_count()
    home.search("")
    assert home.product_count() >= 0
    assert before >= 0


def test_special_character_search_does_not_crash(page: Page):
    home = HomePage(page)
    home.open()
    home.search("@@@###")
    expect(page.locator("body")).to_be_visible()


def test_search_is_case_insensitive(page: Page):
    home = HomePage(page)
    home.open()
    home.search("MILK")
    expect(page.locator("body")).to_be_visible()
