from PIL import Image
import pytesseract

def verify_screenshot(img_path, url_text):
    image = Image.open(img_path)
    text = pytesseract.image_to_string(image)
    return url_text in text

def calculate_trust_level(verified_reports):
    if verified_reports >= 10: return "خبير"
    elif verified_reports >= 3: return "مشارك"
    else: return "مبتدئ"