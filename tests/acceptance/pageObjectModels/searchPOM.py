import re


class SearchPOM:
    def __init__(self, page, base_url) -> None:
        self.page = page
        self.base_url = base_url
        self.path = "/entity/"

    def navigate(self, urlParam=""):
        with self.page.expect_navigation() as navigation_info:
            response = self.page.goto(self.base_url + self.path + urlParam)
        assert navigation_info.value.ok
        return response

    def test_count_of_results(self, count):
        locator = self.page.get_by_role("heading", name=re.compile(r"\d+ result[s]?"))
        assert locator.count() == 1
        foundCount = int(locator.text_content().split(" ")[0])
        assert foundCount == count
        resultsList = self.page.locator("ul.app-results-list").locator(
            "li.app-results-list__item"
        )
        assert resultsList.count() == min(count, 10)

    def find_checkbox(self, filter, typology):
        checkbox = self.page.get_by_label(typology, exact=True)
        if not checkbox.is_visible():
            self.page.locator("summary").filter(has_text=filter).get_by_role(
                "img"
            ).click()
            checkbox = self.page.get_by_label(typology, exact=True)

        assert checkbox.is_visible(), f"couldn't find {filter} checkbox"
        return checkbox

    def check_filter(self, filter, checkbox):
        checkbox = self.find_checkbox(filter, checkbox)
        if not checkbox.is_checked():
            checkbox.click()

    def uncheck_filter(self, filter, checkbox):
        checkbox = self.find_checkbox(filter, checkbox)
        if not checkbox.is_checked():
            checkbox.click()

    def filter_by_entry_date(self, beforeOrAfter, year, month, day):
        if beforeOrAfter == "before":
            self.page.get_by_label("Before").check()
        elif beforeOrAfter == "after":
            self.page.get_by_label("Since").check()
        else:
            Exception("beforeOrAfter must be either 'before' or 'after'")

        self.page.get_by_label("Day").fill(day)
        self.page.get_by_label("Month").fill(month)
        self.page.get_by_label("Year").fill(year)

    def search_button_click(self):
        with self.page.expect_navigation() as navigation_info:
            self.page.get_by_role("button", name="Search").click()
        assert navigation_info.value.ok

    def clear_filter(self, filter):
        self.page.get_by_role("link", name=filter).click()
