import re

import pdfplumber


def extract_consignment_id(pdf_data):
    consignment_ids = []
    with pdfplumber.open(pdf_data["file_name"]) as pdf:
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                lines = text.split('\n')
                for line in lines:
                    if pdf_data["delivery_partner"] == "delhivery" and line.isdigit() and len(line) == 14:
                        consignment_ids.append((page_num + 1, line))
                        break
                    elif pdf_data["delivery_partner"] == "dtdc" and len(line) == 9:
                        consignment_id_pattern = re.compile(r'[A-Z]\d{8,}')
                        if consignment_id_pattern.search(line):
                            consignment_ids.append((page_num + 1, line))
                            break
    return consignment_ids


pdf_files = [
    {"file_name": "delhivery_pdf.pdf", "delivery_partner": "delhivery"},
    {"file_name": "dtdc_pdf.pdf", "delivery_partner": "dtdc"}
]

for pdf_file in pdf_files:
    consignment_ids = extract_consignment_id(pdf_file)
    print(f"Consignment IDs for delivery partner - {pdf_file['delivery_partner']}:")
    for page, cid in consignment_ids:
        print(f"Page {page}: {cid}")
