def test_login_page_fixture(page):
    page.goto("/login")
    assert "EventHub" in page.title()
    assert page.get_by_placeholder("you@email.com").is_visible()
    assert page.get_by_role("button", name="Sign In").is_visible()

def test_email_field_and_isolated_context(page, browserInstance):
    page.goto("/login")
    email_field = page.get_by_placeholder("you@email.com")
    email_field.fill("beginner@sample.com")
    assert email_field.input_value() == "beginner@sample.com"

    context = browserInstance.new_context()
    isolated_page = context.new_page()
    isolated_page.goto("https://eventhub.rahulshettyacademy.com/login")
    assert isolated_page.get_by_role("heading", name="Sign in to EventHub").is_visible()
    assert isolated_page.get_by_placeholder("you@email.com").input_value() == ""
    context.close()
