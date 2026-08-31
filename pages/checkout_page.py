from typing import Optional

from config.test_data import ADDRESS, CARD, UPI
from pages.base_page import BasePage


class CheckoutPage(BasePage):
    CONTENT = "#checkoutContent"
    NAME = "#fullName"
    PHONE = "#phoneNumber"
    LINE = "#addressLine"
    CITY = "#city"
    STATE = "#state"
    PIN = "#pinCode"
    SAVE = "#saveAddressBtn"
    CARD_NUMBER = "#cardNumber"
    CARD_HOLDER = "#cardHolder"
    CARD_EXPIRY = "#cardExpiry"
    CARD_CVV = "#cardCvv"
    UPI_ID = "#upiId"
    OTHER_BANK = "#otherBank"
    LOADER = "#paymentLoader"
    SUCCESS = ".order-success, .success-card"

    def open(self) -> None:
        self.goto("checkout.html")
        self.page.wait_for_timeout(600)

    def fill_address(self, data: Optional[dict] = None) -> None:
        data = data or ADDRESS
        self.page.wait_for_selector(self.NAME)
        self.fill(self.NAME, data["full_name"])
        self.fill(self.PHONE, data["phone"])
        self.fill(self.LINE, data["line"])
        self.fill(self.CITY, data["city"])
        self.fill(self.STATE, data["state"])
        self.fill(self.PIN, data["pin"])

    def save_address(self) -> None:
        self.click(self.SAVE)

    def select_payment_tab(self, method: str) -> None:
        self.page.locator(f"[data-payment-tab='{method}']").click()

    def pay_card(self) -> None:
        self.select_payment_tab("card")
        self.fill(self.CARD_NUMBER, CARD["number"])
        self.fill(self.CARD_HOLDER, CARD["holder"])
        self.fill(self.CARD_EXPIRY, CARD["expiry"])
        self.fill(self.CARD_CVV, CARD["cvv"])
        self.page.locator("[data-pay-now='card']").click()

    def pay_upi(self) -> None:
        self.select_payment_tab("upi")
        self.fill(self.UPI_ID, UPI)
        self.page.locator("[data-pay-now='upi']").click()

    def pay_netbanking(self, bank: str = "HDFC") -> None:
        self.select_payment_tab("netbanking")
        self.page.locator(f"[data-bank='{bank}']").click()
        self.page.locator("[data-pay-now='netbanking']").click()

    def pay_cod(self) -> None:
        self.select_payment_tab("cod")
        self.page.locator("[data-pay-now='cod']").click()
