import requests
from bs4 import BeautifulSoup
import datetime
import os
from pdf_parser.lottery_result_parser import parse_lottery_pdf
from firebase.push_data import publish_lottery_result, get_last_notified_result, push_last_notified_result, push_fcm_notification


def scrape_lottery_result():
    BASE_URL = "https://statelottery.kerala.gov.in"
    RESULT_URL = BASE_URL + "/index.php/lottery-result-view"

    # Today's date in table format
    today = datetime.date.today()
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
                lottery_result = parse_lottery_pdf(filename)
                final_result  = {"lottery_name" : lottery_name, "results" : lottery_result}
                print(final_result)
                publish_lottery_result(lottery_name, final_result)
                last_notified = get_last_notified_result()
                print(f"============== {lottery_name}============================")
                print(f"============== {draw_date}============================")
                if last_notified != lottery_name+"_"+draw_date:
                    push_fcm_notification(lottery_name, draw_date)
                    push_last_notified_result(lottery_name, draw_date)

                if os.path.exists(filename):
                    os.remove(filename)
                    print("File deleted")
                pdf_found = True
                return "Scraped today's result"
            else:
                print("Response is not PDF")
                print("Content-Type:", content_type)
                return "Failed to scrape today's result"

            break

    if not pdf_found:
        print("No result found for", today_str)
        return "No result found for today"

