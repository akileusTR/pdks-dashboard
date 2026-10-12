from flask import Flask, send_file
from playwright.sync_api import sync_playwright
import threading
import time
import json
import re

USERNAME = "emin.us"
PASSWORD = "Cs.17261726."

app = Flask(__name__)

def scrape_pdks():

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True
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
        ).get_by_text(
            "1",
            exact=True
        ).click()

        page.get_by_role(
            "button",
            name="Listele"
        ).click()

        page.wait_for_timeout(5000)

        text = page.locator(
            "body"
        ).inner_text()

        with open(
            "data/raw.txt",
            "w",
            encoding="utf-8"
        ) as f:

            f.write(text)

        browser.close()


def parse_pdks():

    with open(
        "data/raw.txt",
        "r",
        encoding="utf-8"
    ) as f:

        text = f.read()

    lines = [
        x.strip()
        for x in text.splitlines()
        if x.strip()
    ]

    days = []

    for i in range(len(lines)):

        if re.match(
            r"\d{2}\.\d{2}\.\d{4}",
            lines[i]
        ):

            try:

                date = lines[i]
                name = lines[i + 1]
                target = int(lines[i + 2])
                inside = int(lines[i + 3])

                days.append(
                    {
                        "date": date,
                        "name": name,
                        "target": target,
                        "inside": inside,
                        "difference": inside - target
                    }
                )

            except:
                pass

    result = {
        "days": days
    }

    with open(
        "data/latest.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            result,
            f,
            ensure_ascii=False,
            indent=2
        )


def refresh():

    print("PDKS güncelleniyor...")

    scrape_pdks()

    parse_pdks()

    print("PDKS güncellendi.")


def background_worker():

    while True:

        try:

            refresh()

        except Exception as e:

            print(
                "Hata:",
                e
            )

        time.sleep(
            900
        )  # 15 dakika


@app.route("/api/pdks")
def api_pdks():

    return send_file(
        "data/latest.json",
        mimetype="application/json"
    )


@app.route("/")
def home():

    return """
    <h1>PDKS Companion</h1>
    <p>JSON:</p>
    <a href="/api/pdks">PDKS Verisi</a>
    """


if __name__ == "__main__":

    worker = threading.Thread(
        target=background_worker,
        daemon=True
    )

    worker.start()

    app.run(
        host="0.0.0.0",
        port=5000
    )
