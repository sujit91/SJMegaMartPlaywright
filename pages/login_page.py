from playwright.sync_api import expect

from config.settings import DEMO_PASSWORD, DEMO_USER
from pages.base_page import BasePage


class LoginPage(BasePage):
    EMAIL = "#loginEmail"
    PASSWORD = "#loginPassword"
    SUBMIT = "#loginSubmitBtn"
    DEMO = "#demoAdminLoginBtn"
    ERROR = "#loginError, .form-error, .auth-error"
    AUTH_LABEL = ".auth-label"

    def open(self) -> None:
        self.goto("login.html")
        self.expect_visible(self.EMAIL)

    def login(self, email: str, password: str) -> None:
        self.fill(self.EMAIL, email)
        self.fill(self.PASSWORD, password)
        self.click(self.SUBMIT)

    def login_as_admin(self) -> None:
        if self.page.locator(self.DEMO).count():
            self.click(self.DEMO)
        else:
            self.login(DEMO_USER, DEMO_PASSWORD)
        self.page.wait_for_timeout(1200)

    def expect_logged_in(self, name: str = "Admin") -> None:
        expect(self.page.locator(self.AUTH_LABEL).first).to_contain_text(name, timeout=self.timeout)

    def expect_login_visible(self) -> None:
        expect(self.page.locator(self.AUTH_LABEL).first).to_contain_text("Login", timeout=self.timeout)
