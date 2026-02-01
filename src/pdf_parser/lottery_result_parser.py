
import pdfplumber 
import re
from pprint import pprint
import logging



def parse_lottery_pdf(pdf_path, lottery_name):

    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text(layout=True)
            if not text:
                continue
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if line.strip():
                    full_text = full_text + line +"\n"

    target = "1st Prize"
    end_marker = "Government Gazette"

    if target in full_text:
        # This slices the string starting from the location of '1st Prize'
        cleaned_text = full_text[full_text.index(target):]
        if end_marker in cleaned_text:
            cleaned_text = cleaned_text.split(end_marker)[0]
        cleaned_text = remove_footer(cleaned_text)
        return parse_lottery_result(cleaned_text, lottery_name)
    else:
        logging.info("Marker not found.")

def remove_footer(text: str) -> str:
    pattern = r"\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2}.*?Page\s+\d+"
    return re.sub(pattern, "", text)

def parse_lottery_result(text: str, lottery_name:str):
    result = {}
    top_prize_pattern = ()
    prize_blocks = {}

    if re.fullmatch(r"BR-\d{3}", lottery_name):
        logging.info(f"Bumper ticket : {lottery_name}")
        # ---------- 1st, 2nd, 3rd, 4th, 5th PRIZES ----------
        top_prize_pattern = (
            r"(?P<prize>\d+(?:st|nd|rd|th)) Prize\s+Rs\s*:\s*(?P<amount>\d+)/-\s*"
            r"(?P<tickets>(?:\d+\)\s*[A-Z]{1,2}\s*\d+(?:\s*\([A-Z]+\))?\s*)+)"
        ) 
        # ---------- 6th TO 10th PRIZES ----------
        prize_blocks = {
            "6th Prize": r"6th Prize-Rs\s*:\s*(\d+)/-\s*([\s\S]*?)7th Prize",
            "7th Prize": r"7th Prize-Rs\s*:\s*(\d+)/-\s*([\s\S]*?)8th Prize",
            "8th Prize": r"8th Prize-Rs\s*:\s*(\d+)/-\s*([\s\S]*?)9th Prize",
            "9th Prize": r"9th Prize-Rs\s*:\s*(\d+)/-\s*([\s\S]*?)10th Prize",
            "10th Prize": r"10th Prize-Rs\s*:\s*(\d+)/-\s*([\s\S]*?)$"
        }
    else:
        logging.info(f"Weekly ticket : {lottery_name}")
        # ---------- 1st, 2nd, 3rd PRIZES ----------
        top_prize_pattern = (
            r"(?P<prize>\d+(?:st|nd|rd)) Prize\s+Rs\s*:\s*(?P<amount>\d+)/-\s*"
            r"(?P<tickets>(?:\d+\)\s*[A-Z]{1,2}\s*\d+(?:\s*\([A-Z]+\))?\s*)+)"
        )
        # ---------- 4th TO 8th PRIZES ----------
        prize_blocks = {
            "4th Prize": r"4th Prize-Rs\s*:\s*(\d+)/-\s*([\s\S]*?)5th Prize",
            "5th Prize": r"5th Prize-Rs\s*:\s*(\d+)/-\s*([\s\S]*?)6th Prize",
            "6th Prize": r"6th Prize-Rs\s*:\s*(\d+)/-\s*([\s\S]*?)7th Prize",
            "7th Prize": r"7th Prize-Rs\s*:\s*(\d+)/-\s*([\s\S]*?)8th Prize",
            "8th Prize": r"8th Prize-Rs\s*:\s*(\d+)/-\s*([\s\S]*?)9th Prize",
            "9th Prize": r"9th Prize-Rs\s*:\s*(\d+)/-\s*([\s\S]*?)$",
        }

    for m in re.finditer(top_prize_pattern, text, re.DOTALL):
        prize = m.group("prize") + " Prize"
        tickets = re.findall(r"[A-Z]{1,2}\s*\d+", m.group("tickets"))  # all tickets
        result[prize] = {
            "amount": m.group("amount"),
            "ticket_number": tickets
        }

    # ---------- CONSOLATION PRIZE ----------
    cons_pattern = (
        r"Cons Prize-Rs\s*:\s*(?P<amount>\d+)/-\s*"
        r"(?P<body>(?:[A-Z]{2}\s*\d+\s*)+)"
    )

    m = re.search(cons_pattern, text)
    if m:
        tickets = re.findall(r"[A-Z]{2}\s*\d+", m.group("body"))
        result["Cons Prize"] = {
            "amount": m.group("amount"),
            "ticket_number": tickets
        }

    for prize, pattern in prize_blocks.items():
        m = re.search(pattern, text)
        if not m:
            continue

        amount = m.group(1)
        block = m.group(2)

        numbers = re.findall(r"\b\d{4}\b", block)

        result[prize] = {
            "amount": amount,
            "ticket_number": numbers
        }

    return result


