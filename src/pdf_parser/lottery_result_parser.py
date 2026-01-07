
import pdfplumber 
import re
from pprint import pprint



def parse_lottery_pdf(pdf_path):

    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:

            width = page.width
            height = page.height
            top_margin = 100 
            bottom_margin = height - 100
            bounding_box = (0, top_margin, width, bottom_margin)
            clean_page = page.within_bbox(bounding_box)
            text = clean_page.extract_text(layout=True)
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
        return parse_lottery_result(cleaned_text)
    else:
        print("Marker not found.")



def parse_lottery_result(text: str):
    result = {}

    # ---------- 1st, 2nd, 3rd PRIZES ----------
    top_prize_pattern = (
        r"(?P<prize>\d+(?:st|nd|rd)) Prize\s+Rs\s*:\s*(?P<amount>\d+)/-\s*"
        r"1\)\s*(?P<ticket>[A-Z]{2}\s*\d+)"
    )

    for m in re.finditer(top_prize_pattern, text):
        prize = m.group("prize") + " Prize"
        result[prize] = {
            "amount": m.group("amount"),
            "ticket_number": [m.group("ticket")]
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

    # ---------- 4th TO 8th PRIZES ----------
    prize_blocks = {
        "4th Prize": r"4th Prize-Rs\s*:\s*(\d+)/-\s*([\s\S]*?)5th Prize",
        "5th Prize": r"5th Prize-Rs\s*:\s*(\d+)/-\s*([\s\S]*?)6th Prize",
        "6th Prize": r"6th Prize-Rs\s*:\s*(\d+)/-\s*([\s\S]*?)7th Prize",
        "7th Prize": r"7th Prize-Rs\s*:\s*(\d+)/-\s*([\s\S]*?)8th Prize",
        "8th Prize": r"8th Prize-Rs\s*:\s*(\d+)/-\s*([\s\S]*?)$",
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


