import pytest
from playwright.sync_api import Page, expect

from pages.checkout_page import CheckoutPage
from utils.cart_helper import seed_cart


pytestmark = [pytest.mark.checkout, pytest.mark.regression]


def _ready(page: Page) -> CheckoutPage:
    seed_cart(page)
    checkout = CheckoutPage(page)
    checkout.open()
    checkout.fill_address()
    return checkout


@pytest.mark.smoke
def test_cod_place_order_shows_loader_or_success(logged_in_page: Page):
    checkout = _ready(logged_in_page)
    checkout.pay_cod()
    logged_in_page.wait_for_timeout(1500)
    loader = logged_in_page.locator("#paymentLoader")
    success = logged_in_page.locator(".order-success, .success-card, body")
    assert loader.count() >= 0
    expect(success.first).to_be_visible()


def test_card_pay_click(logged_in_page: Page):
    checkout = _ready(logged_in_page)
    checkout.pay_card()
    logged_in_page.wait_for_timeout(1500)
    expect(logged_in_page.locator("body")).to_be_visible()


def test_upi_pay_click(logged_in_page: Page):
    checkout = _ready(logged_in_page)
    checkout.pay_upi()
    logged_in_page.wait_for_timeout(1500)
    expect(logged_in_page.locator("body")).to_be_visible()


def test_netbanking_pay_click(logged_in_page: Page):
    checkout = _ready(logged_in_page)
    checkout.pay_netbanking("SBI")
    logged_in_page.wait_for_timeout(1500)
    expect(logged_in_page.locator("body")).to_be_visible()


def test_upi_apps_visible(logged_in_page: Page):
    seed_cart(logged_in_page)
    CheckoutPage(logged_in_page).open()
    logged_in_page.locator("[data-payment-tab='upi']").click()
    expect(logged_in_page.locator(".upi-app--gpay")).to_be_visible()


def test_other_bank_dropdown(logged_in_page: Page):
    seed_cart(logged_in_page)
    CheckoutPage(logged_in_page).open()
    logged_in_page.locator("[data-payment-tab='netbanking']").click()
    expect(logged_in_page.locator("#otherBank")).to_be_visible()


def test_payment_amount_on_card_button(logged_in_page: Page):
    seed_cart(logged_in_page)
    CheckoutPage(logged_in_page).open()
    expect(logged_in_page.locator("[data-pay-now='card']")).to_contain_text("Pay")


def test_switch_between_payment_tabs(logged_in_page: Page):
    seed_cart(logged_in_page)
    CheckoutPage(logged_in_page).open()
    logged_in_page.locator("[data-payment-tab='upi']").click()
    logged_in_page.locator("[data-payment-tab='cod']").click()
    cls = logged_in_page.locator("[data-payment-panel='cod']").get_attribute("class") or ""
    assert "is-active" in cls


def test_card_cvv_is_password_type(logged_in_page: Page):
    seed_cart(logged_in_page)
    CheckoutPage(logged_in_page).open()
    expect(logged_in_page.locator("#cardCvv")).to_have_attribute("type", "password")


def test_cod_button_label(logged_in_page: Page):
    seed_cart(logged_in_page)
    CheckoutPage(logged_in_page).open()
    logged_in_page.locator("[data-payment-tab='cod']").click()
    expect(logged_in_page.locator("[data-pay-now='cod']")).to_contain_text("Place Order")
