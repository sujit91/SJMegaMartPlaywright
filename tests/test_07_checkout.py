import pytest
from playwright.sync_api import Page, expect

from config.settings import BASE_URL
from pages.checkout_page import CheckoutPage
from utils.cart_helper import clear_cart, seed_cart


pytestmark = [pytest.mark.checkout, pytest.mark.regression]


def test_empty_checkout_shows_message(page: Page):
    clear_cart(page)
    CheckoutPage(page).open()
    expect(page.locator("#checkoutContent, body")).to_contain_text("Add")


@pytest.mark.smoke
def test_checkout_address_fields_when_cart_has_items(logged_in_page: Page):
    seed_cart(logged_in_page)
    checkout = CheckoutPage(logged_in_page)
    checkout.open()
    expect(logged_in_page.locator("#fullName")).to_be_visible()


def test_phone_field_on_checkout(logged_in_page: Page):
    seed_cart(logged_in_page)
    CheckoutPage(logged_in_page).open()
    expect(logged_in_page.locator("#phoneNumber")).to_be_visible()


def test_address_line_on_checkout(logged_in_page: Page):
    seed_cart(logged_in_page)
    CheckoutPage(logged_in_page).open()
    expect(logged_in_page.locator("#addressLine")).to_be_visible()


def test_city_state_pin_fields(logged_in_page: Page):
    seed_cart(logged_in_page)
    CheckoutPage(logged_in_page).open()
    expect(logged_in_page.locator("#city")).to_be_visible()
    expect(logged_in_page.locator("#state")).to_be_visible()
    expect(logged_in_page.locator("#pinCode")).to_be_visible()


def test_save_address_button(logged_in_page: Page):
    seed_cart(logged_in_page)
    CheckoutPage(logged_in_page).open()
    expect(logged_in_page.locator("#saveAddressBtn")).to_be_visible()


def test_fill_and_save_address(logged_in_page: Page):
    seed_cart(logged_in_page)
    checkout = CheckoutPage(logged_in_page)
    checkout.open()
    checkout.fill_address()
    checkout.save_address()
    logged_in_page.wait_for_timeout(500)
    expect(logged_in_page.locator("#fullName")).to_have_value("Sujit Jena")


def test_card_payment_tab(logged_in_page: Page):
    seed_cart(logged_in_page)
    CheckoutPage(logged_in_page).open()
    expect(logged_in_page.locator("[data-payment-tab='card']")).to_be_visible()


def test_upi_payment_tab(logged_in_page: Page):
    seed_cart(logged_in_page)
    CheckoutPage(logged_in_page).open()
    logged_in_page.locator("[data-payment-tab='upi']").click()
    expect(logged_in_page.locator("#upiId")).to_be_visible()


def test_netbanking_tab_shows_banks(logged_in_page: Page):
    seed_cart(logged_in_page)
    CheckoutPage(logged_in_page).open()
    logged_in_page.locator("[data-payment-tab='netbanking']").click()
    expect(logged_in_page.locator("[data-bank='HDFC']")).to_be_visible()


def test_cod_tab(logged_in_page: Page):
    seed_cart(logged_in_page)
    CheckoutPage(logged_in_page).open()
    logged_in_page.locator("[data-payment-tab='cod']").click()
    expect(logged_in_page.locator("[data-pay-now='cod']")).to_be_visible()


def test_card_number_field(logged_in_page: Page):
    seed_cart(logged_in_page)
    CheckoutPage(logged_in_page).open()
    expect(logged_in_page.locator("#cardNumber")).to_be_visible()


def test_detect_location_button(logged_in_page: Page):
    seed_cart(logged_in_page)
    CheckoutPage(logged_in_page).open()
    expect(logged_in_page.locator(".detect-location-btn")).to_be_visible()


def test_checkout_map_placeholder(logged_in_page: Page):
    seed_cart(logged_in_page)
    CheckoutPage(logged_in_page).open()
    expect(logged_in_page.locator("#checkoutMap")).to_be_visible()


def test_checkout_page_url(page: Page):
    page.goto(BASE_URL + "checkout.html")
    assert "checkout.html" in page.url
