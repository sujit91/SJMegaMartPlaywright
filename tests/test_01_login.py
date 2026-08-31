import pytest
from playwright.sync_api import Page, expect

from config.settings import DEMO_PASSWORD, DEMO_USER
from pages.login_page import LoginPage


pytestmark = [pytest.mark.auth, pytest.mark.regression]


@pytest.mark.smoke
def test_login_page_loads(page: Page):
    login = LoginPage(page)
    login.open()
    assert "Login" in page.title()


def test_email_field_is_visible(page: Page):
    LoginPage(page).open()
    expect(page.locator("#loginEmail")).to_be_visible()


def test_password_field_is_visible(page: Page):
    LoginPage(page).open()
    expect(page.locator("#loginPassword")).to_be_visible()


def test_demo_admin_button_is_visible(page: Page):
    LoginPage(page).open()
    expect(page.locator("#demoAdminLoginBtn")).to_be_visible()


def test_help_mentions_demo_credentials(page: Page):
    LoginPage(page).open()
    expect(page.locator(".auth-help")).to_contain_text("admin")


@pytest.mark.smoke
def test_demo_admin_login_shows_admin_in_header(page: Page):
    login = LoginPage(page)
    login.open()
    login.login_as_admin()
    login.expect_logged_in("Admin")


def test_typed_admin_credentials_login(page: Page):
    login = LoginPage(page)
    login.open()
    login.login(DEMO_USER, DEMO_PASSWORD)
    page.wait_for_timeout(1500)
    expect(page.locator(".auth-label").first).to_contain_text("Admin")


def test_invalid_credentials_show_error_or_stay(page: Page):
    login = LoginPage(page)
    login.open()
    login.login("wrong@example.com", "BadPass@123")
    page.wait_for_timeout(1500)
    error = page.locator("#loginError")
    still_login = "login.html" in page.url
    assert still_login or error.is_visible()


def test_empty_submit_stays_on_login(page: Page):
    LoginPage(page).open()
    page.locator("#loginSubmitBtn").click()
    assert "login.html" in page.url


def test_signup_link_is_present(page: Page):
    LoginPage(page).open()
    expect(page.locator("a[href='signup.html']")).to_be_visible()


def test_forgot_password_is_present(page: Page):
    LoginPage(page).open()
    expect(page.locator("#forgotPasswordLink")).to_be_visible()


def test_google_login_button_is_present(page: Page):
    LoginPage(page).open()
    expect(page.locator("#googleLoginBtn")).to_be_visible()


def test_brand_link_goes_home(page: Page):
    LoginPage(page).open()
    page.locator("a.auth-brand").click()
    page.wait_for_timeout(800)
    assert "signup.html" not in page.url


def test_password_toggle_exists(page: Page):
    LoginPage(page).open()
    expect(page.locator("[data-password-toggle='loginPassword']")).to_be_visible()


def test_login_heading_text(page: Page):
    LoginPage(page).open()
    expect(page.locator("#loginHeading")).to_contain_text("Welcome Back")
