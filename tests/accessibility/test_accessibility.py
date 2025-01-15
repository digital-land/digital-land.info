from axe_playwright_python.sync_playwright import Axe
from playwright.sync_api import sync_playwright

axe = Axe()


def accessibility_test(page_url, pause_for_scripts_time=0):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        page.goto(page_url)
        page.wait_for_timeout(pause_for_scripts_time)
        results = axe.run(page)
        browser.close()

        print(f"Found {results.violations_count} violations for the page: {page_url}.")
        print(results.generate_report())

        assert results.violations_count == 0


def test_accessibility_of_homepage(server_url):
    accessibility_test(server_url)


def test_accessibility_of_about_page(server_url):
    accessibility_test(server_url + "/about")


def test_accessibility_of_dataset_index_page(server_url):
    accessibility_test(server_url + "/dataset")


def test_accessibility_of_dataset_page(server_url):
    accessibility_test(server_url + "/dataset/brownfield-site")


def test_accessibility_of_the_search_page(server_url):
    accessibility_test(server_url + "/entity", 1000)


def test_accessibility_of_the_entity_page(server_url):
    accessibility_test(server_url + "/entity/2")


def test_accessibility_of_the_map_page(server_url):
    accessibility_test(server_url + "/map")


def test_accessibility_of_the_docs_page(server_url):
    accessibility_test(server_url + "/docs")


def test_accessibility_of_the_guidance_index_page(server_url):
    accessibility_test(server_url + "/guidance/")


def test_accessibility_of_the_guidance_intro_page(server_url):
    accessibility_test(server_url + "/guidance/introduction")


def test_accessibility_of_the_guidance_how_to_provide_data_page(server_url):
    accessibility_test(server_url + "/guidance/how-to-provide-data")


def test_accessibility_of_the_guidance_specifications_page(server_url):
    accessibility_test(server_url + "/guidance/specifications")


def test_accessibility_of_the_service_status_page(server_url):
    accessibility_test(server_url + "/service-status")


def test_accessibility_of_the_roadmap_page(server_url):
    accessibility_test(server_url + "/about/roadmap")


def test_accessibility_of_the_accessibility_statement_page(server_url):
    accessibility_test(server_url + "/accessibility-statement")

def test_accessibility_of_the_accessibility_statement_page(server_url):
    accessibility_test(server_url + "/terms-and-conditions")
