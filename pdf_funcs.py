from reportlab.lib.units import cm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.pagesizes import A4, A5, landscape
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

import arabic_reshaper
from bidi.algorithm import get_display




pdfmetrics.registerFont(TTFont('ArabicFont', r"fixed_data/Amiri.ttf"))
font = "ArabicFont"


def fit_text_to_column(text, font_name, max_width, max_font_size):
    font_size = max_font_size
    while font_size > 0:
        text_width = stringWidth(text, font_name, font_size)
        if text_width <= max_width - .1 * cm:
            break
        font_size -= 1
    return font_size

def text_to_ar(text: str):
    return get_display(arabic_reshaper.reshape(text))

arabic_weekdays = {
    "Monday": "الإثنين", "Tuesday": "الثلاثاء", "Wednesday": "الأربعاء", "Thursday": "الخميس", "Friday": "الجمعة",
    "Saturday": "السبت", "Sunday": "الأحد",
}
