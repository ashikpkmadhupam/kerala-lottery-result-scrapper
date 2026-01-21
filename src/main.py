import logging
from scrapper.result_scrapper import scrape_lottery_result
import sys
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    stream=sys.stdout
)

def run_lottery_scrapper():
    logging.info("RUN Started")
    scrape_lottery_result()
    logging.info("RUN Completed")

if __name__ == "__main__":
    run_lottery_scrapper()