import requests
from bs4 import BeautifulSoup
import datetime
import os
from pdf_parser.lottery_result_parser import parse_lottery_pdf
from firebase.push_data import publish_lottery_result, get_last_notified_result, push_last_notified_result, push_fcm_notification
import logging

def scrape_lottery_result():
    BASE_URL = "https://statelottery.kerala.gov.in"
    RESULT_URL = BASE_URL + "/index.php/lottery-result-view"

    # Today's date in table format
    today = datetime.date.today()- datetime.timedelta(days=1)
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
            logging.info(f"Row found for today's date : {draw_date}")
            view_link = cols[2].find("a")

            if not view_link:
                continue

            view_url = view_link["href"]

            if view_url.startswith("/"):
                view_url = BASE_URL + view_url

            logging.info(f"Opening View page: {view_url}")
            pdf_response = session.get(
                view_url
            )

            content_type = pdf_response.headers.get("Content-Type", "")
            content_disposition = pdf_response.headers.get("Content-Disposition", "")
            filename = content_disposition.split('filename="')[1].rstrip('"')
            lottery_name = os.path.splitext(filename)[0]
            logging.info(f"Lottery name : {lottery_name}")

            if content_type.startswith("application/pdf"):
                filename = f"kerala_lottery_{lottery_name}_{draw_date.replace('/', '-')}.pdf"
                with open(filename, "wb") as f:
                    f.write(pdf_response.content)

                logging.info(f"PDF downloaded: {filename}")
                lottery_result = parse_lottery_pdf(filename, lottery_name)
                final_result  = {"lottery_name" : lottery_name, "results" : lottery_result}
                publish_lottery_result(lottery_name, final_result)
                last_notified = get_last_notified_result()
                if last_notified != lottery_name+"_"+draw_date:
                    logging.info("Publishing FCM notification ")
                    push_fcm_notification(lottery_name, draw_date)
                    logging.info("Updating last notified")
                    push_last_notified_result(lottery_name, draw_date)

                if os.path.exists(filename):
                    os.remove(filename)
                    logging.info("File deleted")
                pdf_found = True
            else:
                logging.info(f"Response is not a PDF : {content_type}")

    if not pdf_found:
        logging.info(f"No result found for {today_str}")

