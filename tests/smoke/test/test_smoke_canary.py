import os

from smoke_canary import main


def test_smoke_canary_main():
    os.environ["BASE_URL"] = os.environ.get(
        "SMOKE_TEST_BASE_URL", "https://planning.data.gov.uk"
    )
    main()
