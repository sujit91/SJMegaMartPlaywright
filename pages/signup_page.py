from pages.base_page import BasePage


class SignupPage(BasePage):
    NAME = "#signupName"
    EMAIL = "#signupEmail"
    PHONE = "#signupPhone"
    PASSWORD = "#signupPassword"
    CONFIRM = "#signupConfirmPassword"
    SUBMIT = "#signupSubmitBtn"
    HELP = ".auth-help"
    ERROR = "#signupError"

    def open(self) -> None:
        self.goto("signup.html")
        self.expect_visible(self.NAME)

    def submit(self, name: str, email: str, password: str, phone: str = "9876543210") -> None:
        self.fill(self.NAME, name)
        self.fill(self.EMAIL, email)
        self.fill(self.PHONE, phone)
        self.fill(self.PASSWORD, password)
        self.fill(self.CONFIRM, password)
        self.click(self.SUBMIT)
