from flask import Flask, send_file
from playwright.sync_api import sync_playwright
import threading
import time
import json
import re
import os
from datetime import datetime

USERNAME = "emin.us"
PASSWORD = "Cs.17261726."

app = Flask(__name__)

def scrape_pdks():

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False #True
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

        try:

            print("Popup kontrol ediliyor...")

            page.locator("text=Bu sunucuya zaten bağlısınız").wait_for(
                timeout=5000
            )

            print("Popup bulundu.")

            page.get_by_text(
                "OK",
                exact=True
            ).click(
                timeout=5000
            )

            print("Popup kapatıldı.")

            page.wait_for_timeout(5000)
           
            print(page.locator("body").inner_text())

        except Exception as e:

            print("Popup yok veya kapatılamadı:", e)

        page.screenshot(
            path="screenshots/after_popup.png"
        )

        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)
        
        page.screenshot(
            path="screenshots/home.png"
        ) 

        page.locator(
            '[id="ULAKYAŞAM_502__ULKYASAMYENI\x8cBASIC\x8fBTNAPPS14"]'
        ).click(timeout=60000)

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
        "lastUpdate": datetime.now().strftime(
            "%d.%m.%Y %H:%M"
        ),
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

    if not os.path.exists(
     "data/latest.json"
    ):
        return """
        <h2>PDKS Companion</h2>
        <p>Henüz veri oluşturulmadı.</p>
        """
        
    with open(
        "data/latest.json",
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    days = data["days"]

    today = days[-1]
    
    last_update = data.get(
        "lastUpdate",
        "Henüz güncellenmedi"
    )

    total_target = sum(
        x["target"]
        for x in days
    )

    total_inside = sum(
        x["inside"]
        for x in days
    )

    total_diff = (
        total_inside
        - total_target
    )
    
    progress = 0

    if total_target > 0:
        progress = round(
            (total_inside / total_target) * 100
        )

    if progress > 100:
        progress = 100
    
    progress_color = "#22c55e"

    if progress < 70:
        progress_color = "#ef4444"
    elif progress < 90:
        progress_color = "#f59e0b"
    
    month_color = (
    "#16a34a"
    if total_diff >= 0
    else "#dc2626"
    )

    today_color = (
        "#16a34a"
        if today["difference"] >= 0
        else "#dc2626"
    )

    rows = ""

    for d in reversed(days):

        color = (
            "green"
            if d["difference"] >= 0
            else "red"
        )

        rows += f"""
        <tr>
        <td>

        <b>{d['date']}</b><br>
        
        <span style="
        font-size:12px;
        color:#666;
        ">
        {d['inside']} / {d['target']} dk
        </span>

        </td>

        <td
        style="
        color:{color};
        font-size:18px;
        font-weight:bold;
        text-align:right;
        ">

        {d['difference']} dk

        </td>

        </tr>
        """

    return f"""
<html>

<head>

<meta name="viewport"
content="width=device-width, initial-scale=1">

<style>

body {{
    font-family:Arial;
    background:#f4f4f4;
    padding:15px;
}}

.card {{
    background:white;
    padding:18px;
    border-radius:16px;
    margin-bottom:15px;
    box-shadow:0 2px 6px rgba(0,0,0,0.08);
}}

.big {{
    font-size:48px;
    font-weight:bold;
}}

.medium {{
    font-size:30px;
    font-weight:bold;
}}

.small {{
    color:#666;
    font-size:12px;
}}

table {{
    width:100%;
}}

td {{
    padding:8px;
}}

.progress-container{{
    width:100%;
    height:18px;
    background:#e5e7eb;
    border-radius:10px;
    overflow:hidden;
    margin-top:10px;
}}

.progress-bar{{
    height:100%;
    background:#22c55e;
    transition:0.5s;
}}

</style>

</head>

<body>

<div class="card">

<h2>🏢 PDKS Eşşek Takip Sistemi</h2>

<div class="small">
Son Güncelleme:
{last_update}
</div>

<br>

<div class="small">
AYLIK DURUM
</div>

<div class="big">
{total_inside}
</div>

<div>
Hedef: {total_target} dk
</div>

<div
style="
margin-top:10px;
font-weight:bold;
">

%{progress}

</div>

<div class="progress-container">

<div
class="progress-bar"
style="
width:{progress}%;
background:{progress_color};
">
</div>

</div>

<div
style="
font-size:34px;
font-weight:bold;
color:{month_color};
">

{total_diff:+} dk

</div>

</div>

<div class="card">

<h3>Bugün</h3>

<div class="medium">
{today["inside"]} dk
</div>

<div>
Hedef: {today["target"]} dk
</div>

<div
style="
color:{today_color};
font-size:24px;
font-weight:bold;
">

{today["difference"]:+} dk

</div>

</div>

<div class="card">

<h3>📅 Günlük Geçmiş</h3>

<table>

{rows}

</table>

</div>

</body>

</html>
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
