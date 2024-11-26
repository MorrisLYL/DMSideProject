import re
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import fitz
from paddleocr import PaddleOCR

def read_text_file(text_file):
    with open(text_file, 'r', encoding='utf-8') as f:
        text = f.read()
    return text

def is_text_weird(text, threshold=0.5):
    non_ascii_count = len(re.findall(r'[^\x00-\x7F]', text))
    # Calculate the ratio of non-ASCII characters
    weirdness_ratio = non_ascii_count / max(len(text), 1)
    # Return True if the ratio exceeds the threshold
    return weirdness_ratio > threshold

def ocr_pdf_file(pdf_file, total_page):
    ocr = PaddleOCR(use_angle_cls=True, lang="ch", page_num=total_page)
    # ocr = PaddleOCR(use_angle_cls=True, lang="ch", page_num=PAGE_NUM,use_gpu=0) # To Use GPU,uncomment this line and comment the above one.
    result = ocr.ocr(pdf_file, cls=True)
    for idx in range(len(result)):
        res = result[idx]
        if res is None:  # Skip when empty result detected to avoid TypeError:NoneType
            print(f"[DEBUG] Empty page {idx+1} detected, skip it.")
            continue
    all_text = []
    for idx in range(len(result)):
        res = result[idx]
        if res is None:
            continue
        page_text = ''
        for line in res:
            text = line[1][0]
            page_text += text
        all_text.append(page_text)
    return '\n'.join(all_text).replace('\x00', '') 

def extract_text_from_pdf(pdf_path: str) -> str:
    extracted_text = ""
    with fitz.open(pdf_path) as pdf_document:
        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]
            extracted_text += page.get_text() + '\n'
            if is_text_weird(extracted_text):
                print(f"Weird text detected on page {page_num + 1}. Stopping text extraction.")
                # Stop reading or switch to OCR processing here
                break
        if(len(extracted_text) == 0 or (is_text_weird(extracted_text) and page_num == 0)):
            print("Trigger OCR")
            extracted_text = ocr_pdf_file(pdf_path, pdf_document.page_count)
    
    extracted_text = extracted_text.replace('\x00', '')
    return extracted_text

def adjust_timezone(dt: datetime, target_tz: ZoneInfo) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    
    dt_target = dt.astimezone(target_tz)
    return dt_target.strftime("%Y-%m-%d %H:%M:%S")
