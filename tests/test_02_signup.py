import pytest
from playwright.sync_api import Page, expect

from pages.signup_page import SignupPage


pytestmark = [pytest.mark.auth, pytest.mark.regression]


@pytest.mark.smoke
def test_signup_page_loads(page: Page):
    SignupPage(page).open()
    expect(page.locator("#signupHeading")).to_contain_text("Create Account")


def test_mandatory_name_field(page: Page):
    SignupPage(page).open()
    expect(page.locator("#signupName")).to_be_visible()


def test_mandatory_email_field(page: Page):
    SignupPage(page).open()
    expect(page.locator("#signupEmail")).to_be_visible()


def test_mandatory_phone_field(page: Page):
    SignupPage(page).open()
    expect(page.locator("#signupPhone")).to_be_visible()


def test_mandatory_password_fields(page: Page):
    SignupPage(page).open()
    expect(page.locator("#signupPassword")).to_be_visible()
    expect(page.locator("#signupConfirmPassword")).to_be_visible()


def test_registration_help_is_shown(page: Page):
    SignupPage(page).open()
    expect(page.locator(".auth-help")).to_contain_text("How to register")


def test_empty_submit_stays_on_signup(page: Page):
    SignupPage(page).open()
    page.locator("#signupSubmitBtn").click()
    assert "signup.html" in page.url


def test_invalid_email_does_not_leave_signup(page: Page):
    signup = SignupPage(page)
    signup.open()
    signup.submit("QA User", "not-an-email", "Automation@123")
    page.wait_for_timeout(800)
    assert "signup.html" in page.url


def test_short_password_stays_on_signup(page: Page):
    signup = SignupPage(page)
    signup.open()
    signup.submit("QA User", "qa.user@example.com", "123", "9876543210")
    page.wait_for_timeout(800)
    assert "signup.html" in page.url


def test_phone_max_length_is_ten(page: Page):
    SignupPage(page).open()
    expect(page.locator("#signupPhone")).to_have_attribute("maxlength", "10")


def test_login_switch_link(page: Page):
    SignupPage(page).open()
    expect(
        page.locator("p").filter(has_text="Already have an account?").get_by_role("link", name="Login")
    ).to_be_visible()


def test_google_signup_button(page: Page):
    SignupPage(page).open()
    expect(page.locator("#googleSignupBtn")).to_be_visible()
