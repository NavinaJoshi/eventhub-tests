# # Playwright vs Test Runner (Python)
#
# - **playwright**: Core automation library (launch browsers, navigate, interact).
# - **pytest**: Python test runner (fixtures, assertions, reporting).
# → In Python, Playwright integrates with pytest instead of the JS @playwright/test runner.


from playwright.sync_api import expect


def test_eventhub_login_page_loads(page):
    page.goto("https://eventhub.rahulshettyacademy.com/login")
    expect(page.get_by_role("heading", name="Sign in to EventHub")).to_be_visible()
    expect(page.get_by_placeholder("you@email.com")).to_be_visible()
    expect(page.get_by_role("button", name="Sign In")).to_be_visible()


def test_eventhub_password_field_and_url(page):
    page.goto("https://eventhub.rahulshettyacademy.com/login")
    expect(page.get_by_label("Password")).to_be_visible()
    expect(page).to_have_url("https://eventhub.rahulshettyacademy.com/login")
    expect(page.get_by_role("heading", name="Sign in to EventHub")).to_be_visible()

