from selenium import webdriver
import logging

logger = logging.getLogger(__name__)


# Local wrapper for AWS synthetics_webdriver
# Delegates interactions to Selenium WebDriver Chrome
class LocalSyntheticsWebdriver:
    @staticmethod
    def get_http_response(url):
        """
        Get response code from http request to url
        """
        import urllib.request as http_client

        request = http_client.Request(url, headers={"User-Agent": "Chrome"})
        response_code = ""
        try:
            with http_client.urlopen(request) as response:
                response_code = response.code
        except Exception as ex:
            logger.error(ex)
            response_code = "error"
        finally:
            return response_code

    @staticmethod
    def Chrome(chrome_options=None):
        return webdriver.Chrome(options=chrome_options)


synthetics_webdriver = LocalSyntheticsWebdriver()
