import pytest

def pytest_addoption(parser):
    parser.addoption(
        "--browser_name", action="store", default="chrome",
        help="Browser to run tests against: chrome or firefox"
    )

@pytest.fixture(scope="session")
def browserInstance(playwright, request):
    browser_name = request.config.getoption("browser_name")
    if browser_name == "chrome":
        browser = playwright.chromium.launch(headless=False)
    elif browser_name == "firefox":
        browser= playwright.firefox.launch(headless=False)
    else:
        raise ValueError(f"Unsupported browser:{browser_name}")

    yield browser
    browser.close()

def pytest_configure(config):
    config.option.base_url = "https://eventhub.rahulshettyacademy.com"


