import requests

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def get_datasette_http():
    """
    Function to return  http for the use of querying  datasette,
    specifically to add retries for larger queries
    """
    retry_strategy = Retry(
        total=3, status_forcelist=[400], method_whitelist=["GET"], backoff_factor=0
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)

    http = requests.Session()
    http.mount("https://", adapter)
    http.mount("http://", adapter)

    return http
