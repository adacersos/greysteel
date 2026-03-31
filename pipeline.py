import pytesseract
from pdf2image import convert_from_path
import re
import google.generativeai as genai
import os

# Setup Gemini
genai.configure(api_key="AIzaSyCKoXZQuTsgKJsQ0L1tSsKrkFna3GV6l5Q")
model = genai.GenerativeModel("models/gemini-2.5-flash")


def clean_tesseract_soup(text):
    text = re.sub(r'(?<= )[^a-zA-Z0-9\s](?= )', '', text)
    text = re.sub(r'[|\\/_]{2,}', ' ', text)
    text = re.sub(r'^[|\\/_]$', '', text, flags=re.MULTILINE)
    text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def run_psa_extractor(pdf_path):

    # 1. OCR
    pages = convert_from_path(pdf_path, dpi=300)
    full_text = ""
    for page in pages:
        full_text += pytesseract.image_to_string(page) + "\n"

    # 2. Clean
    cleaned_output = clean_tesseract_soup(full_text)

    print("✅ OCR + cleaning done")

    # 3. YOUR PROMPT (unchanged except chunk → full text)
    user_content = f"""
Extract the following milestones from this PSA section into strict JSON.
If a milestone is NOT mentioned in this specific section, return null for that field.

Fields to fill and the information on what to look for:
1. Effective Date – Date the PSA is fully executed; starts the clock for all deadlines
2. Earnest Money Deposit Due – Buyer’s deposit showing good faith, usually credited at closing (typically a money value)
3. Title Due – Deadline to provide title commitment or confirm agreement delivery (look for a timeline, related to the title)
4. Buyer Title Objections Due – Deadline for Buyer to provide Seller with written objections to the Title Commitment, survey, or any title defects discovered during the title review period (timeline related)
5. Feasibility Period Expiration – Last day Buyer may terminate based on inspections or reviews (can also look for something related to due dilignece timeline)
6. Seller Response to Buyer Objections Due – Seller’s reply and timeline to cure title issues. (another timeline one)
7. Closing Date – Scheduled date for transferring ownership and funds (also know as settlement date, timeline one)

PSA SECTION:
{cleaned_output}
"""

    # 4. Call Gemini
    response = model.generate_content(
        user_content,
        generation_config={
            "temperature": 0.1
        }
    )

    return response.text