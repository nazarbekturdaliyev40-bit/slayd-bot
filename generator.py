import os
import re
import json
import logging
import asyncio
import subprocess
import shutil
import urllib.parse
import aiohttp
import socket
from datetime import datetime
from PIL import Image, ImageDraw
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from google import genai
from google.genai import types
import tempfile
import pypdf
import docx
import config
import locales

logger = logging.getLogger(__name__)

# Slayd orqa foni va dizayn mavzulari (Canva uslubida)
THEMES = {
    "white": {
        "name": "⚪️ Oq fon (Minimal)",
        "primary": RGBColor(26, 54, 93),          # Deep Navy banner
        "accent": RGBColor(37, 99, 235),          # Royal Blue
        "accent_secondary": RGBColor(59, 130, 246),
        "bg_slide": RGBColor(255, 255, 255),      # Pure White
        "card_bg": RGBColor(248, 250, 252),       # Light Slate
        "card_border": RGBColor(203, 213, 225),   # Slate Border
        "text_dark": RGBColor(15, 23, 42),        # Slate 900
        "text_muted": RGBColor(100, 116, 139),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "•",
        "tag": "MINIMALIST OQ"
    },
    "dark": {
        "name": "🖤 Qora fon (Premium Dark)",
        "primary": RGBColor(18, 18, 18),          # OLED Black
        "accent": RGBColor(245, 158, 11),         # Luxury Gold / Amber
        "accent_secondary": RGBColor(234, 179, 8),
        "bg_slide": RGBColor(24, 24, 27),         # Dark Zinc
        "card_bg": RGBColor(39, 39, 42),          # Zinc Card
        "card_border": RGBColor(245, 158, 11),
        "text_dark": RGBColor(255, 255, 255),     # 100% Crisp White (Never dark on black)
        "text_muted": RGBColor(212, 212, 216),    # Bright Zinc 300 (Clear silver, never black)
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "•",
        "tag": "PREMIUM DARK"
    },
    "navy": {
        "name": "🔵 Toʻq koʻk fon (Royal Navy)",
        "primary": RGBColor(15, 23, 60),          # Royal Navy
        "accent": RGBColor(217, 119, 6),          # Luxury Gold
        "accent_secondary": RGBColor(245, 158, 11),
        "bg_slide": RGBColor(241, 245, 249),      # Cool Slate
        "card_bg": RGBColor(255, 255, 255),
        "card_border": RGBColor(217, 119, 6),
        "text_dark": RGBColor(15, 23, 42),
        "text_muted": RGBColor(71, 85, 105),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "•",
        "tag": "ROYAL NAVY"
    },
    "blue": {
        "name": "🔷 Moviy fon (Havorang)",
        "primary": RGBColor(26, 54, 93),          # Deep Navy
        "accent": RGBColor(14, 165, 233),         # Sky Blue
        "accent_secondary": RGBColor(2, 132, 199),
        "bg_slide": RGBColor(240, 249, 255),      # Soft Sky Pale
        "card_bg": RGBColor(255, 255, 255),
        "card_border": RGBColor(14, 165, 233),
        "text_dark": RGBColor(15, 23, 42),
        "text_muted": RGBColor(71, 85, 105),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "•",
        "tag": "MOVIY KLASSIK"
    },
    "green": {
        "name": "🟢 Zumrad yashil fon",
        "primary": RGBColor(6, 78, 59),           # Forest Emerald
        "accent": RGBColor(16, 185, 129),         # Fresh Mint
        "accent_secondary": RGBColor(13, 148, 136),# Teal
        "bg_slide": RGBColor(240, 253, 244),      # Mint White
        "card_bg": RGBColor(255, 255, 255),
        "card_border": RGBColor(52, 211, 153),
        "text_dark": RGBColor(6, 78, 59),
        "text_muted": RGBColor(55, 65, 81),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "•",
        "tag": "ZUMRAD YASHIL"
    },
    "purple": {
        "name": "🟣 Binafsha fon (Kosmik)",
        "primary": RGBColor(46, 16, 101),         # Deep Violet
        "accent": RGBColor(139, 92, 246),         # Neon Purple
        "accent_secondary": RGBColor(168, 85, 247),
        "bg_slide": RGBColor(245, 243, 255),      # Lavender Pale
        "card_bg": RGBColor(255, 255, 255),
        "card_border": RGBColor(167, 139, 250),
        "text_dark": RGBColor(30, 27, 75),
        "text_muted": RGBColor(75, 85, 99),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "•",
        "tag": "KOSMIK BINAFSHA"
    },
    "canva_pastel": {
        "name": "🌸 Canva Pastel fon (Nafis)",
        "primary": RGBColor(79, 70, 229),         # Canva Indigo
        "accent": RGBColor(236, 72, 153),         # Hot Pink / Magenta
        "accent_secondary": RGBColor(168, 85, 247),
        "bg_slide": RGBColor(253, 242, 248),      # Soft Pink / Rose Pale
        "card_bg": RGBColor(255, 255, 255),
        "card_border": RGBColor(244, 114, 182),
        "text_dark": RGBColor(30, 27, 75),
        "text_muted": RGBColor(107, 114, 128),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "•",
        "tag": "CANVA PASTEL"
    },
    "vintage": {
        "name": "📜 Klassik pergament fon",
        "primary": RGBColor(67, 40, 24),          # Antique Mahogany
        "accent": RGBColor(194, 137, 44),         # Antique Gold
        "accent_secondary": RGBColor(146, 64, 14),# Warm Amber
        "bg_slide": RGBColor(250, 246, 238),      # Parchment / Pergament fon
        "card_bg": RGBColor(255, 253, 249),       # Antique Ivory
        "card_border": RGBColor(217, 169, 90),    # Vintage Gold Border
        "text_dark": RGBColor(55, 30, 16),        # Espresso
        "text_muted": RGBColor(107, 79, 61),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "•",
        "tag": "KLASSIK RETRO"
    }
}

# Moslik uchun taxalluslar (aliases)
THEMES["tech"] = THEMES["blue"]
THEMES["business"] = THEMES["navy"]
THEMES["nature"] = THEMES["green"]
THEMES["science"] = THEMES["purple"]
THEMES["art"] = THEMES["canva_pastel"]
THEMES["history"] = THEMES["vintage"]

def detect_theme(topic: str, ai_theme: str = "") -> str:
    """Mavzu matniga qarab mos rang va fon mavzusini aniqlaydi."""
    ai_theme = (ai_theme or "").lower().strip()
    if ai_theme in THEMES:
        return ai_theme
        
    t = topic.lower()
    
    # 1. Tarix, madaniyat, qadimgi davr, buyuk shaxslar
    if any(k in t for k in ["tarix", "history", "qadimgi", "sulol", "urush", "amir temur", "bobur", "xonlik", "arxeolog", "madaniyat", "imperiya", "inqilob", "sovet", "jadid", "asr"]):
        return "history"
        
    # 2. Dasturlash, IT, AI, kompyuter, texnologiya
    if any(k in t for k in ["dastur", "program", " it", "it ", "kompyuter", "python", "java", "kod", "texnolog", "sun'iy intellekt", "ai", "kiber", "robot", "tarmoq", "algoritm", "data", "web", "android", "ios", "xavfsizlik", "backend", "frontend"]):
        return "tech"
        
    # 3. Tabiat, biologiya, tibbiyot, salomatlik, ekologiya
    if any(k in t for k in ["tibbiyot", "salomatlik", "kasallik", "vrach", "shifokor", "biolog", "ekolog", "tabiat", "o'simlik", "hayvon", "yashil", "atrof-muhit", "dori", "anatomiya", "geograf", "virus"]):
        return "nature"
        
    # 4. Biznes, iqtisod, moliya, marketing, savdo
    if any(k in t for k in ["biznes", "iqtisod", "moliya", "marketing", "bank", "savdo", "investitsiya", "pul", "daromad", "menejment", "startap", "kompaniya", "bozor"]):
        return "business"
        
    # 5. Ilm-fan, fizika, matematika, kimyo, kosmos
    if any(k in t for k in ["fizika", "matematika", "kimyo", "astronom", "kosmos", "koinot", "formula", "ilmiy", "laboratoriya"]):
        return "science"
        
    # 6. San'at, dizayn, ijod, musiqa
    if any(k in t for k in ["san'at", "dizayn", "musiqa", "rasm", "kino", "teatr", "arxitektura", "she'riyat"]):
        return "art"
        
    return "blue"

EMOJI_PATTERN = re.compile(
    "["
    "\U0001F1E0-\U0001F1FF"  # flags
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F700-\U0001F77F"  # alchemical symbols
    "\U0001F780-\U0001F7FF"  # geometric shapes extended
    "\U0001F800-\U0001F8FF"  # supplemental arrows
    "\U0001F900-\U0001F9FF"  # supplemental symbols and pictographs
    "\U0001FA00-\U0001FA6F"  # chess symbols
    "\U0001FA70-\U0001FAFF"  # symbols and pictographs extended-a
    "\U00002700-\U000027BF"  # dingbats (scissors, checks, stars, crosses, etc.)
    "\U00002600-\U000026FF"  # misc symbols
    "\U00002B50-\U00002B55"  # star, circle
    "\U0000231A-\U0000231B"  # watches
    "\U000023E9-\U000023EC"  # fast-forward / arrows
    "\U000023F0-\U000023F3"  # clocks, hourglass
    "\U000025AA-\U000025FE"  # geometric boxes/shapes
    "\U00002B00-\U00002BFF"  # misc symbols & arrows
    "\U0000FE00-\U0000FE0F"  # variation selectors
    "\U0000200D"              # zero-width joiner
    "]+",
    flags=re.UNICODE
)

def remove_emojis(text: str) -> str:
    """Matndan har qanday emoji, stiker va piktogramma belgilarini tozalaydi."""
    if not text:
        return ""
    cleaned = EMOJI_PATTERN.sub("", str(text))
    cleaned = re.sub(r"[ \t]+", " ", cleaned).strip()
    return cleaned

def clean_data_structure(obj):
    """Lug'at yoki ro'yxat ichidagi barcha matnlarni rekursiv ravishda emojilardan tozalaydi."""
    if isinstance(obj, str):
        return remove_emojis(obj)
    elif isinstance(obj, list):
        return [clean_data_structure(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: clean_data_structure(v) for k, v in obj.items()}
    return obj

def clean_prefix(val: str, prefixes: list) -> str:
    if not val:
        return ""
    v = val.strip()
    for p in prefixes:
        if v.lower().startswith(p.lower()):
            v = v[len(p):].strip(" :-\t")
    return v

def safe_json_loads(raw_text: str) -> dict:
    """Tozalaydi, markdown teglarni olib tashlaydi va xatolarga chidamli JSON yuklaydi."""
    text = (raw_text or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
        text = text.strip()

    try:
        return json.loads(text)
    except Exception:
        pass

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        snippet = text[start:end+1]
        try:
            return json.loads(snippet)
        except Exception:
            cleaned_snippet = re.sub(r",\s*([}\]])", r"\1", snippet)
            try:
                return json.loads(cleaned_snippet)
            except Exception:
                pass

    return json.loads(text)

def smart_parse_student_details(raw: str) -> dict:
    """Foydalanuvchi yozgan xom matndan OTM, fakultet, yo'nalish, guruh, talaba va o'qituvchini aniq ajratib beradi."""
    if not raw or not raw.strip():
        return {}
    
    details = {
        "university": "",
        "faculty": "",
        "direction": "",
        "group": "",
        "student": "",
        "teacher": ""
    }
    
    # 1. Key-value style pattern matching if labeled (e.g. OTM: TATU, Talaba: Aliyev, etc.)
    kv_patterns = {
        "teacher": r"(?:o[\x27\u02bc\u02bb\u2018\u2019`]?qituvchi(?:si)?|ilmiy\s+rahbar(?:i)?|rahbar(?:i)?|qabul\s+qildi|domla|ustoz)[:\s]+([^,\n;]+?)(?=$|\s*[,;\n]|\s+(?:OTM|Universitet|Institut|Fakultet|Guruh|Talaba|Yo[\x27\u02bc\u02bb\u2018\u2019`]?nalish))",
        "student": r"(?:talabasi|talaba|bajardi|muallif)[:\s]+([^,\n;]+?)(?=$|\s*[,;\n]|\s+(?:OTM|Universitet|Institut|Fakultet|Guruh|Yo[\x27\u02bc\u02bb\u2018\u2019`]?nalish|o[\x27\u02bc\u02bb\u2018\u2019`]?qituvchi))",
        "university": r"(?:otm|universitet|institut)[:\s]+([^,\n;]+?)(?=$|\s*[,;\n]|\s+(?:Fakultet|Guruh|Talaba|Yo[\x27\u02bc\u02bb\u2018\u2019`]?nalish|o[\x27\u02bc\u02bb\u2018\u2019`]?qituvchi))",
        "faculty": r"(?:fakultet(?:i)?)[:\s]+([^,\n;]+?)(?=$|\s*[,;\n]|\s+(?:OTM|Universitet|Institut|Guruh|Talaba|Yo[\x27\u02bc\u02bb\u2018\u2019`]?nalish|o[\x27\u02bc\u02bb\u2018\u2019`]?qituvchi))",
        "group": r"(?:guruh(?:i)?|kurs(?:i)?)[:\s]+([^,\n;]+?)(?=$|\s*[,;\n]|\s+(?:OTM|Universitet|Institut|Fakultet|Talaba|Yo[\x27\u02bc\u02bb\u2018\u2019`]?nalish|o[\x27\u02bc\u02bb\u2018\u2019`]?qituvchi))",
        "direction": r"(?:yo[\x27\u02bc\u02bb\u2018\u2019`]?nalish(?:i)?)[:\s]+([^,\n;]+?)(?=$|\s*[,;\n]|\s+(?:OTM|Universitet|Institut|Fakultet|Guruh|Talaba|o[\x27\u02bc\u02bb\u2018\u2019`]?qituvchi))"
    }
    
    text = " " + " ".join(raw.strip().split()) + " "
    for k, pat in kv_patterns.items():
        m = re.search(pat, text, re.I)
        if m:
            val = m.group(1).strip()
            if val and len(val) > 1:
                details[k] = val
                text = text[:m.start()] + " " + text[m.end():]

    # 2. Natural text extraction if not matched by labeled keys
    if not details["teacher"]:
        m = re.search(r"(?:o[\x27\u02bc\u02bb\u2018\u2019`]?qituvchi(?:si)?|ilmiy\s+rahbar(?:i)?|rahbar(?:i)?|qabul\s+qildi|domla|ustoz)[:\s]+([A-Za-z\u0400-\u04FF\x27\u02bc\u02bb\u2018\u2019`\s]+?)(?=$|\s+(?:talaba|fakultet|universitet|guruh|yo[\x27\u02bc\u02bb\u2018\u2019`]?nalish|OTM))", text, re.I)
        if m:
            details["teacher"] = m.group(1).strip()
            text = text[:m.start()] + " " + text[m.end():]

    if not details["university"]:
        m = re.search(r"([A-Za-z\u0400-\u04FF\x27\u02bc\u02bb\u2018\u2019`\s]+?(?:universiteti?|instituti?|akademiyasi?|OTM|TATU|ADU|SamDU|O[\x27\u02bc\u02bb\u2018\u2019`]zMU|ToshDAU|ToshDTU|FarDU|NamDU|GulDU|QDU))", text, re.I)
        if m:
            details["university"] = m.group(1).strip()
            text = text[:m.start()] + " " + text[m.end():]

    if not details["faculty"]:
        m = re.search(r"([A-Za-z\u0400-\u04FF\x27\u02bc\u02bb\u2018\u2019`\s]+?fakulteti?)", text, re.I)
        if m:
            details["faculty"] = m.group(1).strip()
            text = text[:m.start()] + " " + text[m.end():]

    if not details["group"]:
        m = re.search(r"(\d+[- ]*(?:guruh(?:i)?|kurs(?:i)?))", text, re.I)
        if m:
            details["group"] = m.group(1).strip()
            text = text[:m.start()] + " " + text[m.end():]

    if not details["student"]:
        m = re.search(r"(?:talabasi|talaba|bajardi)[:\s]+([A-Za-z\u0400-\u04FF\x27\u02bc\u02bb\u2018\u2019`\s]+)", text, re.I)
        if m:
            details["student"] = m.group(1).strip()
            text = text[:m.start()] + " " + text[m.end():]

    if not details["direction"]:
        m = re.search(r"(?:yo[\x27\u02bc\u02bb\u2018\u2019`]?nalishi?[:\s]+)?([A-Za-z\u0400-\u04FF\x27\u02bc\u02bb\u2018\u2019`\s]+?yo[\x27\u02bc\u02bb\u2018\u2019`]?nalishi?)", text, re.I)
        if m:
            details["direction"] = m.group(1).strip()
            text = text[:m.start()] + " " + text[m.end():]

    rem = " ".join(text.split()).strip("•-, :;")
    if rem:
        if not details["student"]:
            details["student"] = rem
        elif not details["direction"]:
            details["direction"] = rem

    # Clean prefixes
    details["student"] = clean_prefix(details["student"], ["bajardi", "talaba", "talabasi", "muallif", "tayyorladi"])
    details["teacher"] = clean_prefix(details["teacher"], ["qabul qildi", "o'qituvchi", "oʻqituvchi", "ilmiy rahbar", "rahbar", "domla", "ustoz"])
    details["university"] = clean_prefix(details["university"], ["otm", "universitet", "institut"])
    details["faculty"] = clean_prefix(details["faculty"], ["fakultet", "fakulteti"])
    details["group"] = clean_prefix(details["group"], ["guruh", "guruhi", "kurs", "kursi"])
    details["direction"] = clean_prefix(details["direction"], ["yo'nalish", "yoʻnalishi"])

    return details

def calculate_slide_distribution(total_slides: int):
    """Calculates the exact number of intro, content, and closing slides to ensure full coverage of topics."""
    if total_slides <= 5:
        has_agenda = False
        intro_count = 1  # Titul
        closing_count = 1  # Combined Xulosa & Minnatdorchilik
    elif total_slides <= 10:
        has_agenda = True
        intro_count = 2  # Titul + Agenda
        closing_count = 2  # Xulosa & Manbalar + Minnatdorchilik
    else:
        has_agenda = True
        intro_count = 2  # Titul + Agenda
        closing_count = 3  # Xulosa + Manbalar + Minnatdorchilik

    target_content_count = max(1, total_slides - (intro_count + closing_count))
    return has_agenda, intro_count, closing_count, target_content_count

async def generate_presentation_content(topic: str, slide_count: int = 8, language: str = "uz", author_info: str = "", theme_choice: str = "auto", context_document: str = "") -> dict:
    """Uses Google Gemini to generate structured slide content in JSON with academic references, infographic layouts, and structured student details."""
    client = genai.Client(api_key=config.GEMINI_API_KEY)
    
    lang_info = locales.get_slide_lang_info(language)
    prompt_lang = lang_info["prompt"]
    
    author_clause = f"\nTaqdimot muallifi va OTM ma'lumotlari: {author_info}" if author_info else ""
    theme_clause = f"\nFoydalanuvchi tanlagan dizayn mavzusi: '{theme_choice}'." if theme_choice and theme_choice != "auto" else ""
    context_clause = f"\nASOSIY MANBA MATN (Kitob/Konspekt/Hujjat):\n```\n{context_document[:8000]}\n```\nYuqoridagi manba matnidan foydalanib, undagi asosiy dalillar, faktlar va tushunchalar asosida taqdimot tuzing." if context_document else ""
    
    has_agenda, intro_count, closing_count, num_content = calculate_slide_distribution(slide_count)

    prompt = f"""
Siz universitet va oliy ta'lim talabalari uchun akademik va professional taqdimotlar tayyorlovchi yetuk AI mutaxassisiz.

FOYDALANUVCHI YUBORGAN TAQDIMOT MAVZUSI VA TALABLARI:
\"\"\"
{topic.strip()}
\"\"\"{author_clause}{theme_clause}{context_clause}

======================================================================
MUHIM VA QAT'IY TALAB: FOYDALANUVCHI YUBORGAN MAVZULARNI TO'LIQ VA CHUQUR YORITIB BERISH!
======================================================================
1. FOYDALANUVCHI YUBORGAN BARCHA MAVZU VA REJA BANDLARINI 100% QAMRAB OLISH:
- Agar foydalanuvchi o'z xabarida bir nechta mavzular, reja bandlari, savollar yoki kichik mavzular (subtopics) yuborgan bo'lsa (masalan: 1, 2, 3... deb raqamlangan ro'yxat, qavs ichidagi mavzular yoki matndagi bir necha masalalar):
  * Yuborilgan HAR BIR mavzu va reja bandini ISTISNOSIZ to'liq qamrab oling!
  * Birorta ham mavzu, masala yoki reja bandi tashlab ketilmasin (o'tkazib yuborilmasin)!
  * Taqdimotning asosiy 'slides' slaydlari aynan foydalanuvchi so'ragan mana shu mavzular va reja bandlariga bag'ishlansin.
- Agar foydalanuvchi bitta umumiy mavzu yuborgan bo'lsa:
  * Ushbu mavzuni tor va yuzaki emas, balki sohaning barcha asosiy tushunchalari, ilmiy-amaliy tarmoqlari, muhim tamoyillari, funksiyalari va zamonaviy yutuqlarini o'z ichiga olgan holda TO'LIQ, BAFURJA VA CHUQUR yoritib bering! Har bir mazmuniy slayd mavzuning alohida mustaqil qismini to'liq ochib bersin.

2. SLAYDLARNI ZOYE KETKAZMASLIK VA 100% BEVOSITA MAZMUNGA QARATISH:
- DIQQAT: Taqdimotning titul (muqova), mundarija (reja), xulosa va adabiyotlar slaydlari avtomatik tarzda alohida yaratiladi!
- Shu sababli, 'slides' massividagi RO'PPA-ROSA {num_content} ta slaydning HAMMASI 100% BEVOSITA FOYDALANUVCHI MAVZULARIGA bag'ishlangan bo'lishi SHART!
- 'slides' massivining boshida umumiy quruq "Kirish" yoki oxirida ortiqcha "Xulosa va amaliy tavsiyalar" kabi keraksiz slaydlarni QO'SHMANG! Har bir slayd bevosita foydalanuvchi yuborgan mavzuning alohida muhim qismini to'liq ochib bersin!

3. TAQDIMOT REJASI ("agenda"):
- Taqdimot rejasi ("agenda") umumiy quruq shablon ("Kirish", "Nazariya", "Amaliyot", "Xulosa") BO'LMASIN!
- Reja bandlari aynan foydalanuvchi yuborgan mavzular va asosiy mazmuniy slaydlarning haqiqiy sarlavhalarini aks ettirsin (3 tadan 5 tagacha asosiy band)!

4. SLAYD MATNLARI VA MAZMUNINING CHUQURLIGI:
- Har bir slaydda 3 tadan 5 tagacha yuqori darajada mazmunli, chuqur va batafsil band ("bullet_points") bo'lsin.
- Bandlar shunchaki 2-3 ta so'zdan iborat bo'sh gap bo'lmasin! Har bir bandni quyidagi tartibda to'liq yozing:
  "Kalit so'z yoki tushuncha: Mazkur tushunchaning ilmiy-amaliy mohiyati, aniq faktlar, tahlillar va amaliy ahamiyati haqida kamida 15-25 so'zdan iborat to'liq, chuqur tushuntirish."
- Talaba ushbu slaydni o'qiganda va ko'rsatganda mavzu to'liq, mukammal va professional yoritilgani yaqqol ko'rinib tursin!

5. MA'RUZA NUTQI (SPEAKER_NOTES):
- Har bir slayd uchun "speaker_notes" maydonida talaba doskada turib gapirib beradigan jonli, ravon, ilmiy va tushunarli ma'ruza nutqi (3-5 ta to'liq gap) bo'lsin.

DIQQAT (QAT'IY TALAB): Foydalanuvchi jami taqdimot hajmi (titul muqova, reja, xulosa va yakun bilan birga) JAMI RO'PPA-ROSA {slide_count} TA SLAYDDAN iborat bo'lishini belgiladi (belgilangandan 1 list ham oshmasin!).
Shu sababli, taqdimotning ichki 'slides' massivida RO'PPA-ROSA {num_content} ta asosiy mazmuniy slayd tuzib bering (hech qachon {num_content} tadan oshmasin yoki kam bo'lmasin).
Qat'iy talab qilingan til: {prompt_lang}.
DIQQAT: Taqdimotning barcha slaydlari, sarlavhalari, rejalari, matnlari, taqqoslashlari, xulosalari, manbalari va spiker nutqi (speaker_notes) 100% FAQAT va FAQAT {prompt_lang} tilida bo'lishi SHART! Barcha matnlar tanlangan tilning imlo, orfografik va grammatik qoidalariga to'liq mos kelishi, tushunarli, akademik va professional bo'lishi kerak.

Mavzuning sohasini aniqlang va quyidagi rang temalaridan birini tanlang:
- "tech" (agar dasturlash, kompyuter, axborot texnologiyalari, IT, sun'iy intellekt, robototexnika, kiberxavfsizlik bo'lsa)
- "history" (agar tarix, qadimiy davrlar, buyuk shaxslar, madaniyat, urushlar, arxeologiya bo'lsa)
- "nature" (agar tibbiyot, sog'liqni saqlash, biologiya, ekologiya, tabiat, qishloq xo'jaligi bo'lsa)
- "business" (agar biznes, iqtisodiyot, marketing, moliya, investitsiya, savdo, menejment bo'lsa)
- "science" (agar fizika, matematika, kimyo, astronomiya, aniq fanlar bo'lsa)
- "art" (agar san'at, musiqa, dizayn, adabiyot, madaniyat bo'lsa)
- "dark" (agar qora fon, premium, tungi mavzu bo'lsa)
- "canva_pastel" (agar nozik, pastel, zamonaviy ranglar bo'lsa)
- "blue" (agar boshqa umumiy mavzular bo'lsa)

Quyidagi qat'iy JSON formatida taqdimot rejasini, har bir slayd matnini, xulosasini, manbalarini va mavzuga mos rasmlar uchun inglizcha aniq qidiruv so'zlarini tuzib bering:
{{
  "title": "Taqdimotning to'liq va jozibador akademik sarlavhasi",
  "subtitle": "Qisqa izoh yoki ilmiy yo'nalishi",
  "theme": "tech / history / nature / business / science / art / dark / canva_pastel / blue dan biri",
  "cover_image_query": "Taqdimot muqovasi (titul slayd) uchun inglizcha 2-3 ta aniq qidiruv so'zi (masalan: 'artificial intelligence computer' yoki 'Amir Timur history')",
  "student_details": {{
    "university": "OTM / Universitet yoki institut nomi (agar kiritilgan bo'lsa)",
    "faculty": "Fakultet nomi (agar kiritilgan bo'lsa)",
    "direction": "Ta'lim yo'nalishi (agar kiritilgan bo'lsa)",
    "group": "Guruh yoki kurs (agar kiritilgan bo'lsa)",
    "student": "Bajardi: Talaba ismi va familiyasi (agar kiritilgan bo'lsa)",
    "teacher": "Qabul qildi: O'qituvchi ismi va familiyasi (agar kiritilgan bo'lsa)"
  }},
  "agenda": [
    "Foydalanuvchi mavzusining 1-asosiy yo'nalishi",
    "Foydalanuvchi mavzusining 2-asosiy yo'nalishi",
    "Foydalanuvchi mavzusining 3-asosiy yo'nalishi",
    "Foydalanuvchi mavzusining 4-asosiy yo'nalishi"
  ],
  "slides": [
    {{
      "slide_number": 1,
      "type": "content",
      "layout": "standard / kpi / comparison / steps",
      "title": "Foydalanuvchi yuborgan mavzuning 1-yo'nalishi bo'yicha aniq mazmuniy sarlavha",
      "kpi_items": [
        {{"number": "85%", "label": "Ko'rsatkich yoki statistika tavsifi"}},
        {{"number": "2.4x", "label": "Ko'rsatkich yoki statistika tavsifi"}},
        {{"number": "100+", "label": "Ko'rsatkich yoki statistika tavsifi"}}
      ],
      "comparison_data": {{
        "col1_title": "1-yo'nalish yoki an'anaviy yondashuv",
        "col1_points": ["1-muhim jihat", "2-muhim jihat"],
        "col2_title": "2-yo'nalish yoki innovatsion yondashuv",
        "col2_points": ["1-muhim jihat", "2-muhim jihat"]
      }},
      "steps_data": [
        {{"step": "01", "title": "1-bosqich nomi", "desc": "Qisqa tushuntirish"}},
        {{"step": "02", "title": "2-bosqich nomi", "desc": "Qisqa tushuntirish"}},
        {{"step": "03", "title": "3-bosqich nomi", "desc": "Qisqa tushuntirish"}}
      ],
      "bullet_points": [
        "1-muhim tushuncha: Mazkur tushunchaning ilmiy-amaliy mohiyati va faktlar bilan boyitilgan batafsil tushuntirishi",
        "2-muhim tushuncha: Aniq raqamlar, qonuniyatlar yoki statistik ma'lumotlar bilan tahlil",
        "3-muhim tushuncha: Sohadagi amaliy yondashuvlar va qiyosiy xulosa",
        "4-muhim tushuncha: Zamonaviy rivojlanish omillari va istiqbolli jihatlar"
      ],
      "speaker_notes": "Talaba himoya paytida ushbu slaydni tushuntirganda doskada turib aytishi kerak bo'lgan 3-5 jumlalik jonli va ilmiy ma'ruza nutqi.",
      "image_query": "Ushbu slayd uchun mavzuga mos inglizcha 1-3 ta aniq qidiruv so'zi (masalan: 'neural network', 'samarkand architecture', 'human heart anatomy')"
    }}
  ],
  "conclusion": [
    "Asosiy ilmiy/amaliy xulosa 1",
    "Tahlillar natijasi bo'yicha xulosa 2",
    "Amaliyotga tatbiq etish yoki kelajak istiqbollari bo'yicha takliflar"
  ],
  "references": [
    "1. Mavzuga oid darslik yoki monografiya muallifi, kitob nomi, yili.",
    "2. O'zbekiston Respublikasi qonun hujjatlari yoki tegishli me'yoriy standartlar.",
    "3. Mavzuga oid zamonaviy ilmiy jurnal yoki nufuzli axborot manbasi (veb-resurs)."
  ]
}}

Talablar:
- Jami mazmuniy slaydlar soni ('slides' massivida) roppa-rosa {num_content} taga teng bo'lsin (kam ham, ko'p ham bo'lmasin).
- TAQDIMOT REJASI ("agenda"): QAT'IY RAVISHDA ENG KO'PI 4 TAdan 5 TAgacha umumlashtirilgan asosiy reja bandlaridan iborat bo'lsin (hech qachon 5 tadan oshmasin).
- DIZAYN VA LAYOUT XILMA-XILLIGI (MUHIM): Taqdimot bir xil zerikarli bullet point bo'lib qolmasligi uchun slaydlarga mos layout tanlang:
  * "kpi" — Asosiy raqamlar, statistika yoki foizlar bo'lgan slaydlarga (kamida 1 ta slaydda ishlating, 3 ta ko'rsatkich berilsin);
  * "comparison" — Taqqoslash, solishtirish yoki ijobiy/salbiy tomonlar bo'lgan slaydga (kamida 1 ta slaydda ishlating);
  * "steps" — Bosqichlar, jarayon yoki ketma-ketlik bo'lgan slaydga (agar mos kelsa);
  * "standard" — Boshqa umumiy mazmunli slaydlar uchun (bullet_points va rasm).
  Har bir slaydga qaysi layout tanlanganidan qat'i nazar har doim "bullet_points" va "speaker_notes" ham yozilsin!
- QAT'IY TALAB: Taqdimot sarlavhalarida, reja bandlarida, slayd matnlarida, xulosada, manbalarda va ma'ruza nutqida MUTLAQO HECH QANDAY emoji, stiker, piktogramma yoki smayliklar ISHLATILMASIN! Taqdimot sof akademik, rasmiy va ilmiy uslubda bo'lsin.
- Har bir mazmuniy slayd foydalanuvchi so'ragan mavzularni chuqur, qiziqarli, dalillarga asoslangan holda to'liq yoritib bersin.
- Har bir slaydda 3 tadan 5 tagacha sifatli band (bullet_points) bo'lsin. Har bir band "Kalit so'z: Batafsil tavsif va tahlil" ko'rinishida yozilsin.
- Har bir slaydga talabaning himoyasi uchun speaker_notes (ma'ruza nutqi) yozilsin.
- Har bir slaydga va muqovaga mos inglizcha aniq image_query yozilsin.
- "references" maydonida kamida 3-4 ta haqiqiy va ishonarli adabiyot/manba bo'lsin.
- "Taqdimot muallifi va OTM ma'lumotlari" berilgan bo'lsa, ularni aralashtirib yubormasdan, har birini o'z o'rniga aniq ajratib "student_details" obyektiga joylashtiring.
- Faqat to'g'ri JSON formatida javob bering.
"""

    models_to_try = [
        "gemini-3.5-flash-lite",
        "gemini-3.1-flash-lite",
        "gemini-3.1-flash-lite-preview",
        "gemini-flash-lite-latest",
        "gemini-3-flash-preview"
    ]
    last_error = None

    for model_name in models_to_try:
        try:
            logger.info(f"Slayd generatsiyasi boshlanmoqda: model={model_name}")
            response = await asyncio.wait_for(
                client.aio.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.7,
                        max_output_tokens=8192,
                        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
                    )
                ),
                timeout=50.0
            )
            data = safe_json_loads(response.text)
            
            # Mavzuga mos theme ni aniqlash
            if theme_choice and theme_choice != "auto" and theme_choice in THEMES:
                chosen_theme = theme_choice
            else:
                ai_theme = data.get("theme", "")
                chosen_theme = detect_theme(topic, ai_theme)
            data["theme"] = chosen_theme
            
            # Student details ni birlashtirish va boyitish (foydalanuvchi kiritgan ma'lumot ustun turadi)
            has_author_input = bool(author_info and author_info.strip())
            if has_author_input:
                parsed_py = smart_parse_student_details(author_info)
                ai_det = data.get("student_details", {}) or {}
                merged_details = {}
                for k in ["university", "faculty", "direction", "group", "student", "teacher"]:
                    user_val = str(parsed_py.get(k, "")).strip()
                    ai_val = str(ai_det.get(k, "")).strip()
                    if any(ph in ai_val.lower() for ph in ["agar kiritilgan", "kiritilmagan", "namuna"]):
                        ai_val = ""
                    val = user_val if user_val else ai_val
                    if k == "student":
                        val = clean_prefix(val, ["bajardi", "talaba", "talabasi", "muallif", "tayyorladi"])
                    elif k == "teacher":
                        val = clean_prefix(val, ["qabul qildi", "o'qituvchi", "oʻqituvchi", "ilmiy rahbar", "rahbar", "domla", "ustoz"])
                    elif k == "university":
                        val = clean_prefix(val, ["otm", "universitet", "institut"])
                    elif k == "faculty":
                        val = clean_prefix(val, ["fakultet", "fakulteti"])
                    elif k == "group":
                        val = clean_prefix(val, ["guruh", "guruhi", "kurs", "kursi"])
                    elif k == "direction":
                        val = clean_prefix(val, ["yo'nalish", "yoʻnalishi"])
                    merged_details[k] = val
                data["student_details"] = merged_details
            else:
                data["student_details"] = {}

            # References ni tozalash va ro'yxatga keltirish
            raw_refs = data.get("references", [])
            clean_refs = []
            if isinstance(raw_refs, str):
                clean_refs = [r.strip() for r in raw_refs.split("\n") if r.strip()]
            elif isinstance(raw_refs, list):
                for item in raw_refs:
                    if isinstance(item, str) and item.strip():
                        clean_refs.append(item.strip())
                    elif isinstance(item, dict):
                        clean_refs.append(" ".join(str(v) for v in item.values() if v).strip())
            data["references"] = clean_refs

            # Agenda (reja) ni tozalash va qat'iy eng ko'pi 5 taga cheklash
            raw_agenda = data.get("agenda", [])
            clean_agenda = []
            if isinstance(raw_agenda, str):
                clean_agenda = [re.sub(r"^\d+[\.\)\-\s]+", "", r).strip() for r in raw_agenda.split("\n") if r.strip()]
            elif isinstance(raw_agenda, list):
                for item in raw_agenda:
                    if isinstance(item, str) and item.strip():
                        clean_agenda.append(re.sub(r"^\d+[\.\)\-\s]+", "", item).strip())
                    elif isinstance(item, dict):
                        clean_agenda.append(re.sub(r"^\d+[\.\)\-\s]+", "", " ".join(str(v) for v in item.values() if v)).strip())
            clean_agenda = [a for a in clean_agenda if a][:5]
            data["agenda"] = clean_agenda

            # Slides sonini qat'iy cheklash va target_slide_count saqlash
            if "slides" in data and isinstance(data["slides"], list):
                data["slides"] = data["slides"][:num_content]
            data["target_slide_count"] = slide_count

            # Barcha matnlarni stiker va emojilardan tozalash
            data = clean_data_structure(data)

            data["language"] = language
            logger.info(f"{model_name} orqali slayd ma'lumotlari muvaffaqiyatli olindi!")
            return data
        except asyncio.TimeoutError:
            logger.warning(f"{model_name} 40 soniyada javob bermadi (timeout). Keyingi model sinab ko'rilmoqda...")
            last_error = TimeoutError(f"{model_name} javob bermadi (timeout)")
        except Exception as e:
            logger.warning(f"{model_name} orqali generatsiyada xatolik bo'ldi: {e}. Boshqa model sinab ko'rilmoqda...")
            last_error = e

    logger.error(f"Barcha modellar bo'yicha xatolik: {last_error}")
    raise last_error


def process_image(data: bytes, dst_path: str, target_w: int = 900, target_h: int = 1000, radius: int = 28) -> str:
    """Rasmni qirqadi, o'lchamini moslaydi va burchaklarini yumaloqlashtiradi."""
    tmp = dst_path + ".raw"
    with open(tmp, "wb") as f:
        f.write(data)
    try:
        im = Image.open(tmp).convert("RGBA")
        orig_w, orig_h = im.size
        target_ratio = target_w / target_h
        orig_ratio = orig_w / orig_h

        if orig_ratio > target_ratio:
            new_w = int(orig_h * target_ratio)
            offset = (orig_w - new_w) // 2
            im = im.crop((offset, 0, offset + new_w, orig_h))
        else:
            new_h = int(orig_w / target_ratio)
            offset = (orig_h - new_h) // 2
            im = im.crop((0, offset, orig_w, offset + new_h))

        im = im.resize((target_w, target_h), Image.Resampling.LANCZOS)
        
        mask = Image.new("L", (target_w, target_h), 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle((0, 0, target_w, target_h), radius=radius, fill=255)
        
        out = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
        out.paste(im, (0, 0), mask=mask)
        out.save(dst_path, "PNG")
        return dst_path
    finally:
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except Exception:
                pass

async def fetch_image_single(session: aiohttp.ClientSession, query: str, fallback_query: str, dst_path: str) -> str:
    """Wikimedia Commons yoki Wikipedia orqali mavzuga mos sifatli rasm qidiradi va yuklaydi."""
    headers = {"User-Agent": "SlaydGeneratorBot/2.0 (https://t.me/tagdimot_generator_bot; contact: admin@tagdimot.uz)"}
    candidates = []
    for raw in [query, fallback_query]:
        if not raw or len(raw.strip()) < 2:
            continue
        cleaned = "".join(c for c in raw if c.isalnum() or c.isspace()).strip()
        if cleaned and cleaned not in candidates:
            candidates.append(cleaned)
        words = cleaned.split()
        if len(words) > 2:
            short = " ".join(words[:2])
            if short not in candidates:
                candidates.append(short)

    for q_candidate in candidates:
        # 1. Wikimedia Commons search
        try:
            url = f"https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=search&gsrsearch={urllib.parse.quote(q_candidate)}&gsrnamespace=6&gsrlimit=4&prop=imageinfo&iiprop=url|mime&iiurlwidth=900"
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    pages = data.get("query", {}).get("pages", {})
                    for pid, p in pages.items():
                        title = p.get("title", "").lower()
                        if title.endswith(".pdf"):
                            continue
                        info = p.get("imageinfo", [{}])[0]
                        mime = info.get("mime", "")
                        if mime in ("image/jpeg", "image/png", "image/webp"):
                            thumb_url = info.get("thumburl") or info.get("url")
                            if thumb_url:
                                async with session.get(thumb_url, headers=headers, timeout=aiohttp.ClientTimeout(total=7)) as img_r:
                                    if img_r.status == 200:
                                        raw = await img_r.read()
                                        return await asyncio.to_thread(process_image, raw, dst_path)
        except Exception:
            pass

        # 2. Wikipedia search pageimages
        try:
            wiki_url = f"https://en.wikipedia.org/w/api.php?action=query&generator=search&gsrsearch={urllib.parse.quote(q_candidate)}&gsrlimit=3&prop=pageimages&piprop=thumbnail&pithumbsize=900&format=json"
            async with session.get(wiki_url, headers=headers, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    pages = data.get("query", {}).get("pages", {})
                    for pid, pdata in pages.items():
                        if "thumbnail" in pdata:
                            img_url = pdata["thumbnail"]["source"]
                            if img_url:
                                async with session.get(img_url, headers=headers, timeout=aiohttp.ClientTimeout(total=7)) as img_r:
                                    if img_r.status == 200:
                                        raw = await img_r.read()
                                        return await asyncio.to_thread(process_image, raw, dst_path)
        except Exception:
            pass

    return None

async def fetch_images_for_presentation(content: dict, temp_dir: str) -> dict:
    """Taqdimot muqovasi va har bir slayd uchun parallel ravishda mos rasmlarni yuklaydi."""
    title = content.get("title", "")
    cover_q = content.get("cover_image_query", "") or title
    slides_data = content.get("slides", [])

    tasks_info = []
    # Cover
    cover_dst = os.path.join(temp_dir, "cover.png")
    tasks_info.append(("cover", cover_q, title, cover_dst))

    # Slides
    for idx, s_data in enumerate(slides_data, 1):
        s_title = s_data.get("title", "")
        s_q = s_data.get("image_query", "") or s_title
        s_dst = os.path.join(temp_dir, f"slide_{idx}.png")
        tasks_info.append((idx, s_q, s_title, s_dst))

    images_map = {}
    conn = aiohttp.TCPConnector(family=socket.AF_INET)
    async with aiohttp.ClientSession(connector=conn) as session:
        coros = [
            fetch_image_single(session, q, fb, dst)
            for (key, q, fb, dst) in tasks_info
        ]
        results = await asyncio.gather(*coros, return_exceptions=True)

        for (key, _, _, _), res in zip(tasks_info, results):
            if isinstance(res, str) and os.path.exists(res):
                images_map[key] = res
            else:
                images_map[key] = None

    loaded_count = sum(1 for v in images_map.values() if v)
    logger.info(f"Muvaffaqiyatli yuklangan rasmlar soni: {loaded_count} / {len(tasks_info)}")
    return images_map

def convert_pptx_to_pdf(pptx_path: str, pdf_path: str = None) -> str:
    """LibreOffice headless yordamida PPTX faylini PDF ga o'giradi."""
    out_dir = os.path.dirname(pptx_path)
    base_name = os.path.splitext(os.path.basename(pptx_path))[0]
    expected_pdf = os.path.join(out_dir, f"{base_name}.pdf")
    
    user_install_dir = f"file://{out_dir}/lo_profile"
    cmd = [
        "soffice",
        f"-env:UserInstallation={user_install_dir}",
        "--headless",
        "--convert-to", "pdf",
        "--outdir", out_dir,
        pptx_path
    ]
    logger.info(f"PPTX fayl PDF ga aylantirilmoqda: {pptx_path} -> {expected_pdf}")
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if res.returncode != 0 or not os.path.exists(expected_pdf):
        logger.error(f"LibreOffice conversion failed (code {res.returncode}): {res.stderr}")
        raise RuntimeError(f"LibreOffice PDF konvertatsiyasida xatolik: {res.stderr}")

    if pdf_path and pdf_path != expected_pdf:
        shutil.move(expected_pdf, pdf_path)
        expected_pdf = pdf_path

    return expected_pdf

def convert_images_to_pdf(image_paths: list, output_pdf_path: str) -> str:
    """Rasmlarni (bir yoki bir nechta) yuqori sifatli PDF hujjatga aylantiradi."""
    images = []
    for path in image_paths:
        try:
            img = Image.open(path)
            if img.mode in ("RGBA", "LA", "P"):
                bg = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "RGBA":
                    bg.paste(img, mask=img.split()[3])
                else:
                    bg.paste(img.convert("RGBA"))
                images.append(bg)
            else:
                images.append(img.convert("RGB"))
        except Exception as e:
            logger.warning(f"Rasm ochishda xatolik ({path}): {e}")
            
    if not images:
        raise ValueError("Hech qanday to'g'ri rasm topilmadi")

    first = images[0]
    rest = images[1:]
    first.save(output_pdf_path, "PDF", resolution=100.0, save_all=True, append_images=rest)
    return output_pdf_path

def _add_styled_bullet(text_frame, bullet_text: str, theme: dict, font_size: Pt, space_after: Pt, is_first: bool = False):
    """Slayd matn bandini kalit so'zlarni qalin qilib, yuqori sifatli infografika uslubida joylash."""
    p = text_frame.paragraphs[0] if is_first else text_frame.add_paragraph()
    p.space_after = space_after

    clean_txt = re.sub(r"^[\s•\-\*–—\d\.\)]+", "", remove_emojis(str(bullet_text))).strip()
    if not clean_txt:
        return

    is_dark = (
        theme.get("tag") == "PREMIUM DARK" or
        theme.get("bg_slide") == RGBColor(24, 24, 27) or
        "qora" in theme.get("name", "").lower()
    )

    lead_color = theme["accent"] if is_dark else theme.get("primary", theme["text_dark"])
    body_color = theme["white"] if is_dark else theme["text_dark"]

    # Bullet ikonkasi
    r_icon = p.add_run()
    r_icon.text = f"{theme.get('bullet_icon', '✦')}  "
    r_icon.font.bold = True
    r_icon.font.size = font_size
    r_icon.font.color.rgb = theme["accent"]
    r_icon.font.name = "Arial"

    # Kalit so'z va tavsifni ajratish (masalan: "Kalit so'z: Tavsif matni" yoki "Bosqich — Izoh")
    match = re.match(r"^([^:—–\-]{3,35}[:—–\-])\s*(.*)$", clean_txt)
    if match:
        lead, rest = match.groups()
        r_lead = p.add_run()
        r_lead.text = f"{lead} "
        r_lead.font.bold = True
        r_lead.font.size = font_size
        r_lead.font.color.rgb = lead_color
        r_lead.font.name = "Arial"

        if rest:
            r_rest = p.add_run()
            r_rest.text = rest
            r_rest.font.bold = False
            r_rest.font.size = font_size
            r_rest.font.color.rgb = body_color
            r_rest.font.name = "Arial"
    else:
        words = clean_txt.split()
        if len(words) > 4:
            lead = " ".join(words[:2]) + " "
            rest = " ".join(words[2:])
            r_lead = p.add_run()
            r_lead.text = lead
            r_lead.font.bold = True
            r_lead.font.size = font_size
            r_lead.font.color.rgb = lead_color
            r_lead.font.name = "Arial"

            r_rest = p.add_run()
            r_rest.text = rest
            r_rest.font.bold = False
            r_rest.font.size = font_size
            r_rest.font.color.rgb = body_color
            r_rest.font.name = "Arial"
        else:
            r = p.add_run()
            r.text = clean_txt
            r.font.bold = False
            r.font.size = font_size
            r.font.color.rgb = body_color
            r.font.name = "Arial"

def _add_header(slide, title_text: str, theme: dict, slide_num: int = None, total_slides: int = None, category: str = "ILMIY TAQDIMOT"):
    """Slaydning yuqori qismiga zamonaviy sarlavha va stilistika qo'shish."""
    banner_h = Inches(1.15)
    top_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), banner_h)
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = theme["primary"]
    top_bar.line.fill.background()

    # Sleek bottom accent line
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, banner_h, Inches(13.333), Inches(0.06))
    line.fill.solid()
    line.fill.fore_color.rgb = theme["accent"]
    line.line.fill.background()

    # Category breadcrumb (hech qachon bot ichki tema nomini chiqarmaymiz)
    if not category:
        category = "ILMIY TAQDIMOT"
    tag_tb = slide.shapes.add_textbox(Inches(0.9), Inches(0.12), Inches(8.5), Inches(0.28))
    tag_tf = tag_tb.text_frame
    tag_tf.word_wrap = True
    tag_p = tag_tf.paragraphs[0]
    tag_p.text = f"✦  {category.upper()}"
    tag_p.font.size = Pt(10)
    tag_p.font.bold = True
    tag_p.font.color.rgb = theme["accent"]
    tag_p.font.name = "Arial"

    # Header title text
    tb = slide.shapes.add_textbox(Inches(0.9), Inches(0.38), Inches(9.8), Inches(0.72))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = remove_emojis(title_text)
    p.font.size = Pt(22 if len(title_text) > 40 else 24)
    p.font.bold = True
    p.font.color.rgb = theme["white"]
    p.font.name = "Arial"

    # Slide number badge pill
    if slide_num and total_slides:
        badge_w = Inches(1.3)
        badge_h = Inches(0.42)
        badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(11.1), Inches(0.36), badge_w, badge_h)
        badge.fill.solid()
        badge.fill.fore_color.rgb = theme["accent"]
        badge.line.fill.background()
        btf = badge.text_frame
        bp = btf.paragraphs[0]
        bp.text = f"{slide_num:02d} / {total_slides:02d}"
        bp.font.size = Pt(12)
        bp.font.bold = True
        bp.font.color.rgb = RGBColor(255, 255, 255)
        bp.alignment = PP_ALIGN.CENTER

def _create_hero_slide(prs, blank_layout, theme, title_text, subtitle_text, total_slides, is_dark, custom_bg, images_map, lang_info=None):
    """Foydalanuvchi muallif kiritmagan holatda 1-slayd uchun zamonaviy Hero Master Slide chizadi."""
    if not lang_info:
        lang_info = locales.get_slide_lang_info("uz")
    topic_slide = prs.slides.add_slide(blank_layout)
    if custom_bg and os.path.exists(custom_bg):
        topic_slide.shapes.add_picture(custom_bg, 0, 0, width=Inches(13.333), height=Inches(7.5))
    else:
        bg_topic = topic_slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg_topic.fill.solid()
        bg_topic.fill.fore_color.rgb = theme["bg_slide"]
        bg_topic.line.fill.background()

    # Top accent bar across full width
    top_acc = topic_slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(0.2))
    top_acc.fill.solid()
    top_acc.fill.fore_color.rgb = theme["accent"]
    top_acc.line.fill.background()

    # Capsule Badge
    b_tag = topic_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), Inches(0.7), Inches(2.9), Inches(0.42))
    b_tag.fill.solid()
    b_tag.fill.fore_color.rgb = theme["primary"]
    b_tag.line.fill.background()
    bp = b_tag.text_frame.paragraphs[0]
    bp.text = f"✦  {lang_info.get('work_title', 'ILMIY TAQDIMOT')[:20]}"
    bp.font.size = Pt(11)
    bp.font.bold = True
    bp.font.color.rgb = theme["accent"]
    bp.alignment = PP_ALIGN.CENTER

    # Pill slide number on top right
    num_badge = topic_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(11.1), Inches(0.7), Inches(1.3), Inches(0.42))
    num_badge.fill.solid()
    num_badge.fill.fore_color.rgb = theme["accent"]
    num_badge.line.fill.background()
    nb_p = num_badge.text_frame.paragraphs[0]
    nb_p.text = f"01 / {total_slides:02d}"
    nb_p.font.size = Pt(12)
    nb_p.font.bold = True
    nb_p.font.color.rgb = RGBColor(255, 255, 255)
    nb_p.alignment = PP_ALIGN.CENTER

    cover_img = images_map.get("cover") if images_map else None
    if cover_img and os.path.exists(cover_img):
        t_box = topic_slide.shapes.add_textbox(Inches(0.9), Inches(1.25), Inches(7.0), Inches(1.8))
        t_tf = t_box.text_frame
        t_tf.word_wrap = True
        p_t = t_tf.paragraphs[0]
        p_t.text = remove_emojis(title_text)
        p_t.font.size = Pt(26 if len(title_text) > 40 else 30)
        p_t.font.bold = True
        p_t.font.color.rgb = theme["primary"] if not is_dark else theme["accent"]
        p_t.font.name = "Arial"

        if subtitle_text:
            p_sub = t_tf.add_paragraph()
            p_sub.text = remove_emojis(subtitle_text)
            p_sub.font.size = Pt(14)
            p_sub.font.color.rgb = theme["text_muted"]
            p_sub.font.name = "Arial"
            p_sub.space_before = Pt(6)

        card_l = topic_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), Inches(3.25), Inches(7.0), Inches(3.8))
        card_l.fill.solid()
        card_l.fill.fore_color.rgb = theme["card_bg"]
        card_l.line.color.rgb = theme["card_border"]
        card_l.line.width = Pt(1.5)

        cl_tf = card_l.text_frame
        cl_tf.word_wrap = True
        cl_tf.margin_left = Inches(0.4)
        cl_tf.margin_top = Inches(0.25)
        cl_tf.margin_right = Inches(0.4)

        pillars = [
            ("Maqsadi:", "Mavzuning nazariy va amaliy asoslarini chuqur tahlil qilish hamda tizimlashtirish."),
            ("Dolzarbligi:", "Sohadagi zamonaviy tendensiyalar va dolzarb masalalarga ilmiy yechim topish."),
            ("Kutilayotgan natija:", "Aniq xulosalar va amaliyotga tatbiq etish mumkin boʻlgan takliflar ishlab chiqish.")
        ]
        for pi_idx, (p_label, p_desc) in enumerate(pillars):
            p = cl_tf.paragraphs[0] if pi_idx == 0 else cl_tf.add_paragraph()
            p.space_after = Pt(12)
            r_icon = p.add_run()
            r_icon.text = "✦  "
            r_icon.font.bold = True
            r_icon.font.size = Pt(13)
            r_icon.font.color.rgb = theme["accent"]
            
            r_lbl = p.add_run()
            r_lbl.text = f"{p_label} "
            r_lbl.font.bold = True
            r_lbl.font.size = Pt(13)
            r_lbl.font.color.rgb = theme["primary"] if not is_dark else theme["accent"]

            r_txt = p.add_run()
            r_txt.text = p_desc
            r_txt.font.bold = False
            r_txt.font.size = Pt(13)
            r_txt.font.color.rgb = theme["text_dark"]

        try:
            topic_slide.shapes.add_picture(cover_img, Inches(8.3), Inches(1.3), width=Inches(4.1), height=Inches(5.75))
        except Exception:
            pass
    else:
        card_full = topic_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), Inches(1.3), Inches(11.533), Inches(5.75))
        card_full.fill.solid()
        card_full.fill.fore_color.rgb = theme["card_bg"]
        card_full.line.color.rgb = theme["card_border"]
        card_full.line.width = Pt(1.5)

        t_box = topic_slide.shapes.add_textbox(Inches(1.3), Inches(1.6), Inches(10.7), Inches(2.2))
        t_tf = t_box.text_frame
        t_tf.word_wrap = True

        p_t = t_tf.paragraphs[0]
        p_t.text = remove_emojis(title_text)
        p_t.font.size = Pt(32 if len(title_text) > 40 else 36)
        p_t.font.bold = True
        p_t.font.color.rgb = theme["primary"] if not is_dark else theme["accent"]
        p_t.font.name = "Arial"
        p_t.alignment = PP_ALIGN.CENTER

        if subtitle_text:
            p_sub = t_tf.add_paragraph()
            p_sub.text = remove_emojis(subtitle_text)
            p_sub.font.size = Pt(16)
            p_sub.font.color.rgb = theme["text_muted"]
            p_sub.font.name = "Arial"
            p_sub.space_before = Pt(8)
            p_sub.alignment = PP_ALIGN.CENTER

        p_start_x = Inches(1.3)
        p_w = Inches(3.35)
        p_gap = Inches(0.32)
        p_y = Inches(4.1)
        p_h = Inches(2.5)

        pillars = [
            ("Mavzu Maqsadi", "Ushbu tadqiqotda mavzuning nazariy va amaliy asoslari tizimli yoritib beriladi."),
            ("Dolzarbligi", "Zamonaviy rivojlanish bosqichida mazkur sohadagi masalalarga ilmiy yechim topish."),
            ("Kutilayotgan Natija", "Aniq tahlillar, statistik ko'rsatkichlar va amaliy tavsiyalar majmuasi.")
        ]

        for p_i, (p_title, p_body) in enumerate(pillars):
            px = p_start_x + p_i * (p_w + p_gap)
            p_card = topic_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, px, p_y, p_w, p_h)
            p_card.fill.solid()
            p_card.fill.fore_color.rgb = theme["bg_slide"]
            p_card.line.color.rgb = theme["accent"] if p_i == 0 else theme["card_border"]
            p_card.line.width = Pt(1.5)

            p_box = topic_slide.shapes.add_textbox(px + Inches(0.2), p_y + Inches(0.2), p_w - Inches(0.4), p_h - Inches(0.4))
            ptf = p_box.text_frame
            ptf.word_wrap = True
            pp1 = ptf.paragraphs[0]
            pp1.text = f"✦  {p_title}"
            pp1.font.size = Pt(14)
            pp1.font.bold = True
            pp1.font.color.rgb = theme["accent"] if not is_dark else theme["white"]
            pp1.alignment = PP_ALIGN.CENTER
            pp1.space_after = Pt(8)

            pp2 = ptf.add_paragraph()
            pp2.text = p_body
            pp2.font.size = Pt(13)
            pp2.font.color.rgb = theme["text_dark"]
            pp2.alignment = PP_ALIGN.CENTER
    return topic_slide

def _create_agenda_slide(prs, blank_layout, theme, content, slides_data, total_slides, custom_bg, lang_info):
    """2-slayd sifatida Infografik Reja (Agenda / Mundarija) slaydi chizadi."""
    reja_slide = prs.slides.add_slide(blank_layout)
    if custom_bg and os.path.exists(custom_bg):
        reja_slide.shapes.add_picture(custom_bg, 0, 0, width=Inches(13.333), height=Inches(7.5))
    else:
        bg_reja = reja_slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg_reja.fill.solid()
        bg_reja.fill.fore_color.rgb = theme["bg_slide"]
        bg_reja.line.fill.background()

    _add_header(reja_slide, lang_info["agenda"], theme, slide_num=2, total_slides=total_slides, category=lang_info["agenda"].upper())

    raw_agenda = content.get("agenda")
    agenda_items = []
    if isinstance(raw_agenda, list) and raw_agenda:
        for it in raw_agenda:
            if isinstance(it, str) and it.strip():
                cleaned = re.sub(r"^\d+[\.\)\-\s]+", "", it.strip()).strip()
                if cleaned:
                    agenda_items.append(cleaned)
    elif isinstance(raw_agenda, str) and raw_agenda.strip():
        for line in raw_agenda.split("\n"):
            cleaned = re.sub(r"^\d+[\.\)\-\s]+", "", line.strip()).strip()
            if cleaned:
                agenda_items.append(cleaned)

    if not agenda_items:
        for s in slides_data[:5]:
            t = re.sub(r"^\d+[\.\)\-\s]+", "", s.get("title", "")).strip()
            if t and t not in agenda_items:
                agenda_items.append(t)
        if len(agenda_items) < 3:
            agenda_items.append(lang_info.get("conclusion", "Xulosa va asosiy natijalar"))
            agenda_items.append(lang_info.get("references", "Foydalanilgan adabiyotlar va manbalar"))

    agenda_items = [a for a in agenda_items if a][:5]
    content["agenda"] = agenda_items

    n_items = len(agenda_items)
    card_w = Inches(11.533)
    card_h = Inches(0.85 if n_items == 5 else 1.0)
    gap = Inches(0.18 if n_items == 5 else 0.25)
    start_y = Inches(1.65 if n_items == 5 else 1.8)

    for i, item_text in enumerate(agenda_items):
        y = start_y + i * (card_h + gap)
        ag_card = reja_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), y, card_w, card_h)
        ag_card.fill.solid()
        ag_card.fill.fore_color.rgb = theme["card_bg"]
        ag_card.line.color.rgb = theme["card_border"]
        ag_card.line.width = Pt(1.5)

        circ = reja_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.15), y + (card_h - Inches(0.55)) / 2, Inches(0.85), Inches(0.55))
        circ.fill.solid()
        circ.fill.fore_color.rgb = theme["accent"]
        circ.line.fill.background()
        cp = circ.text_frame.paragraphs[0]
        cp.text = f"{i+1:02d}"
        cp.font.size = Pt(14)
        cp.font.bold = True
        cp.font.color.rgb = RGBColor(255, 255, 255)
        cp.alignment = PP_ALIGN.CENTER

        ag_tb = reja_slide.shapes.add_textbox(Inches(2.2), y + (card_h - Inches(0.55)) / 2, Inches(9.3), Inches(0.55))
        ag_tf = ag_tb.text_frame
        ag_tf.word_wrap = True
        ag_p = ag_tf.paragraphs[0]
        ag_p.text = item_text
        ag_p.font.size = Pt(17 if n_items == 5 else 19)
        ag_p.font.bold = True
        ag_p.font.color.rgb = theme["text_dark"]
        ag_p.font.name = "Arial"

        arr_b = reja_slide.shapes.add_textbox(Inches(11.8), y + (card_h - Inches(0.55)) / 2, Inches(0.5), Inches(0.55))
        arr_p = arr_b.text_frame.paragraphs[0]
        arr_p.text = "➔"
        arr_p.font.size = Pt(16)
        arr_p.font.bold = True
        arr_p.font.color.rgb = theme["accent"]
    return reja_slide

def _create_thanks_slide(prs, blank_layout, theme, custom_bg, is_white, is_dark, lang_info, presenter_str: str = ""):
    """Yakuniy Minnatdorchilik slaydi chizadi."""
    end_slide = prs.slides.add_slide(blank_layout)
    if custom_bg and os.path.exists(custom_bg):
        end_slide.shapes.add_picture(custom_bg, 0, 0, width=Inches(13.333), height=Inches(7.5))
    else:
        bg_end = end_slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg_end.fill.solid()
        if is_white:
            bg_end.fill.fore_color.rgb = RGBColor(248, 250, 252)
        else:
            bg_end.fill.fore_color.rgb = theme["primary"]
        bg_end.line.fill.background()

    end_bar = end_slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(0.35))
    end_bar.fill.solid()
    end_bar.fill.fore_color.rgb = theme["accent"]
    end_bar.line.fill.background()

    card_w = Inches(10.5)
    card_h = Inches(5.2)
    card_l = Inches(1.416)
    card_t = Inches(1.3)

    end_card = end_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, card_l, card_t, card_w, card_h)
    end_card.fill.solid()
    end_card.fill.fore_color.rgb = theme["card_bg"]
    end_card.line.color.rgb = theme["accent"]
    end_card.line.width = Pt(2.5)

    end_box = end_slide.shapes.add_textbox(card_l + Inches(0.4), card_t + Inches(0.35), card_w - Inches(0.8), card_h - Inches(0.7))
    end_tf = end_box.text_frame
    end_tf.word_wrap = True
    end_tf.margin_top = Inches(0.15)
    end_tf.margin_bottom = Inches(0.15)
    end_tf.margin_left = Inches(0.15)
    end_tf.margin_right = Inches(0.15)

    p_badge = end_tf.paragraphs[0]
    p_badge.text = "✦  YAKUNIY MINNATDORCHILIK  ✦"
    p_badge.font.size = Pt(13)
    p_badge.font.bold = True
    p_badge.font.color.rgb = theme["accent"]
    p_badge.font.name = "Arial"
    p_badge.alignment = PP_ALIGN.CENTER
    p_badge.space_after = Pt(14)

    ep1 = end_tf.add_paragraph()
    ep1.text = lang_info["thanks"].upper()
    ep1.font.size = Pt(38)
    ep1.font.bold = True
    ep1.font.color.rgb = theme["accent"] if is_dark else theme["primary"]
    ep1.font.name = "Arial"
    ep1.alignment = PP_ALIGN.CENTER
    ep1.space_after = Pt(12)

    ep2 = end_tf.add_paragraph()
    ep2.text = lang_info.get("questions_welcome", "Savollar, fikr-mulohazalar va muhokama uchun tayyorman")
    ep2.font.size = Pt(18)
    ep2.font.bold = False
    ep2.font.color.rgb = theme["accent"] if is_dark else theme.get("accent_secondary", theme["accent"])
    ep2.font.name = "Arial"
    ep2.alignment = PP_ALIGN.CENTER
    ep2.space_after = Pt(16)

    if presenter_str:
        ep3 = end_tf.add_paragraph()
        ep3.text = presenter_str
        ep3.font.size = Pt(14)
        ep3.font.bold = True
        ep3.font.color.rgb = theme["text_dark"] if not is_dark else theme["white"]
        ep3.font.name = "Arial"
        ep3.alignment = PP_ALIGN.CENTER

    return end_slide

def create_pptx_file(content: dict, output_path: str, theme_name: str = "", images_map: dict = None, author_info: str = "", default_student_name: str = "", custom_bg: str = None, language: str = "", target_slide_count: int = 0) -> str:
    """Creates a beautiful 16:9 PowerPoint file with student academic structure, author info, references, and closing slides."""
    content = clean_data_structure(content)
    lang_code = language or content.get("language", "uz")
    lang_info = locales.get_slide_lang_info(lang_code)
    if not theme_name or theme_name not in THEMES:
        theme_name = content.get("theme", "blue")
    theme = THEMES.get(theme_name, THEMES["blue"])
    is_dark = (theme_name == "dark")
    is_white = (theme_name == "white")

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]
    
    title_text = content.get("title", "Taqdimot")
    subtitle_text = content.get("subtitle", "")
    slides_data = content.get("slides", [])
    conclusion_points = content.get("conclusion", [])
    raw_refs = content.get("references", [])
    
    has_author = bool(author_info and author_info.strip())

    # Jami talab qilingan slaydlar soni (belgilangandan 1 list ham oshmasin)
    if not target_slide_count or target_slide_count < 3:
        target_slide_count = content.get("target_slide_count") or 8
    total_slides = target_slide_count

    has_agenda_slide, intro_count, closing_count, target_content_count = calculate_slide_distribution(total_slides)
    slides_data = slides_data[:target_content_count]

    if has_author:
        # Structured student details
        student_details = content.get("student_details") or smart_parse_student_details(author_info)
        uni_name = (student_details.get("university") or "").strip()
        faculty_name = (student_details.get("faculty") or "").strip()
        student_name = (student_details.get("student") or "").strip()
        direction_val = (student_details.get("direction") or "").strip()
        group_val = (student_details.get("group") or "").strip()
        teacher_name = (student_details.get("teacher") or "").strip()

        student_name = clean_prefix(student_name, ["bajardi", "talaba", "talabasi", "muallif", "tayyorladi"])
        teacher_name = clean_prefix(teacher_name, ["qabul qildi", "o'qituvchi", "oʻqituvchi", "ilmiy rahbar", "rahbar", "domla", "ustoz"])
        uni_name = clean_prefix(uni_name, ["otm", "universitet", "institut"])
        faculty_name = clean_prefix(faculty_name, ["fakultet", "fakulteti"])
        group_val = clean_prefix(group_val, ["guruh", "guruhi", "kurs", "kursi"])
        direction_val = clean_prefix(direction_val, ["yo'nalish", "yoʻnalishi"])

        if not student_name and default_student_name:
            student_name = default_student_name

        # Display texts (OTM, Fakultet, Yoʻnalish, Guruh, Talaba, Ilmiy rahbar tagma-tag to'liq chiqadi)
        display_uni = uni_name if uni_name else lang_info.get("uni_label", "Oliy taʼlim muassasasi")
        display_fac = faculty_name if faculty_name else lang_info.get("faculty_label", "Fakultet va kafedra")
        display_dir = direction_val if direction_val else lang_info.get("direction_label", "Taʼlim yoʻnalishi")
        display_group = group_val if group_val else lang_info.get("group_label", "Akademik guruh")
        display_student = student_name if student_name else lang_info.get("student_label", "Talaba (Muallif)")
        display_teacher = teacher_name if teacher_name else lang_info.get("teacher_label", "Ilmiy rahbar / Oʻqituvchi")

        # ================= 1. TITUL SLAYD (RASMIY TITUL VARAQASI) =================
        slide = prs.slides.add_slide(blank_layout)
        
        # Background: Custom photo or theme color
        if custom_bg and os.path.exists(custom_bg):
            slide.shapes.add_picture(custom_bg, 0, 0, width=Inches(13.333), height=Inches(7.5))
        else:
            bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
            bg.fill.solid()
            if is_white:
                bg.fill.fore_color.rgb = RGBColor(248, 250, 252)
            else:
                bg.fill.fore_color.rgb = theme["primary"]
            bg.line.fill.background()

        # Decorative top bar
        bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(0.2))
        bar.fill.solid()
        bar.fill.fore_color.rgb = theme["accent"]
        bar.line.fill.background()

        # Top Ministry Header Text
        top_tb = slide.shapes.add_textbox(Inches(1.0), Inches(0.35), Inches(11.333), Inches(0.65))
        top_tf = top_tb.text_frame
        top_tf.word_wrap = True
        p_min = top_tf.paragraphs[0]
        p_min.text = lang_info.get("ministry", "OʻZBEKISTON RESPUBLIKASI OLIY TAʼLIM, FAN VA INNOVATSIYALAR VAZIRLIGI")
        p_min.font.size = Pt(13)
        p_min.font.bold = True
        p_min.font.color.rgb = theme["primary"] if is_white else theme["accent"]
        p_min.font.name = "Arial"
        p_min.alignment = PP_ALIGN.CENTER

        # Slide number badge
        num_tb = slide.shapes.add_textbox(Inches(10.5), Inches(0.35), Inches(2.2), Inches(0.5))
        num_tf = num_tb.text_frame
        num_p = num_tf.paragraphs[0]
        num_p.text = f"01 / {total_slides:02d}"
        num_p.font.size = Pt(14)
        num_p.font.bold = True
        num_p.font.color.rgb = theme["primary"] if is_white else theme["accent"]
        num_p.alignment = PP_ALIGN.RIGHT

        # Centered Academic Title Card on Slide 1
        card_w = Inches(10.8)
        card_h = Inches(5.6)
        card_left = Inches(1.266)  # (13.333 - 10.8) / 2
        card_top = Inches(1.15)

        titul_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, card_left, card_top, card_w, card_h)
        titul_card.fill.solid()
        if is_dark:
            titul_card.fill.fore_color.rgb = RGBColor(30, 30, 35)
            titul_card.line.color.rgb = theme["accent"]
        elif custom_bg:
            titul_card.fill.fore_color.rgb = RGBColor(255, 255, 255)
            titul_card.line.color.rgb = theme["accent"]
        else:
            titul_card.fill.fore_color.rgb = theme.get("card_bg", RGBColor(255, 255, 255))
            titul_card.line.color.rgb = theme.get("card_border", theme["accent"])
        titul_card.line.width = Pt(2.0)

        c_tf = titul_card.text_frame
        c_tf.word_wrap = True
        c_tf.margin_left = Inches(0.6)
        c_tf.margin_right = Inches(0.6)
        c_tf.margin_top = Inches(0.3)
        c_tf.margin_bottom = Inches(0.3)

        # Card Title
        p_head = c_tf.paragraphs[0]
        p_head.text = lang_info.get("work_title", "OLIY TAʼLIM MUASSASASI TALABASINING TAQDIMOT ISHI")
        p_head.font.size = Pt(14)
        p_head.font.bold = True
        p_head.font.color.rgb = theme["accent"] if is_dark else theme["primary"]
        p_head.font.name = "Arial"
        p_head.alignment = PP_ALIGN.CENTER
        p_head.space_after = Pt(8)

        # Topic Title
        p_topic = c_tf.add_paragraph()
        topic_lbl = lang_info.get("topic_label", "Mavzu")
        p_topic.text = f"{topic_lbl}: {remove_emojis(title_text)}"
        p_topic.font.size = Pt(16)
        p_topic.font.bold = True
        p_topic.font.color.rgb = theme["accent"] if is_dark else theme["primary"]
        p_topic.font.name = "Arial"
        p_topic.alignment = PP_ALIGN.CENTER
        p_topic.space_after = Pt(10)

        # All fields tagma-tag (line-by-line stacked vertically)
        fields = [
            (lang_info.get("uni_label", "OTM (Taʼlim muassasasi)") + ":", display_uni),
            (lang_info.get("faculty_label", "Fakultet (Kafedra)") + ":", display_fac),
            (lang_info.get("direction_label", "Taʼlim yoʻnalishi") + ":", display_dir),
            (lang_info.get("group_label", "Akademik guruh") + ":", display_group),
            (lang_info.get("student_label", "Bajardi (Talaba)") + ":", display_student),
            (lang_info.get("teacher_label", "Qabul qildi (Ilmiy rahbar)") + ":", display_teacher),
        ]

        for lbl, val in fields:
            p_field = c_tf.add_paragraph()
            p_field.space_after = Pt(10)
            
            r_lbl = p_field.add_run()
            r_lbl.text = f"{lbl}   "
            r_lbl.font.bold = True
            r_lbl.font.size = Pt(15)
            r_lbl.font.color.rgb = theme["accent"] if is_dark else theme["primary"]
            r_lbl.font.name = "Arial"

            r_val = p_field.add_run()
            r_val.text = val
            r_val.font.bold = True
            r_val.font.size = Pt(15)
            r_val.font.color.rgb = theme["text_dark"]
            r_val.font.name = "Arial"

        # Bottom footer: Toshkent - current year
        current_year = datetime.now().year
        p_foot = c_tf.add_paragraph()
        city_label = lang_info.get("city_year", "Toshkent")
        p_foot.text = f"{city_label} — {current_year}"
        p_foot.font.size = Pt(13)
        p_foot.font.bold = True
        p_foot.font.color.rgb = theme["accent"] if is_dark else theme["text_muted"]
        p_foot.font.name = "Arial"
        p_foot.alignment = PP_ALIGN.CENTER
        p_foot.space_before = Pt(14)
    else:
        student_name = teacher_name = uni_name = faculty_name = group_val = direction_val = ""

    # Slide 1: Agar muallif ma'lumotlari kiritilmagan bo'lsa, Hero Master Slide yaratiladi
    if not has_author:
        _create_hero_slide(prs, blank_layout, theme, title_text, subtitle_text, total_slides, is_dark, custom_bg, images_map, lang_info)

    # Slide 2: Mundarija / Reja slaydi (agar jami slaydlar 5 yoki undan ortiq bo'lsa)
    if has_agenda_slide:
        _create_agenda_slide(prs, blank_layout, theme, content, slides_data, total_slides, custom_bg, lang_info)

    # Agar sun'iy intellekt taqdim etgan mazmun slaydlari yetarli bo'lmasa, to'ldiramiz
    while len(slides_data) < target_content_count:
        pad_idx = len(slides_data) + 1
        lang_name = lang_info.get("name", "")
        if "Русский" in lang_name:
            p_title = f"Практические аспекты и развитие темы ({pad_idx})"
            p_pts = [
                "Перспективы углубления научно-практических исследований.",
                "Механизмы внедрения в практику и оценка эффективности.",
                "Использование современных технологий и инноваций."
            ]
        elif "English" in lang_name:
            p_title = f"Practical Applications & Insights ({pad_idx})"
            p_pts = [
                "Key perspectives and future research development.",
                "Implementation mechanisms and performance analysis.",
                "Application of modern technology and innovative practices."
            ]
        else:
            p_title = f"Mavzuni rivojlantirish va amaliy tavsiyalar ({pad_idx})"
            p_pts = [
                "Mavzu bo'yicha ilmiy-amaliy tadqiqotlarni chuqurlashtirish istiqbollari.",
                "Amaliyotga tatbiq etish mexanizmlari va samaradorlik ko'rsatkichlari.",
                "Sohada zamonaviy axborot texnologiyalari va innovatsiyalardan foydalanish."
            ]
        slides_data.append({
            "title": p_title,
            "bullet_points": p_pts,
            "layout": "standard"
        })

    # ================= 3. ASOSIY MAZMUN SLAYDLARI =================
    for idx, s_data in enumerate(slides_data, 1):
        c_slide = prs.slides.add_slide(blank_layout)
        if custom_bg and os.path.exists(custom_bg):
            c_slide.shapes.add_picture(custom_bg, 0, 0, width=Inches(13.333), height=Inches(7.5))
        else:
            bg_c = c_slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
            bg_c.fill.solid()
            bg_c.fill.fore_color.rgb = theme["bg_slide"]
            bg_c.line.fill.background()

        s_title = s_data.get("title", f"Boʻlim {idx}")
        content_slide_num = len(prs.slides)
        sec_lbl = lang_info.get("section_label", "BOʻLIM")
        _add_header(c_slide, s_title, theme, slide_num=content_slide_num, total_slides=total_slides, category=f"{sec_lbl} {idx}")

        img_path = images_map.get(idx) if images_map else None
        bullets = s_data.get("bullet_points", [])
        layout_type = str(s_data.get("layout", "standard")).lower().strip()
        kpi_items = s_data.get("kpi_items", [])
        comparison_data = s_data.get("comparison_data", {})
        steps_data = s_data.get("steps_data", [])

        if layout_type == "kpi" and isinstance(kpi_items, list) and len(kpi_items) >= 2:
            # 3 ta KPI karta
            items = kpi_items[:3]
            card_w = Inches(3.6)
            card_h = Inches(4.9)
            gap = Inches(0.4)
            start_x = Inches(0.9)
            y_pos = Inches(1.8)

            for k_idx, item in enumerate(items):
                x_pos = start_x + k_idx * (card_w + gap)
                k_card = c_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x_pos, y_pos, card_w, card_h)
                k_card.fill.solid()
                k_card.fill.fore_color.rgb = theme["card_bg"]
                k_card.line.color.rgb = theme["accent"] if k_idx == 0 else theme["card_border"]
                k_card.line.width = Pt(2.0 if k_idx == 0 else 1.5)

                # Top color bar
                c_bar = c_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x_pos + Inches(0.3), y_pos + Inches(0.3), card_w - Inches(0.6), Inches(0.08))
                c_bar.fill.solid()
                c_bar.fill.fore_color.rgb = theme["accent"]
                c_bar.line.fill.background()

                # Big Number Textbox
                num_box = c_slide.shapes.add_textbox(x_pos + Inches(0.2), y_pos + Inches(0.55), card_w - Inches(0.4), Inches(1.3))
                ntf = num_box.text_frame
                ntf.word_wrap = True
                np = ntf.paragraphs[0]
                raw_num = str(item.get("number", f"#{k_idx+1}"))
                np.text = remove_emojis(raw_num)
                np.font.size = Pt(38)
                np.font.bold = True
                np.font.color.rgb = theme["accent"]
                np.font.name = "Arial"
                np.alignment = PP_ALIGN.CENTER

                # Label Textbox
                lbl_box = c_slide.shapes.add_textbox(x_pos + Inches(0.2), y_pos + Inches(1.9), card_w - Inches(0.4), Inches(0.7))
                ltf = lbl_box.text_frame
                ltf.word_wrap = True
                lp = ltf.paragraphs[0]
                raw_lbl = str(item.get("label", ""))
                lp.text = remove_emojis(raw_lbl)
                lp.font.size = Pt(18)
                lp.font.bold = True
                lp.font.color.rgb = theme["primary"] if not is_dark else theme["white"]
                lp.font.name = "Arial"
                lp.alignment = PP_ALIGN.CENTER

                # Desc/Bullets in KPI card
                desc_box = c_slide.shapes.add_textbox(x_pos + Inches(0.3), y_pos + Inches(2.7), card_w - Inches(0.6), Inches(1.9))
                dtf = desc_box.text_frame
                dtf.word_wrap = True
                if k_idx < len(bullets):
                    b_txt = re.sub(r"^[\s•\-\*–—\d\.\)]+", "", remove_emojis(str(bullets[k_idx]))).strip()
                    dp = dtf.paragraphs[0]
                    dp.text = b_txt
                    dp.font.size = Pt(13)
                    dp.font.color.rgb = theme["white"] if is_dark else theme["text_muted"]
                    dp.font.name = "Arial"
                    dp.alignment = PP_ALIGN.CENTER

        elif layout_type == "comparison" and isinstance(comparison_data, dict) and comparison_data.get("col1_points") and comparison_data.get("col2_points"):
            col1_title = comparison_data.get("col1_title", "1-yondashuv")
            col1_pts = comparison_data.get("col1_points", [])
            col2_title = comparison_data.get("col2_title", "2-yondashuv")
            col2_pts = comparison_data.get("col2_points", [])

            card_w = Inches(5.3)
            card_h = Inches(5.1)
            y_pos = Inches(1.8)

            # Left Card
            left_card = c_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), y_pos, card_w, card_h)
            left_card.fill.solid()
            left_card.fill.fore_color.rgb = theme["card_bg"]
            left_card.line.color.rgb = theme["card_border"]
            left_card.line.width = Pt(1.5)

            lt_box = c_slide.shapes.add_textbox(Inches(1.15), y_pos + Inches(0.2), card_w - Inches(0.5), Inches(0.7))
            ltf = lt_box.text_frame
            ltf.word_wrap = True
            lp = ltf.paragraphs[0]
            lp.text = remove_emojis(col1_title)
            lp.font.size = Pt(20)
            lp.font.bold = True
            lp.font.color.rgb = theme["primary"] if not is_dark else theme["accent"]
            lp.font.name = "Arial"

            lb_box = c_slide.shapes.add_textbox(Inches(1.15), y_pos + Inches(0.95), card_w - Inches(0.5), card_h - Inches(1.1))
            lbtf = lb_box.text_frame
            lbtf.word_wrap = True
            for p_idx, pt in enumerate(col1_pts[:4]):
                _add_styled_bullet(lbtf, str(pt), theme, font_size=Pt(15), space_after=Pt(10), is_first=(p_idx == 0))

            # Right Card
            right_card = c_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.1), y_pos, card_w, card_h)
            right_card.fill.solid()
            right_card.fill.fore_color.rgb = theme["card_bg"]
            right_card.line.color.rgb = theme["accent"]
            right_card.line.width = Pt(2.0)

            rt_box = c_slide.shapes.add_textbox(Inches(7.35), y_pos + Inches(0.2), card_w - Inches(0.5), Inches(0.7))
            rtf = rt_box.text_frame
            rtf.word_wrap = True
            rp = rtf.paragraphs[0]
            rp.text = remove_emojis(col2_title)
            rp.font.size = Pt(20)
            rp.font.bold = True
            rp.font.color.rgb = theme["accent"]
            rp.font.name = "Arial"

            rb_box = c_slide.shapes.add_textbox(Inches(7.35), y_pos + Inches(0.95), card_w - Inches(0.5), card_h - Inches(1.1))
            rbtf = rb_box.text_frame
            rbtf.word_wrap = True
            for p_idx, pt in enumerate(col2_pts[:4]):
                _add_styled_bullet(rbtf, str(pt), theme, font_size=Pt(15), space_after=Pt(10), is_first=(p_idx == 0))

            # Central VS Badge
            vs_badge = c_slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(6.25), y_pos + Inches(2.1), Inches(0.8), Inches(0.8))
            vs_badge.fill.solid()
            vs_badge.fill.fore_color.rgb = theme["accent"]
            vs_badge.line.fill.background()
            vs_tf = vs_badge.text_frame
            vsp = vs_tf.paragraphs[0]
            vsp.text = "VS"
            vsp.font.size = Pt(14)
            vsp.font.bold = True
            vsp.font.color.rgb = RGBColor(255, 255, 255)
            vsp.alignment = PP_ALIGN.CENTER

        elif layout_type == "steps" and isinstance(steps_data, list) and len(steps_data) >= 2:
            s_items = steps_data[:3]
            card_w = Inches(3.6)
            card_h = Inches(5.0)
            gap = Inches(0.4)
            start_x = Inches(0.9)
            y_pos = Inches(1.8)

            for st_idx, st in enumerate(s_items):
                x_pos = start_x + st_idx * (card_w + gap)
                step_card = c_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x_pos, y_pos, card_w, card_h)
                step_card.fill.solid()
                step_card.fill.fore_color.rgb = theme["card_bg"]
                step_card.line.color.rgb = theme["card_border"]
                step_card.line.width = Pt(1.5)

                # Step Number Pill
                circ = c_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x_pos + Inches(0.3), y_pos + Inches(0.35), Inches(0.9), Inches(0.55))
                circ.fill.solid()
                circ.fill.fore_color.rgb = theme["accent"]
                circ.line.fill.background()
                ctf = circ.text_frame
                cp = ctf.paragraphs[0]
                step_num = str(st.get("step", f"0{st_idx+1}"))
                cp.text = remove_emojis(step_num if len(step_num) >= 2 else f"0{step_num}")
                cp.font.size = Pt(14)
                cp.font.bold = True
                cp.font.color.rgb = RGBColor(255, 255, 255)
                cp.alignment = PP_ALIGN.CENTER

                # Step Title
                st_title_box = c_slide.shapes.add_textbox(x_pos + Inches(0.3), y_pos + Inches(1.1), card_w - Inches(0.6), Inches(0.9))
                st_tf = st_title_box.text_frame
                st_tf.word_wrap = True
                tp = st_tf.paragraphs[0]
                tp.text = remove_emojis(str(st.get("title", "")))
                tp.font.size = Pt(18)
                tp.font.bold = True
                tp.font.color.rgb = theme["primary"] if not is_dark else theme["accent"]
                tp.font.name = "Arial"

                # Step Desc
                desc_box = c_slide.shapes.add_textbox(x_pos + Inches(0.3), y_pos + Inches(2.1), card_w - Inches(0.6), Inches(2.6))
                dtf = desc_box.text_frame
                dtf.word_wrap = True
                dp = dtf.paragraphs[0]
                dp.text = remove_emojis(str(st.get("desc", "")))
                dp.font.size = Pt(14)
                dp.font.color.rgb = theme["text_dark"]
                dp.font.name = "Arial"

        elif img_path and os.path.exists(img_path):
            card = c_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), Inches(1.75), Inches(6.9), Inches(5.25))
            card.fill.solid()
            card.fill.fore_color.rgb = theme["card_bg"]
            card.line.color.rgb = theme["card_border"]
            card.line.width = Pt(1.5)

            content_box = c_slide.shapes.add_textbox(Inches(1.15), Inches(1.95), Inches(6.4), Inches(4.85))
            ctf = content_box.text_frame
            ctf.word_wrap = True

            font_sz = Pt(15 if len(bullets) >= 4 else 17)
            space_aft = Pt(12 if len(bullets) >= 4 else 16)

            for b_idx, bullet in enumerate(bullets):
                _add_styled_bullet(ctf, bullet, theme, font_size=font_sz, space_after=space_aft, is_first=(b_idx == 0))

            try:
                c_slide.shapes.add_picture(img_path, Inches(8.05), Inches(1.75), width=Inches(4.4), height=Inches(5.25))
            except Exception:
                pass
        else:
            card = c_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), Inches(1.75), Inches(11.533), Inches(5.25))
            card.fill.solid()
            card.fill.fore_color.rgb = theme["card_bg"]
            card.line.color.rgb = theme["card_border"]
            card.line.width = Pt(1.5)

            content_box = c_slide.shapes.add_textbox(Inches(1.3), Inches(2.0), Inches(10.7), Inches(4.75))
            ctf = content_box.text_frame
            ctf.word_wrap = True

            font_sz = Pt(17 if len(bullets) >= 5 else 19)
            space_aft = Pt(14 if len(bullets) >= 5 else 18)

            for b_idx, bullet in enumerate(bullets):
                _add_styled_bullet(ctf, bullet, theme, font_size=font_sz, space_after=space_aft, is_first=(b_idx == 0))

        # Speaker notes
        notes = s_data.get("speaker_notes", "")
        if notes:
            notes_slide = c_slide.notes_slide
            text_frame = notes_slide.notes_text_frame
            text_frame.text = f"Ma'ruza nutqi:\n{notes}"

    # References ro'yxatini tozalash va tekshirish
    clean_refs = []
    if isinstance(raw_refs, str):
        clean_refs = [r.strip() for r in raw_refs.split("\n") if r.strip()]
    elif isinstance(raw_refs, list):
        for item in raw_refs:
            if isinstance(item, str) and item.strip():
                clean_refs.append(item.strip())
            elif isinstance(item, dict):
                clean_refs.append(" ".join(str(v) for v in item.values() if v).strip())
    elif isinstance(raw_refs, dict):
        clean_refs = [str(v).strip() for v in raw_refs.values() if str(v).strip()]

    if len(clean_refs) < 3:
        fb_refs = lang_info.get("fallback_refs", [])
        if fb_refs:
            clean_refs = [f"{i+1}. {r}" for i, r in enumerate(fb_refs)]
        else:
            clean_refs = [
                f"1. Oʻzbekiston Respublikasi qonun hujjatlari va davlat taʼlim standartlari toʻplami.",
                f"2. {title_text} yoʻnalishi boʻyicha oliy taʼlim darsliklari va oʻquv qoʻllanmalari toʻplami.",
                f"3. Xalqaro va respublika nufuzli ilmiy jurnallari materiallari (Scopus, Google Scholar, OAK).",
                f"4. Davlat va xalqaro ochiq ilmiy-axborot resurslari hamda elektron kutubxona bazalari."
            ]

    presenter_parts = []
    if has_author:
        done_by_lbl = lang_info.get("done_by", "Taqdimotchi")
        acc_by_lbl = lang_info.get("accepted_by", "Ilmiy rahbar")
        if student_name:
            presenter_parts.append(f"{done_by_lbl}: {student_name}")
        elif author_info:
            first_line = author_info.splitlines()[0].strip()
            presenter_parts.append(f"{done_by_lbl}: {first_line}")
        if teacher_name:
            presenter_parts.append(f"{acc_by_lbl}: {teacher_name}")
        if uni_name:
            presenter_parts.append(uni_name)
    presenter_str = "  |  ".join(presenter_parts)

    # ================= 4. YAKUNIY SLAYDLAR (QAT'IY HISOB-KITOB ASOSIDA) =================
    if closing_count == 1:
        # total_slides <= 5 bo'lganda: Yagona birlashtirilgan Xulosa va Minnatdorchilik slaydi
        end_slide = prs.slides.add_slide(blank_layout)
        if custom_bg and os.path.exists(custom_bg):
            end_slide.shapes.add_picture(custom_bg, 0, 0, width=Inches(13.333), height=Inches(7.5))
        else:
            bg_end = end_slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
            bg_end.fill.solid()
            bg_end.fill.fore_color.rgb = theme["bg_slide"]
            bg_end.line.fill.background()

        concl_hdr = lang_info.get("concl_title", "Xulosa va Yakun")
        _add_header(end_slide, concl_hdr, theme, slide_num=len(prs.slides), total_slides=total_slides, category=concl_hdr.upper())

        # Top Card: Xulosa
        card_t = end_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), Inches(1.6), Inches(11.533), Inches(2.5))
        card_t.fill.solid()
        card_t.fill.fore_color.rgb = theme["card_bg"]
        card_t.line.color.rgb = theme["card_border"]
        card_t.line.width = Pt(1.5)

        t_tf = card_t.text_frame
        t_tf.word_wrap = True
        t_tf.margin_left = Inches(0.4)
        t_tf.margin_top = Inches(0.2)
        t_tf.margin_right = Inches(0.4)
        p_ch = t_tf.paragraphs[0]
        p_ch.text = lang_info.get("main_conclusions", "✦  ASOSIY ILMIY-AMALIY XULOSALAR")
        p_ch.font.size = Pt(14)
        p_ch.font.bold = True
        p_ch.font.color.rgb = theme["accent"]
        p_ch.space_after = Pt(8)

        points = conclusion_points[:2] if conclusion_points else [
            "Mavzu boʻyicha belgilangan barcha vazifalar toʻliq yoritildi va tahlil qilindi.",
            "Olingan natijalar sohaning nazariy va amaliy rivojlanishi uchun muhim ahamiyat kasb etadi."
        ]
        for pt in points:
            _add_styled_bullet(t_tf, pt, theme, font_size=Pt(14), space_after=Pt(6))

        # Bottom Card: E'tiboringiz uchun rahmat
        card_b = end_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), Inches(4.35), Inches(11.533), Inches(2.65))
        card_b.fill.solid()
        card_b.fill.fore_color.rgb = theme["card_bg"]
        card_b.line.color.rgb = theme["accent"]
        card_b.line.width = Pt(2.0)

        b_tf = card_b.text_frame
        b_tf.word_wrap = True
        bp1 = b_tf.paragraphs[0]
        bp1.text = lang_info["thanks"].upper()
        bp1.font.size = Pt(30)
        bp1.font.bold = True
        bp1.font.color.rgb = theme["accent"] if is_dark else theme["primary"]
        bp1.alignment = PP_ALIGN.CENTER
        bp1.space_before = Pt(8)
        bp1.space_after = Pt(6)

        bp2 = b_tf.add_paragraph()
        bp2.text = lang_info.get("questions_welcome", "Savollar, fikr-mulohazalar va muhokama uchun tayyorman")
        bp2.font.size = Pt(15)
        bp2.font.color.rgb = theme["accent"] if is_dark else theme.get("accent_secondary", theme["accent"])
        bp2.alignment = PP_ALIGN.CENTER
        bp2.space_after = Pt(8)

        if presenter_str:
            bp3 = b_tf.add_paragraph()
            bp3.text = presenter_str
            bp3.font.size = Pt(13)
            bp3.font.bold = True
            bp3.font.color.rgb = theme["text_dark"] if not is_dark else theme["white"]
            bp3.alignment = PP_ALIGN.CENTER

    elif closing_count == 2:
        # 6 <= total_slides <= 8: Slide N-1 (Xulosa va Manbalar) + Slide N (Yakuniy Minnatdorchilik)
        concl_slide = prs.slides.add_slide(blank_layout)
        if custom_bg and os.path.exists(custom_bg):
            concl_slide.shapes.add_picture(custom_bg, 0, 0, width=Inches(13.333), height=Inches(7.5))
        else:
            bg_concl = concl_slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
            bg_concl.fill.solid()
            bg_concl.fill.fore_color.rgb = theme["bg_slide"]
            bg_concl.line.fill.background()

        concl_refs_hdr = lang_info.get("concl_and_refs", "Xulosa va Foydalanilgan manbalar")
        _add_header(concl_slide, concl_refs_hdr, theme, slide_num=len(prs.slides), total_slides=total_slides, category=concl_refs_hdr.upper())

        # Left Card: Xulosa
        card_l = concl_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), Inches(1.75), Inches(5.6), Inches(5.25))
        card_l.fill.solid()
        card_l.fill.fore_color.rgb = theme["card_bg"]
        card_l.line.color.rgb = theme["card_border"]
        card_l.line.width = Pt(1.5)

        cl_tf = card_l.text_frame
        cl_tf.word_wrap = True
        cl_tf.margin_left = Inches(0.3)
        cl_tf.margin_top = Inches(0.25)
        cl_tf.margin_right = Inches(0.3)
        p_lh = cl_tf.paragraphs[0]
        p_lh.text = lang_info.get("main_conclusions", "✦  ASOSIY XULOSALAR")
        p_lh.font.size = Pt(16)
        p_lh.font.bold = True
        p_lh.font.color.rgb = theme["accent"]
        p_lh.space_after = Pt(12)

        points = conclusion_points[:4] if conclusion_points else [
            "Mavzu boʻyicha belgilangan barcha vazifalar toʻliq yoritildi va tahlil qilindi.",
            "Olingan natijalar sohaning nazariy va amaliy rivojlanishi uchun muhim ahamiyat kasb etadi.",
            "Tadqiqot natijasida amaliyotga tatbiq qilish mumkin boʻlgan takliflar shakllantirildi."
        ]
        for pt in points:
            _add_styled_bullet(cl_tf, pt, theme, font_size=Pt(14), space_after=Pt(10))

        # Right Card: Adabiyotlar
        card_r = concl_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.75), Inches(5.6), Inches(5.25))
        card_r.fill.solid()
        card_r.fill.fore_color.rgb = theme["card_bg"]
        card_r.line.color.rgb = theme["card_border"]
        card_r.line.width = Pt(1.5)

        cr_tf = card_r.text_frame
        cr_tf.word_wrap = True
        cr_tf.margin_left = Inches(0.3)
        cr_tf.margin_top = Inches(0.25)
        cr_tf.margin_right = Inches(0.3)
        p_rh = cr_tf.paragraphs[0]
        p_rh.text = f"✦  {lang_info.get('references', 'FOYDALANILGAN MANBALAR').upper()}"
        p_rh.font.size = Pt(16)
        p_rh.font.bold = True
        p_rh.font.color.rgb = theme["accent"]
        p_rh.space_after = Pt(12)
        p_rh.font.size = Pt(16)
        p_rh.font.bold = True
        p_rh.font.color.rgb = theme["accent"]
        p_rh.space_after = Pt(12)

        for r_idx, ref_text in enumerate(clean_refs[:4], 1):
            p = cr_tf.add_paragraph()
            t_cleaned = re.sub(r"^[\d\.\)\-\s•]+", "", remove_emojis(str(ref_text))).strip()
            p.text = f"{r_idx}.  {t_cleaned}"
            p.font.size = Pt(13)
            p.font.color.rgb = theme["text_dark"]
            p.font.name = "Arial"
            p.space_after = Pt(10)

        # Slide N: Yakuniy Minnatdorchilik
        _create_thanks_slide(prs, blank_layout, theme, custom_bg, is_white, is_dark, lang_info, presenter_str)

    else:
        # total_slides >= 9: Slide N-2 (Xulosa) + Slide N-1 (Adabiyotlar) + Slide N (Yakuniy Minnatdorchilik)
        concl_slide = prs.slides.add_slide(blank_layout)
        if custom_bg and os.path.exists(custom_bg):
            concl_slide.shapes.add_picture(custom_bg, 0, 0, width=Inches(13.333), height=Inches(7.5))
        else:
            bg_concl = concl_slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
            bg_concl.fill.solid()
            bg_concl.fill.fore_color.rgb = theme["bg_slide"]
            bg_concl.line.fill.background()

        _add_header(concl_slide, lang_info["conclusion"], theme, slide_num=len(prs.slides), total_slides=total_slides, category=lang_info["conclusion"].upper())

        concl_card = concl_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), Inches(1.75), Inches(11.533), Inches(5.25))
        concl_card.fill.solid()
        concl_card.fill.fore_color.rgb = theme["card_bg"]
        concl_card.line.color.rgb = theme["card_border"]
        concl_card.line.width = Pt(1.5)

        concl_box = concl_slide.shapes.add_textbox(Inches(1.3), Inches(2.1), Inches(10.7), Inches(4.6))
        concl_tf = concl_box.text_frame
        concl_tf.word_wrap = True

        if conclusion_points:
            for c_idx, point in enumerate(conclusion_points):
                _add_styled_bullet(concl_tf, point, theme, font_size=Pt(18), space_after=Pt(16), is_first=(c_idx == 0))
        else:
            p = concl_tf.paragraphs[0]
            p.text = "Taqdimot mavzusi to'liq yoritildi va asosiy masalalar muhokama qilindi."
            p.font.size = Pt(22)
            p.font.color.rgb = theme["text_dark"]

        # Slide N-1: Foydalanilgan adabiyotlar
        ref_slide = prs.slides.add_slide(blank_layout)
        if custom_bg and os.path.exists(custom_bg):
            ref_slide.shapes.add_picture(custom_bg, 0, 0, width=Inches(13.333), height=Inches(7.5))
        else:
            bg_ref = ref_slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
            bg_ref.fill.solid()
            bg_ref.fill.fore_color.rgb = theme["bg_slide"]
            bg_ref.line.fill.background()

        _add_header(ref_slide, lang_info["references"], theme, slide_num=len(prs.slides), total_slides=total_slides, category=lang_info["references"].upper())

        ref_card = ref_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), Inches(1.75), Inches(11.533), Inches(5.25))
        ref_card.fill.solid()
        ref_card.fill.fore_color.rgb = theme["card_bg"]
        ref_card.line.color.rgb = theme["card_border"]
        ref_card.line.width = Pt(1.5)

        ref_box = ref_slide.shapes.add_textbox(Inches(1.3), Inches(2.0), Inches(10.7), Inches(4.7))
        ref_tf = ref_box.text_frame
        ref_tf.word_wrap = True

        font_sz = Pt(15 if len(clean_refs) > 4 else 17)
        spacing = Pt(10 if len(clean_refs) > 4 else 14)

        for r_idx, ref_text in enumerate(clean_refs):
            p = ref_tf.paragraphs[0] if r_idx == 0 else ref_tf.add_paragraph()
            t_cleaned = re.sub(r"^[\d\.\)\-\s•]+", "", remove_emojis(str(ref_text))).strip()
            p.text = f"{r_idx + 1}.  {t_cleaned}"
            p.font.size = font_sz
            p.font.bold = False
            p.font.color.rgb = theme["text_dark"]
            p.font.name = "Arial"
            p.space_after = spacing

        # Slide N: Yakuniy Minnatdorchilik
        _create_thanks_slide(prs, blank_layout, theme, custom_bg, is_white, is_dark, lang_info, presenter_str)

    # Belgilangandan 1 list ham oshmasin: ortiqcha slaydlar bo'lsa oxiridan tozalaymiz
    while len(prs.slides) > total_slides:
        rId = prs.slides._sldIdLst[-1].rId
        prs.part.drop_rel(rId)
        del prs.slides._sldIdLst[-1]

    # Save to disk
    if os.path.dirname(output_path):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
    prs.save(output_path)
    return output_path

def generate_speech_script(content: dict, author_info: str = "", default_student_name: str = "", target_slide_count: int = 0) -> str:
    """Talabalar uchun taqdimotni doskada himoya qilish bo'yicha to'liq nutq matnini tayyorlaydi."""
    content = clean_data_structure(content)
    title = content.get("title", "Taqdimot")
    subtitle = content.get("subtitle", "")
    slides = content.get("slides", [])
    conclusion = content.get("conclusion", [])
    has_author = bool(author_info and author_info.strip())

    if not target_slide_count or target_slide_count < 3:
        target_slide_count = content.get("target_slide_count") or 8
    total_slides = target_slide_count

    has_agenda_slide, intro_count, closing_count, target_content_count = calculate_slide_distribution(total_slides)
    slides = slides[:target_content_count]

    student_details = content.get("student_details") or (smart_parse_student_details(author_info) if has_author else {})
    uni = (student_details.get("university") or "").strip() if has_author else ""
    fac = (student_details.get("faculty") or "").strip() if has_author else ""
    stud = (student_details.get("student") or "").strip() if has_author else ""
    if has_author and not stud and default_student_name:
        stud = default_student_name
    teach = (student_details.get("teacher") or "").strip() if has_author else ""
    direction_val = (student_details.get("direction") or "").strip() if has_author else ""
    group_val = (student_details.get("group") or "").strip() if has_author else ""

    dir_grp = direction_val
    if group_val:
        dir_grp = f"{dir_grp} ({group_val})" if dir_grp else group_val

    lines = []
    lines.append("TAQDIMOT HIMOYASI UCHUN NUTQ MATNI (DOKLAD)")
    lines.append(f"Mavzu: {title}")
    if subtitle:
        lines.append(f"Yoʻnalish: {subtitle}")
    if has_author:
        if uni:
            lines.append(f"OTM: {uni}")
        if fac:
            lines.append(f"Fakultet: {fac}")
        if dir_grp:
            lines.append(f"Yoʻnalish va guruh: {dir_grp}")
        if stud:
            lines.append(f"Talaba (bajardi): {stud}")
        if teach:
            lines.append(f"Oʻqituvchi (qabul qildi): {teach}")

    lines.append("=" * 45)
    lines.append("")

    # 1-Slayd: Titul yoki Mavzu
    if has_author:
        lines.append("1-SLAYD: RASMIY TITUL VARAQASI VA TAQDIMOT MAVZUSI")
        intro_parts = []
        if uni:
            intro_parts.append(uni)
        if fac:
            intro_parts.append(fac)
        if dir_grp:
            intro_parts.append(f"{dir_grp} talabasi")
        if stud:
            intro_parts.append(stud)

        intro_who = " ".join(intro_parts)
        who_clause = f"Men {intro_who}. " if intro_who else ""
        teach_clause = f"oʻqituvchim (ilmiy rahbarim) {teach} rahbarligida tayyorlangan " if teach else ""

        lines.append("«Assalomu alaykum, hurmatli ustozlar va qadrli talabalar!")
        lines.append(f"{who_clause}Sizlarning eʼtiboringizga {teach_clause}'{title}' mavzusidagi ilmiy taqdimotimni himoya qilish uchun havola etmoqdaman.")
        lines.append("Ushbu mavzuning dolzarbligi shundaki, zamonaviy davrda bu masalani chuqur oʻrganish, mavjud muammolarni tahlil qilish va istiqbolli yechimlarni topish muhim amaliy ahamiyatga egadir.»\n")
    else:
        lines.append("1-SLAYD: TAQDIMOT MAVZUSI VA MAQSADI")
        lines.append("«Assalomu alaykum, hurmatli tinglovchilar!")
        lines.append(f"Bugungi taqdimotimiz mavzusi: '{title}'.")
        if subtitle:
            lines.append(f"Yoʻnalish va soha: {subtitle}.")
        lines.append("Ushbu mavzuning dolzarbligi shundaki, zamonaviy davrda bu masalani chuqur oʻrganish, mavjud muammolarni tahlil qilish va istiqbolli yechimlarni topish muhim amaliy ahamiyatga egadir.»\n")

    # 2-Slayd: Reja (agar total_slides >= 5 bo'lsa)
    current_slide_num = 1
    if has_agenda_slide:
        current_slide_num = 2
        lines.append("2-SLAYD: TAQDIMOT REJASI (MUNDARIJA)")
        lines.append("«Taqdimotimiz reja asosida tizimli ravishda quyidagi asosiy yoʻnalishlar boʻyicha koʻrib chiqiladi:")
        speech_agenda = content.get("agenda")
        if not speech_agenda:
            speech_agenda = [re.sub(r"^\d+[\.\)\-\s]+", "", s.get("title", f"Boʻlim {i}")) for i, s in enumerate(slides[:3], 1)]
            speech_agenda.append("Xulosa va Asosiy Natijalar")
            speech_agenda.append("Foydalanilgan Adabiyotlar")
        for i, plan_item in enumerate(speech_agenda[:5], 1):
            lines.append(f"   {i}. {plan_item}")
        lines.append("Endi esa bevosita rejamizdagi asosiy mazmuniy slaydlarga oʻtsak.»\n")

    # Mazmun slaydlari
    for i, s in enumerate(slides, 1):
        current_slide_num += 1
        s_title = s.get("title", f"Boʻlim {i}")
        notes = s.get("speaker_notes", "")
        bullets = s.get("bullet_points", [])
        lines.append(f"{current_slide_num}-SLAYD: {s_title.upper()}")
        if notes:
            lines.append(f"«{notes}»")
        else:
            bullets_text = "; ".join(bullets[:3])
            lines.append(f"«Ushbu slaydda {s_title} masalasiga toʻxtalib oʻtamiz. Xususan: {bullets_text} kabi muhim omillar taʼkidlab oʻtildi.»")
        lines.append("")

    # Yakuniy slaydlar
    if closing_count == 1:
        current_slide_num += 1
        lines.append(f"{current_slide_num}-SLAYD: XULOSA VA YAKUNIY SOʻZ")
        lines.append("«Oʻtkazilgan tahlillar va oʻrganishlar asosida quyidagi xulosalarga keldik:")
        if conclusion:
            for c in conclusion[:3]:
                lines.append(f" • {c}")
        else:
            lines.append(" • Mavzu doirasida barcha qoʻyilgan vazifalar toʻliq yoritib berildi.")
        lines.append("Eʼtiboringiz uchun katta rahmat! Mavzu yuzasidan barcha savollaringiz va fikrlaringizga mamnuniyat bilan javob berishga tayyorman.»")

    elif closing_count == 2:
        current_slide_num += 1
        lines.append(f"{current_slide_num}-SLAYD: XULOSA VA ILMIY MANBALAR")
        lines.append("«Oʻtkazilgan tahlillar va oʻrganishlar asosida quyidagi xulosalarga keldik:")
        if conclusion:
            for c in conclusion[:3]:
                lines.append(f" • {c}")
        else:
            lines.append(" • Mavzu doirasida barcha qoʻyilgan vazifalar toʻliq yoritib berildi.")
        lines.append("Ushbu tadqiqotda asosiy ilmiy adabiyotlar va davlat meʼyoriy manbalaridan foydalanildi.»\n")

        current_slide_num += 1
        lines.append(f"{current_slide_num}-SLAYD: YAKUNIY MINNATDORCHILIK")
        lines.append("«Eʼtiboringiz uchun katta rahmat! Mavzu yuzasidan barcha savollaringiz va fikrlaringizga mamnuniyat bilan javob berishga tayyorman.»")

    else:
        current_slide_num += 1
        lines.append(f"{current_slide_num}-SLAYD: XULOSA")
        lines.append("«Oʻtkazilgan tahlillar va oʻrganishlar asosida quyidagi xulosalarga keldik:")
        if conclusion:
            for c in conclusion:
                lines.append(f" • {c}")
        else:
            lines.append(" • Mavzu doirasida barcha qoʻyilgan vazifalar toʻliq yoritib berildi.")
        lines.append("Ushbu natijalar mavzuning nazariy va amaliy jihatdan dolzarbligini tasdiqlaydi.»\n")

        current_slide_num += 1
        lines.append(f"{current_slide_num}-SLAYD: FOYDALANILGAN ADABIYOTLAR")
        lines.append("«Taqdimotni tayyorlashda quyidagi asosiy ilmiy darsliklar va rasmiy manbalardan foydalanildi:")
        raw_refs = content.get("references", [])
        if isinstance(raw_refs, str):
            raw_refs = [r.strip() for r in raw_refs.split("\n") if r.strip()]
        for r_idx, ref_text in enumerate(raw_refs[:5], 1):
            t_cleaned = re.sub(r"^[\d\.\)\-\s•]+", "", str(ref_text)).strip()
            lines.append(f"   {r_idx}. {t_cleaned}")
        lines.append("Ushbu manbalar mavzuning ilmiy asoslanganligini taʼminlaydi.»\n")

        current_slide_num += 1
        lines.append(f"{current_slide_num}-SLAYD: YAKUNIY MINNATDORCHILIK")
        lines.append("«Eʼtiboringiz uchun katta rahmat! Mavzu yuzasidan barcha savollaringiz va fikrlaringizga mamnuniyat bilan javob berishga tayyorman.»")

    return "\n".join(lines)


async def parse_voice_to_presentation_details(audio_path: str) -> dict:
    """Ovozli xabar faylini eshitib, undan taqdimot mavzusi, slaydlar soni va muallifni aniqlaydi."""
    client = genai.Client(api_key=config.GEMINI_API_KEY)
    
    mp3_path = audio_path
    cleanup_mp3 = False
    if not audio_path.lower().endswith(".mp3"):
        mp3_fd, mp3_tmp = tempfile.mkstemp(prefix="voice_conv_", suffix=".mp3")
        os.close(mp3_fd)
        try:
            cmd = ["ffmpeg", "-y", "-i", audio_path, "-ac", "1", "-ar", "16000", mp3_tmp]
            proc = await asyncio.create_subprocess_exec(*cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            await proc.communicate()
            if os.path.exists(mp3_tmp) and os.path.getsize(mp3_tmp) > 0:
                mp3_path = mp3_tmp
                cleanup_mp3 = True
        except Exception as e:
            logger.warning(f"ffmpeg conversion error: {e}")

    try:
        with open(mp3_path, "rb") as f:
            audio_bytes = f.read()

        audio_part = types.Part.from_bytes(data=audio_bytes, mime_type="audio/mp3")
        prompt = """
Ushbu audio xabarda foydalanuvchi taqdimot (slayd) tayyorlash haqida gapirmoqda.
Audio xabarni diqqat bilan eshiting va undan quyidagi ma'lumotlarni aniq ajratib oling:
1. topic: Taqdimot mavzusi (toza, aniq akademik mavzu sarlavhasi).
2. slide_count: Slaydlar soni (agar audioda aniq aytilgan bo'lsa butun son, aytilmagan bo'lsa 8).
3. author_info: Taqdimot muallifi, OTM, fakultet, guruh yoki talaba ismi (agar aytilgan bo'lsa, aks holda bo'sh satr "").
4. language: Qaysi tilda ekanligi ("uzbek", "russian", "english").

Qat'iy quyidagi JSON formatida javob bering:
{
  "topic": "Aniqlangan mavzu",
  "slide_count": 8,
  "author_info": "",
  "language": "uzbek"
}
"""
        models_to_try = ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-flash-lite-latest"]
        for m in models_to_try:
            try:
                res = await client.aio.models.generate_content(
                    model=m,
                    contents=[audio_part, prompt],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.3,
                        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
                    )
                )
                text = res.text.strip()
                data = safe_json_loads(text)
                return {
                    "topic": str(data.get("topic", "")).strip(),
                    "slide_count": int(data.get("slide_count", 8) or 8),
                    "author_info": str(data.get("author_info", "")).strip(),
                    "language": str(data.get("language", "uzbek")).strip()
                }
            except Exception as e:
                logger.warning(f"Voice parse model {m} failed: {e}")
                continue
    finally:
        if cleanup_mp3 and os.path.exists(mp3_path):
            try:
                os.remove(mp3_path)
            except Exception:
                pass

    return {"topic": "", "slide_count": 8, "author_info": "", "language": "uzbek"}


async def extract_topic_and_context_from_document_or_image(file_path: str, mime_type: str = "") -> dict:
    """Rasm (kitob/konspekt) yoki fayl (PDF, Word, TXT) ichidagi matnni tahlil qilib, mavzu va asosiy kontekstni ajratadi."""
    client = genai.Client(api_key=config.GEMINI_API_KEY)
    ext = os.path.splitext(file_path)[1].lower()
    
    extracted_text = ""
    image_part = None

    if ext in [".jpg", ".jpeg", ".png", ".webp"]:
        with open(file_path, "rb") as f:
            img_data = f.read()
        m_type = "image/jpeg" if ext in [".jpg", ".jpeg"] else "image/png"
        image_part = types.Part.from_bytes(data=img_data, mime_type=m_type)

    elif ext == ".pdf":
        try:
            reader = pypdf.PdfReader(file_path)
            pages_text = []
            for i, page in enumerate(reader.pages[:15]):
                t = page.extract_text() or ""
                if t.strip():
                    pages_text.append(t.strip())
            extracted_text = "\n\n".join(pages_text)
        except Exception as e:
            logger.warning(f"pypdf extraction error: {e}")

    elif ext in [".docx", ".doc"]:
        try:
            doc = docx.Document(file_path)
            extracted_text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        except Exception as e:
            logger.warning(f"docx extraction error: {e}")

    elif ext in [".txt", ".md"]:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                extracted_text = f.read()
        except Exception as e:
            logger.warning(f"txt read error: {e}")

    prompt = """
Ushbu taqdim etilgan manba (kitob beti, konspekt yoki hujjat) asosida taqdimot tayyorlashimiz kerak.
Ushbu materialni tahlil qiling va quyidagilarni aniqlab, JSON formatida qaytaring:
1. topic: Eng mos keladigan aniq akademik taqdimot mavzusi (sarlavhasi).
2. summary: Hujjatdagi eng muhim asosiy g'oyalar, faktlar, nazariyalar va xulosalar (taqdimot slaydlari uchun kerak bo'ladigan siqilgan konspekt matni).
3. suggested_slides: Ushbu hajmga mos keladigan tavsiya etilgan slaydlar soni (kamida 5, ko'pi bilan 15).

Qat'iy JSON formatida javob bering:
{
  "topic": "...",
  "summary": "...",
  "suggested_slides": 8
}
"""
    contents = [prompt]
    if image_part:
        contents.insert(0, image_part)
    elif extracted_text:
        contents.append(f"\nHujjat matni:\n```\n{extracted_text[:12000]}\n```")
    else:
        return {"topic": "", "summary": "", "suggested_slides": 8}

    models_to_try = ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-flash-lite-latest"]
    for m in models_to_try:
        try:
            res = await client.aio.models.generate_content(
                model=m,
                contents=contents,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.3,
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
                )
            )
            data = safe_json_loads(res.text.strip())
            return {
                "topic": str(data.get("topic", "")).strip(),
                "summary": str(data.get("summary", "")).strip(),
                "suggested_slides": int(data.get("suggested_slides", 8) or 8)
            }
        except Exception as e:
            logger.warning(f"Doc extract model {m} failed: {e}")
            continue

    return {"topic": "", "summary": extracted_text[:2000], "suggested_slides": 8}



