from playwright.sync_api import sync_playwright
import json

USERNAME = "emin.us"
PASSWORD = "Cs.17261726."

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    page = browser.new_page()

    page.goto(
        "https://canias.ulakhaberlesme.com.tr/CaniasWebClient/"
    )

    page.locator("#username").fill(USERNAME)

    page.locator("#password").fill(PASSWORD)

    page.get_by_role(
        "button",
        name="Oturumu Başlat"
    ).click()

    page.wait_for_timeout(5000)

    page.locator(
        '[id="ULAKYAŞAM_502__ULKYASAMYENI\x8cBASIC\x8fBTNAPPS14"]'
    ).click()

    page.wait_for_timeout(3000)

    page.locator(
        '[id="ULKT09_503__ULKT09D001\x8cBASIC\x8fTMPPERSONEL--0-_0"]'
    ).get_by_text("1", exact=True).click()

    page.get_by_role(
        "button",
        name="Listele"
    ).click()

    page.wait_for_timeout(5000)

    text = page.locator("body").inner_text()

    with open(
        "data/raw.txt",
        "w",
        encoding="utf-8"
    ) as f:
        f.write(text)

    print("raw.txt oluşturuldu.")

    browser.close()
