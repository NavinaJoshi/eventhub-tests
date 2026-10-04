import re

from playwright.sync_api import Page, expect

BASE = "https://eventhub.rahulshettyacademy.com"


def login(page: Page):
    page.goto(BASE)
    page.get_by_placeholder("you@email.com").fill("navijoshi@gmail.com")
    page.locator("input[type='password']").fill("Qwerty@03")
    page.get_by_role("button", name="Sign In").click()
    page.get_by_role("link", name="Browse Events").nth(1).click()
    expect(page.get_by_role("heading", name="Upcoming Events")).to_be_visible()


def get_event_card(page, title):
    return page.get_by_role("article").filter(has=page.get_by_role("heading", name=title))


def read_confirmation(page: Page):
    expect(page.get_by_role("heading", name="Booking Confirmed! 🎉")).to_be_visible(timeout=10000)
    ref = page.get_by_text("Booking Ref", exact=True).locator("xpath=following-sibling::*[1]").inner_text().strip()
    total = page.get_by_text("Total", exact=True).locator("xpath=following-sibling::*[1]").inner_text().strip()
    return ref, total


def booking_card(page: Page, ref: str):
    # Innermost element containing BOTH the reference and the View Details control.
    # Works whether the card is an article, div or li. Found by reference, not index.
    return (
        page.locator("article, li, div")
        .filter(has_text=ref)
        .filter(has=page.get_by_text("View Details", exact=True))
        .last
    )


def check_card(page: Page, b: dict):
    card = booking_card(page, b["reference"])
    expect(card).to_be_visible(timeout=10000)
    expect(card).to_contain_text(re.compile("confirmed", re.I))
    expect(card).to_contain_text(b["title"])
    expect(card).to_contain_text(re.compile(rf"\b{b['tickets']}\s*ticket", re.I))
    expect(card).to_contain_text(b["total"])


def open_and_check_detail(page: Page, b: dict, other: dict):
    card = booking_card(page, b["reference"])
    card.get_by_text("View Details", exact=True).click()
    # SPA route change: wait for the URL, not a navigation event (also proves numeric id)
    expect(page).to_have_url(re.compile(r"/bookings/\d+"), timeout=10000)

    body = page.locator("main")
    expect(body).to_contain_text(b["reference"], timeout=10000)
    expect(page.get_by_role("heading", name=b["title"])).to_be_visible()
    expect(body).to_contain_text(b["email"])
    expect(body).to_contain_text(b["total"])
    expect(body).to_contain_text(re.compile(rf"Tickets\s*{b['tickets']}(?!\d)"))
    # No cross-booking mix-up
    expect(body).not_to_contain_text(other["reference"])
    expect(body).not_to_contain_text(other["title"])


def test_multi_booking_history(page: Page):
    login(page)

    # ---- Booking 1: Conference / Hyderabad / "World" / qty 1 ----
    page.get_by_placeholder("Search events").fill("World")
    page.get_by_role("combobox").nth(0).select_option("Conference")
    page.get_by_role("combobox").nth(1).select_option("Hyderabad")
    page.wait_for_load_state("networkidle")
    summit_card = get_event_card(page, "World Tech Summit")
    expect(summit_card).to_be_visible(timeout=10000)
    summit_card.get_by_role("link", name="Book Now").click()
    expect(page).to_have_url(re.compile(r"/events/\d+"), timeout=10000)
    expect(page.get_by_role("heading", name="Book Tickets")).to_be_visible(timeout=10000)
    page.get_by_placeholder("Your full name").fill("Navina Joshi")
    page.get_by_placeholder("you@email.com").fill("navijoshi@gmail.com")
    page.get_by_placeholder("+91 98765 43210").fill("+91 9876543210")
    page.get_by_role("button", name="Confirm Booking").click()
    ref1, total1 = read_confirmation(page)
    booking1 = {"reference": ref1, "title": "World Tech Summit", "tickets": "1",
                "total": total1, "email": "navijoshi@gmail.com"}
    assert booking1["reference"]

    # ---- Booking 2: Festival / Delhi / "Dilli" / qty 2 ----
    page.goto(f"{BASE}/events")
    page.get_by_placeholder("Search events").fill("Dilli")
    page.get_by_role("combobox").nth(0).select_option("Festival")
    page.get_by_role("combobox").nth(1).select_option("Delhi")
    page.wait_for_load_state("networkidle")
    festival_card = get_event_card(page, "Dilli Diwali Mela")
    expect(festival_card).to_be_visible(timeout=10000)
    festival_card.get_by_role("link", name="Book Now").click()
    expect(page).to_have_url(re.compile(r"/events/\d+"), timeout=10000)
    expect(page.get_by_role("heading", name="Book Tickets")).to_be_visible(timeout=10000)
    page.get_by_placeholder("Your full name").fill("Ravi Kumar")
    page.get_by_placeholder("you@email.com").fill("ravikumar@gmail.com")
    page.get_by_placeholder("+91 98765 43210").fill("+91 9123456789")
    page.get_by_role("button", name="+").click()
    page.get_by_role("button", name="Confirm Booking").click()
    ref2, total2 = read_confirmation(page)
    booking2 = {"reference": ref2, "title": "Dilli Diwali Mela", "tickets": "2",
                "total": total2, "email": "ravikumar@gmail.com"}

    assert booking1["reference"] != booking2["reference"]
    assert booking1["title"] != booking2["title"]

    # ---- My Bookings: find both cards by reference, verify ----
    page.goto(f"{BASE}/bookings")
    check_card(page, booking1)
    check_card(page, booking2)

    # ---- Detail page of booking 1 ----
    open_and_check_detail(page, booking1, booking2)

    # ---- Back to My Bookings, re-find booking 2, detail page ----
    page.goto(f"{BASE}/bookings")
    check_card(page, booking2)
    open_and_check_detail(page, booking2, booking1)