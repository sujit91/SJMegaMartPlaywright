from pages.home_page import HomePage


class ListingPage(HomePage):
    FILTER = ".filter-chip"
    TITLE = ".page-title, h1, .section-title"

    def open_filter(self, value: str) -> None:
        self.page.locator(f".filter-chip[data-filter='{value}']").first.click()
        self.page.wait_for_timeout(300)

    def filter_count(self) -> int:
        return self.page.locator(self.FILTER).count()
