import requests
from bs4 import BeautifulSoup
import datetime
import os
import pdfplumber 
import re


def parse_pdf(pdf_path):

    # Step 1: Read all text from PDF
    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                full_text += t + "\n"
    print(full_text)


BASE_URL = "https://statelottery.kerala.gov.in"
RESULT_URL = BASE_URL + "/index.php/lottery-result-view"

# Today's date in table format
today = datetime.date(2026, 1, 5)
today_str = today.strftime("%d/%m/%Y")

session = requests.Session()
resp = session.get(RESULT_URL)
resp.raise_for_status()

soup = BeautifulSoup(resp.text, "html.parser")

pdf_found = False

# Loop through table rows
for row in soup.select("table tr"):
    cols = row.find_all("td")
    if len(cols) < 3:
        continue

    draw_date = cols[1].get_text(strip=True)

    if draw_date == today_str:
        print(f"Row found for today's date : {draw_date}")
        view_link = cols[2].find("a")

        if not view_link:
            continue

        view_url = view_link["href"]

        if view_url.startswith("/"):
            view_url = BASE_URL + view_url

        print("Opening View page:", view_url)
        pdf_response = session.get(
            view_url
        )

        content_type = pdf_response.headers.get("Content-Type", "")
        content_disposition = pdf_response.headers.get("Content-Disposition", "")
        filename = content_disposition.split('filename="')[1].rstrip('"')
        lottery_name = os.path.splitext(filename)[0]
        print(f"Lottery name : {lottery_name}")

        if content_type.startswith("application/pdf"):
            filename = f"kerala_lottery_{lottery_name}_{draw_date.replace('/', '-')}.pdf"
            with open(filename, "wb") as f:
                f.write(pdf_response.content)

            print("PDF downloaded:", filename)
            parse_pdf(filename)
            pdf_found = True
        else:
            print("Response is not PDF")
            print("Content-Type:", content_type)

        break

if not pdf_found:
    print("No result found for", today_str)