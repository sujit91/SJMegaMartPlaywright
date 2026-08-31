import pytest
from playwright.sync_api import Page

from config.settings import BASE_URL, HEADLESS
from pages.login_page import LoginPage

pytest_plugins = ["utils.reporting"]


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    return {
        **browser_type_launch_args,
        "headless": HEADLESS,
    }


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "base_url": BASE_URL,
        "viewport": {"width": 1440, "height": 900},
        "ignore_https_errors": True,
    }


@pytest.fixture
def logged_in_page(page: Page) -> Page:
    login = LoginPage(page)
    login.open()
    login.login_as_admin()
    login.expect_logged_in("Admin")
    return page
