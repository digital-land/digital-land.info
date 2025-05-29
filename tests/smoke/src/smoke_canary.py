import os
import time

from aws_synthetics.selenium import synthetics_webdriver as syn_webdriver
from aws_synthetics.common import synthetics_logger as logger

screenshot_dir = os.environ.get("SCREENSHOT_DIR", "screenshots")


def main():
    # Test comment to ensure CI/CD is working via GHA
    base_url = os.environ.get("BASE_URL")
    browser = syn_webdriver.Chrome()

    paths = ["/", "/about", "/dataset", "/entity", "/map", "/docs"]
    for path in paths:
        visit_and_screenshot(browser, base_url, path)

    logger.info("Canary successfully executed.")


def visit_and_screenshot(browser, base_url, path):
    url = base_url + path
    browser.get(url)
    path_string = path_to_string(path)
    time_string = time.strftime("%Y-%m-%d_%H-%M-%S")
    browser.save_screenshot(f"{screenshot_dir}/{path_string}-{time_string}.png")
    response_code = syn_webdriver.get_http_response(url)
    if not response_code or response_code < 200 or response_code > 299:
        raise Exception("Failed to load page!")


def path_to_string(path):
    if path == "/":
        return "root"
    else:
        return path


def handler(event, context):
    return main()
