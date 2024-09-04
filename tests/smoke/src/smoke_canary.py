import asyncio
import os
import json

from datetime import datetime

from aws_synthetics.selenium import synthetics_webdriver as syn_webdriver
from aws_synthetics.common import synthetics_logger as logger, CanaryStatus
from faker import Faker

faker = Faker()

# www.development.digital - land.info
# https: // www.development.digital - land.info /
# www.development.digital - land.info
# https: // www.development.digital - land.info / dataset /
# www.development.digital - land.info
# https: // www.development.digital - land.info / entity /
# www.development.digital - land.info
# https: // www.development.digital - land.info / map /
# www.development.digital - land.info
# https: // www.development.digital - land.info / docs
# Entity
# API
# Checkfrom aws_synthetics.selenium import synthetics_webdriver as syn_webdriver
# from aws_synthetics.common import synthetics_logger as logger
# from faker import Faker
#
# faker = Faker()
#
# # www.development.digital - land.info
# # https: // www.development.digital - land.info /
# # www.development.digital - land.info
# # https: // www.development.digital - land.info / dataset /
# # www.development.digital - land.info
# # https: // www.development.digital - land.info / entity /
# # www.development.digital - land.info
# # https: // www.development.digital - land.info / map /
# # www.development.digital - land.info
# # https: // www.development.digital - land.info / docs
# # Entity
# # API
# # Check
# # https: // www.development.digital - land.info / entity.json?limit = 10
# # Dataset
# # API
# # Check
# # https: // www.development.digital - land.info / dataset.json
#
#
# def main():
#     logger.info("UUID: " + faker.uuid4())
#     url = "https://planning.data.gov.uk/"
#     browser = syn_webdriver.Chrome()
#     browser.get(url)
#     browser.save_screenshot("loaded.png")
#
#     response_code = syn_webdriver.get_http_response(url)
#     if not response_code or response_code < 200 or response_code > 299:
#         raise Exception("Failed to load page!")
#
#     logger.info("Canary successfully executed.")
#
#
# def visit_and_screenshot(browser, url):
#     browser = syn_webdriver.Chrome()
#     browser.get(url)
#     browser.save_screenshot("loaded.png")
#     response_code = syn_webdriver.get_http_response(url)
#     if not response_code or response_code < 200 or response_code > 299:
#         raise Exception("Failed to load page!")
#
#
# def handler(event, context):
#     return main()
# https: // www.development.digital - land.info / entity.json?limit = 10
# Dataset
# API
# Check
# https: // www.development.digital - land.info / dataset.json


async def main(event, context):
    canary_result = CanaryStatus.NO_RESULT.value
    canary_error = None
    start_time = None
    reset_time = None
    setup_time = None
    launch_time = None
    await syn_webdriver.before_canary()
    launch_time = datetime.now()
    launch_time = (datetime.now() - launch_time).total_seconds() * 1000

    logger.info("UUID: " + faker.uuid4())
    base_url = os.environ.get("BASE_URL")
    url = base_url
    browser = syn_webdriver.Chrome()
    browser.get(url)
    browser.save_screenshot("loaded.png")

    response_code = syn_webdriver.get_http_response(url)
    if not response_code or response_code < 200 or response_code > 299:
        logger.error(
            "Failed to load page, did not get expected code: " + str(response_code)
        )
        raise Exception("Failed to load page!")

    end_time = datetime.now()
    logger.info("Canary successfully executed.")
    return_value = await syn_webdriver.after_canary(
        canary_result,
        canary_error,
        start_time,
        end_time,
        reset_time,
        setup_time,
        launch_time,
    )
    return json.dumps(return_value)


def visit_and_screenshot(browser, url):
    browser = syn_webdriver.Chrome()
    browser.get(url)
    browser.save_screenshot("loaded.png")
    response_code = syn_webdriver.get_http_response(url)
    if not response_code or response_code < 200 or response_code > 299:
        raise Exception("Failed to load page!")


# def handler(event, context):
#     return main()


def handler(event, context):
    return asyncio.run(main(event, context))
