import re

from playwright.sync_api import Page, expect


def login(page: Page):
    page.goto("https://eventhub.rahulshettyacademy.com/login")
    page.get_by_placeholder("you@email.com").fill("navijoshi@gmail.com")
    page.locator("input[type='password']").fill("Qwerty@03")
    page.get_by_role("button", name="Sign In").click()
    page.get_by_role("link", name="Browse Events").nth(1).click()
    expect(page.get_by_role("heading", name="Upcoming Events")).to_be_visible()

def get_event_card(page, title):
    return page.get_by_role("article").filter(has=page.get_by_role("heading", name=title))

def test_event_filters_and_detail(page: Page):
    # start from a logged‑in state
    login(page)

    # Filters
    page.get_by_placeholder("Search events").fill("World")
    page.get_by_role("combobox").nth(0).select_option("Conference")
    page.get_by_role("combobox").nth(1).select_option("Hyderabad")

    summit_card = get_event_card(page, "World Tech Summit")
    expect(summit_card).to_be_visible(timeout=10000)

    # Extract details
    title = summit_card.get_by_role("heading").inner_text()
    price_text = summit_card.locator("p").nth(0).inner_text()
    seats_text = summit_card.get_by_text("seats available").inner_text()

    assert title == "World Tech Summit"
    assert "$" in price_text
    assert int(seats_text.split()[0]) > 0

    # Book Now → same tab navigation
    with page.expect_navigation(url=re.compile(r".*/events.*")):
        summit_card.get_by_role("link", name="Book Now").click()

    # Verify detail page
    expect(page).to_have_url(re.compile(r"/events.*"))
    expect(page.get_by_role("heading", name=title)).to_have_text(title)
    expect(page.get_by_text(price_text, exact=True)).to_be_visible()

    # Back to Events list
    page.get_by_role("link", name="Browse Events", exact=True).click()
    page.get_by_role("combobox").nth(0).select_option("")  # clear category
    page.get_by_role("combobox").nth(1).select_option("")  # clear city
    cards = page.locator("[data-testid='event-card']")
    expect(cards.first).to_be_visible(timeout=10000)
    assert cards.count() >= 3

    first_title = cards.nth(0).get_by_role("heading").inner_text()
    second_title = cards.nth(1).get_by_role("heading").inner_text()
    last_title = cards.last.get_by_role("heading").inner_text()

    assert first_title and second_title and last_title
    assert first_title != last_title
