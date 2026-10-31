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

# Slayd orqa foni va dizayn mavzulari (Zamonaviy Dark Glass uslubida, oq matnlar bilan)
THEMES = {
    "white": {
        "name": "⚪️ Minimalist Dark Slate",
        "primary": RGBColor(15, 23, 42),          # Deep Navy/Slate banner
        "accent": RGBColor(56, 189, 248),         # Sky Cyan
        "accent_secondary": RGBColor(129, 140, 248),
        "bg_slide": RGBColor(15, 23, 42),         # Deep Canvas (Hech qachon daftar varog'i emas)
        "card_bg": RGBColor(24, 34, 56),          # Dark Glass Card
        "card_border": RGBColor(56, 189, 248),    # Luminous Border
        "text_dark": RGBColor(255, 255, 255),     # 100% Oq rang
        "text_muted": RGBColor(226, 232, 240),    # Bright Silver-White
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "MINIMALIST SLATE"
    },
    "dark": {
        "name": "🖤 Qora fon (Premium Dark)",
        "primary": RGBColor(18, 18, 18),          # OLED Black
        "accent": RGBColor(245, 158, 11),         # Luxury Gold / Amber
        "accent_secondary": RGBColor(234, 179, 8),
        "bg_slide": RGBColor(20, 20, 24),         # Dark Zinc
        "card_bg": RGBColor(34, 34, 40),          # Zinc Card
        "card_border": RGBColor(245, 158, 11),
        "text_dark": RGBColor(255, 255, 255),     # 100% Crisp White
        "text_muted": RGBColor(226, 232, 240),    # Bright Silver-White
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "PREMIUM DARK"
    },
    "navy": {
        "name": "🔵 Toʻq koʻk fon (Royal Navy)",
        "primary": RGBColor(10, 25, 47),          # Royal Navy
        "accent": RGBColor(245, 158, 11),         # Luxury Gold
        "accent_secondary": RGBColor(56, 189, 248),
        "bg_slide": RGBColor(10, 25, 47),         # Deep Navy Canvas
        "card_bg": RGBColor(17, 38, 70),          # Navy Glass Card
        "card_border": RGBColor(245, 158, 11),
        "text_dark": RGBColor(255, 255, 255),     # 100% Oq rang
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "ROYAL NAVY"
    },
    "blue": {
        "name": "🔷 Moviy fon (Havorang)",
        "primary": RGBColor(12, 36, 68),          # Deep Navy
        "accent": RGBColor(14, 165, 233),         # Sky Blue
        "accent_secondary": RGBColor(56, 189, 248),
        "bg_slide": RGBColor(12, 36, 68),         # Deep Ocean
        "card_bg": RGBColor(18, 50, 94),          # Deep Blue Card
        "card_border": RGBColor(14, 165, 233),
        "text_dark": RGBColor(255, 255, 255),     # 100% Oq rang
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "MOVIY KLASSIK"
    },
    "green": {
        "name": "🟢 Zumrad yashil fon",
        "primary": RGBColor(6, 44, 34),           # Forest Emerald
        "accent": RGBColor(16, 185, 129),         # Fresh Mint
        "accent_secondary": RGBColor(45, 212, 191),# Teal
        "bg_slide": RGBColor(6, 44, 34),          # Deep Emerald
        "card_bg": RGBColor(10, 64, 50),          # Emerald Card
        "card_border": RGBColor(16, 185, 129),
        "text_dark": RGBColor(255, 255, 255),     # 100% Oq rang
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "ZUMRAD YASHIL"
    },
    "purple": {
        "name": "🟣 Binafsha fon (Kosmik)",
        "primary": RGBColor(30, 16, 56),          # Deep Violet
        "accent": RGBColor(168, 85, 247),         # Neon Purple
        "accent_secondary": RGBColor(216, 70, 239),
        "bg_slide": RGBColor(30, 16, 56),         # Deep Violet Space
        "card_bg": RGBColor(46, 24, 84),          # Cosmic Card
        "card_border": RGBColor(168, 85, 247),
        "text_dark": RGBColor(255, 255, 255),     # 100% Oq rang
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "KOSMIK BINAFSHA"
    },
    "canva_pastel": {
        "name": "🌸 Canva Pastel fon (Nafis)",
        "primary": RGBColor(46, 18, 42),          # Deep Twilight Plum
        "accent": RGBColor(244, 114, 182),        # Rose Pink
        "accent_secondary": RGBColor(251, 146, 60),
        "bg_slide": RGBColor(46, 18, 42),         # Deep Twilight Plum
        "card_bg": RGBColor(68, 28, 62),          # Velvet Plum Card
        "card_border": RGBColor(244, 114, 182),
        "text_dark": RGBColor(255, 255, 255),     # 100% Oq rang
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "CANVA PASTEL"
    },
    "vintage": {
        "name": "📜 Klassik pergament fon",
        "primary": RGBColor(44, 28, 18),          # Deep Antique Espresso
        "accent": RGBColor(217, 169, 90),         # Antique Gold
        "accent_secondary": RGBColor(234, 179, 8),# Warm Amber
        "bg_slide": RGBColor(44, 28, 18),         # Deep Bronze
        "card_bg": RGBColor(64, 40, 26),          # Antique Card
        "card_border": RGBColor(217, 169, 90),
        "text_dark": RGBColor(255, 255, 255),     # 100% Oq rang
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "KLASSIK RETRO"
    },
    # ================= POWERPOINT 2016 RASMIY SHABLONLARI =================
    "facet": {
        "name": "🟢 Facet 2016 (Geometrik Zumrad)",
        "primary": RGBColor(8, 42, 34),           # Deep Forest Pine
        "accent": RGBColor(16, 185, 129),         # Bright Emerald / Mint
        "accent_secondary": RGBColor(45, 212, 191),# Teal
        "bg_slide": RGBColor(8, 42, 34),          # Deep Facet Pine
        "card_bg": RGBColor(12, 60, 48),          # Facet Card
        "card_border": RGBColor(45, 212, 191),
        "text_dark": RGBColor(255, 255, 255),     # 100% Oq rang
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "PPT 2016 FACET"
    },
    "ion": {
        "name": "🔴 Ion 2016 (Bordo & To'q qizil)",
        "primary": RGBColor(52, 14, 26),          # Deep Burgundy Wine
        "accent": RGBColor(249, 115, 22),         # Radiant Orange / Amber
        "accent_secondary": RGBColor(244, 63, 94),# Crimson
        "bg_slide": RGBColor(52, 14, 26),         # Deep Wine Canvas
        "card_bg": RGBColor(74, 20, 36),          # Wine Card
        "card_border": RGBColor(249, 115, 22),
        "text_dark": RGBColor(255, 255, 255),     # 100% Oq rang
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "PPT 2016 ION"
    },
    "slice": {
        "name": "🔷 Slice 2016 (Kesimli Neo Havorang)",
        "primary": RGBColor(15, 23, 42),          # Deep Slate
        "accent": RGBColor(6, 182, 212),          # Electric Cyan
        "accent_secondary": RGBColor(56, 189, 248),# Sky
        "bg_slide": RGBColor(15, 23, 42),         # Modern Deep Slate
        "card_bg": RGBColor(24, 34, 58),          # Slate Card
        "card_border": RGBColor(6, 182, 212),
        "text_dark": RGBColor(255, 255, 255),     # 100% Oq rang
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "PPT 2016 SLICE"
    },
    "celestial": {
        "name": "🌌 Celestial 2016 (Koinot Tungi Moviy)",
        "primary": RGBColor(10, 20, 50),          # Midnight Space Blue
        "accent": RGBColor(234, 179, 8),          # Starlight Gold
        "accent_secondary": RGBColor(56, 189, 248),# Celestial Blue
        "bg_slide": RGBColor(10, 20, 50),         # Deep Celestial Blue
        "card_bg": RGBColor(16, 32, 76),          # Deep Sky Card
        "card_border": RGBColor(234, 179, 8),
        "text_dark": RGBColor(255, 255, 255),     # 100% Oq rang
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "PPT 2016 CELESTIAL"
    },
    "integral": {
        "name": "📐 Integral 2016 (Muhandislik & Terrakota)",
        "primary": RGBColor(22, 38, 58),          # Steel Navy
        "accent": RGBColor(235, 94, 60),          # Terracotta Coral
        "accent_secondary": RGBColor(245, 158, 11),# Warm Amber
        "bg_slide": RGBColor(22, 38, 58),         # Deep Steel Mist
        "card_bg": RGBColor(32, 54, 82),          # Steel Card
        "card_border": RGBColor(235, 94, 60),
        "text_dark": RGBColor(255, 255, 255),     # 100% Oq rang
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "PPT 2016 INTEGRAL"
    },
    "retrospect": {
        "name": "🏺 Retrospect 2016 (Retro Oltin Qum)",
        "primary": RGBColor(48, 26, 14),          # Mahogany Earth
        "accent": RGBColor(217, 119, 6),          # Rich Amber Gold
        "accent_secondary": RGBColor(234, 179, 8), # Warm Copper
        "bg_slide": RGBColor(48, 26, 14),         # Deep Warm Earth
        "card_bg": RGBColor(68, 38, 20),          # Earth Card
        "card_border": RGBColor(217, 119, 6),
        "text_dark": RGBColor(255, 255, 255),     # 100% Oq rang
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "PPT 2016 RETROSPECT"
    },
    "droplet": {
        "name": "💧 Droplet 2016 (Yumshoq Tomchi Akva)",
        "primary": RGBColor(10, 46, 52),          # Deep Ocean Teal
        "accent": RGBColor(20, 184, 166),         # Aquamarine
        "accent_secondary": RGBColor(56, 189, 248),# Soft Sky
        "bg_slide": RGBColor(10, 46, 52),         # Deep Aqua
        "card_bg": RGBColor(16, 68, 76),          # Aqua Card
        "card_border": RGBColor(20, 184, 166),
        "text_dark": RGBColor(255, 255, 255),     # 100% Oq rang
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "PPT 2016 DROPLET"
    },
    "savon": {
        "name": "📜 Savon 2016 (Aristokrat Shampan)",
        "primary": RGBColor(36, 32, 30),          # Muted Deep Bronze
        "accent": RGBColor(217, 119, 6),          # Champagne Gold
        "accent_secondary": RGBColor(245, 158, 11),
        "bg_slide": RGBColor(36, 32, 30),         # Deep Linen Charcoal
        "card_bg": RGBColor(52, 46, 44),          # Bronze Card
        "card_border": RGBColor(217, 119, 6),
        "text_dark": RGBColor(255, 255, 255),     # 100% Oq rang
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "PPT 2016 SAVON"
    },
    "circuit": {
        "name": "⚡️ Circuit 2016 (Kiber Texno Dark)",
        "primary": RGBColor(15, 23, 42),          # Cyber Black
        "accent": RGBColor(6, 182, 212),          # Neon Cyan
        "accent_secondary": RGBColor(139, 92, 246),# Neon Violet
        "bg_slide": RGBColor(15, 23, 42),         # Dark Circuit Canvas
        "card_bg": RGBColor(24, 34, 58),          # Dark Card
        "card_border": RGBColor(6, 182, 212),
        "text_dark": RGBColor(255, 255, 255),     # 100% Oq rang
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "PPT 2016 CIRCUIT"
    },
    "office": {
        "name": "🏢 Office 2016 (Klassik Moviy)",
        "primary": RGBColor(15, 28, 52),          # Official Office Blue
        "accent": RGBColor(56, 189, 248),         # Steel Vivid Blue
        "accent_secondary": RGBColor(245, 158, 11),# Warm Accent
        "bg_slide": RGBColor(15, 28, 52),         # Deep Executive Slate
        "card_bg": RGBColor(22, 42, 78),          # Executive Card
        "card_border": RGBColor(56, 189, 248),
        "text_dark": RGBColor(255, 255, 255),     # 100% Oq rang
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "PPT 2016 OFFICE"
    },
    "mix": {
        "name": "🔀 PPT 2016 Dinamik Mix",
        "primary": RGBColor(15, 23, 42),
        "accent": RGBColor(234, 179, 8),
        "accent_secondary": RGBColor(56, 189, 248),
        "bg_slide": RGBColor(15, 23, 42),
        "card_bg": RGBColor(24, 34, 58),
        "card_border": RGBColor(234, 179, 8),
        "text_dark": RGBColor(255, 255, 255),     # 100% Oq rang
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "PPT 2016 MIX"
    },
    # ================= 1. IT, DASTURLASH & KIBERXAVFSIZLIK =================
    "cyber": {
        "name": "⚡️ Kiberxavfsizlik & Neon Cyan",
        "primary": RGBColor(3, 7, 18),
        "accent": RGBColor(6, 182, 212),
        "accent_secondary": RGBColor(59, 130, 246),
        "bg_slide": RGBColor(3, 7, 18),
        "card_bg": RGBColor(15, 23, 42),
        "card_border": RGBColor(6, 182, 212),
        "text_dark": RGBColor(255, 255, 255),
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "CYBER SECURITY"
    },
    "ai_violet": {
        "name": "🤖 Sun'iy Intellekt & Neyron Binafsha",
        "primary": RGBColor(24, 12, 44),
        "accent": RGBColor(168, 85, 247),
        "accent_secondary": RGBColor(217, 70, 239),
        "bg_slide": RGBColor(24, 12, 44),
        "card_bg": RGBColor(38, 18, 68),
        "card_border": RGBColor(168, 85, 247),
        "text_dark": RGBColor(255, 255, 255),
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "AI & NEURAL"
    },
    "tech_matrix": {
        "name": "💻 Dasturlash & Terminal Green",
        "primary": RGBColor(2, 20, 13),
        "accent": RGBColor(16, 185, 129),
        "accent_secondary": RGBColor(52, 211, 153),
        "bg_slide": RGBColor(2, 20, 13),
        "card_bg": RGBColor(6, 36, 24),
        "card_border": RGBColor(16, 185, 129),
        "text_dark": RGBColor(255, 255, 255),
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "DEVELOPER CODE"
    },
    "tech_cloud": {
        "name": "☁️ Bulutli Texnologiya & Azure Blue",
        "primary": RGBColor(10, 28, 56),
        "accent": RGBColor(56, 189, 248),
        "accent_secondary": RGBColor(96, 165, 250),
        "bg_slide": RGBColor(10, 28, 56),
        "card_bg": RGBColor(18, 44, 82),
        "card_border": RGBColor(56, 189, 248),
        "text_dark": RGBColor(255, 255, 255),
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "CLOUD & BIG DATA"
    },
    "tech_mobile": {
        "name": "📱 Mobil Ilovalar & Flutter Coral",
        "primary": RGBColor(26, 18, 38),
        "accent": RGBColor(251, 113, 133),
        "accent_secondary": RGBColor(129, 140, 248),
        "bg_slide": RGBColor(26, 18, 38),
        "card_bg": RGBColor(40, 26, 58),
        "card_border": RGBColor(251, 113, 133),
        "text_dark": RGBColor(255, 255, 255),
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "MOBILE & UI"
    },
    # ================= 2. TIBBIYOT & SALOMATLIK =================
    "med_clinic": {
        "name": "🩺 Shifoxona & Klinik Teal",
        "primary": RGBColor(6, 44, 38),
        "accent": RGBColor(20, 184, 166),
        "accent_secondary": RGBColor(45, 212, 191),
        "bg_slide": RGBColor(6, 44, 38),
        "card_bg": RGBColor(10, 64, 56),
        "card_border": RGBColor(20, 184, 166),
        "text_dark": RGBColor(255, 255, 255),
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "CLINICAL MEDICINE"
    },
    "med_pharma": {
        "name": "💊 Farmatsevtika & Bio Yalpiz",
        "primary": RGBColor(8, 40, 32),
        "accent": RGBColor(16, 185, 129),
        "accent_secondary": RGBColor(167, 243, 208),
        "bg_slide": RGBColor(8, 40, 32),
        "card_bg": RGBColor(14, 58, 48),
        "card_border": RGBColor(16, 185, 129),
        "text_dark": RGBColor(255, 255, 255),
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "PHARMACEUTICAL"
    },
    "med_cardio": {
        "name": "🫀 Kardiologiya & Qon Tomir Qizil",
        "primary": RGBColor(48, 12, 20),
        "accent": RGBColor(244, 63, 94),
        "accent_secondary": RGBColor(251, 113, 133),
        "bg_slide": RGBColor(48, 12, 20),
        "card_bg": RGBColor(68, 18, 28),
        "card_border": RGBColor(244, 63, 94),
        "text_dark": RGBColor(255, 255, 255),
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "CARDIOLOGY"
    },
    "med_dental": {
        "name": "🦷 Stomatologiya & Marvarid Oq",
        "primary": RGBColor(12, 34, 56),
        "accent": RGBColor(14, 165, 233),
        "accent_secondary": RGBColor(224, 242, 254),
        "bg_slide": RGBColor(12, 34, 56),
        "card_bg": RGBColor(20, 48, 76),
        "card_border": RGBColor(14, 165, 233),
        "text_dark": RGBColor(255, 255, 255),
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "DENTISTRY"
    },
    "med_lab": {
        "name": "🔬 Biotexnologiya & Genetika Laboratoriyasi",
        "primary": RGBColor(15, 23, 42),
        "accent": RGBColor(56, 189, 248),
        "accent_secondary": RGBColor(129, 140, 248),
        "bg_slide": RGBColor(15, 23, 42),
        "card_bg": RGBColor(26, 36, 62),
        "card_border": RGBColor(56, 189, 248),
        "text_dark": RGBColor(255, 255, 255),
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "BIO RESEARCH"
    },
    # ================= 3. BIZNES & MOLIYA =================
    "biz_pitch": {
        "name": "💼 Obsidian & Oltin Lux (Pitch Deck)",
        "primary": RGBColor(20, 20, 22),
        "accent": RGBColor(234, 179, 8),
        "accent_secondary": RGBColor(245, 158, 11),
        "bg_slide": RGBColor(20, 20, 22),
        "card_bg": RGBColor(34, 34, 38),
        "card_border": RGBColor(234, 179, 8),
        "text_dark": RGBColor(255, 255, 255),
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "PITCH DECK LUX"
    },
    "biz_bank": {
        "name": "📊 FinTech, Bank & Katta Moliya",
        "primary": RGBColor(10, 30, 59),
        "accent": RGBColor(56, 189, 248),
        "accent_secondary": RGBColor(96, 165, 250),
        "bg_slide": RGBColor(10, 30, 59),
        "card_bg": RGBColor(16, 44, 84),
        "card_border": RGBColor(56, 189, 248),
        "text_dark": RGBColor(255, 255, 255),
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "BANK & FINTECH"
    },
    "biz_crypto": {
        "name": "🪙 Kriptovalyuta & Blokcheyn",
        "primary": RGBColor(13, 27, 30),
        "accent": RGBColor(16, 185, 129),
        "accent_secondary": RGBColor(245, 158, 11),
        "bg_slide": RGBColor(13, 27, 30),
        "card_bg": RGBColor(22, 42, 46),
        "card_border": RGBColor(16, 185, 129),
        "text_dark": RGBColor(255, 255, 255),
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "CRYPTO & DEFI"
    },
    "biz_marketing": {
        "name": "🚀 Marketing, Savdo & E-Commerce",
        "primary": RGBColor(36, 16, 40),
        "accent": RGBColor(249, 115, 22),
        "accent_secondary": RGBColor(236, 72, 153),
        "bg_slide": RGBColor(36, 16, 40),
        "card_bg": RGBColor(54, 24, 60),
        "card_border": RGBColor(249, 115, 22),
        "text_dark": RGBColor(255, 255, 255),
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "MARKETING & SALES"
    },
    "biz_lead": {
        "name": "🏆 Korporativ Boshqaruv & Liderlik",
        "primary": RGBColor(50, 10, 14),
        "accent": RGBColor(239, 68, 68),
        "accent_secondary": RGBColor(248, 113, 113),
        "bg_slide": RGBColor(50, 10, 14),
        "card_bg": RGBColor(72, 16, 22),
        "card_border": RGBColor(239, 68, 68),
        "text_dark": RGBColor(255, 255, 255),
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "LEADERSHIP"
    },
    # ================= 4. OTM & ILMIY TADQIQOTLAR =================
    "academic_royal": {
        "name": "🎓 Royal Academic Blue (OTM & Diplom)",
        "primary": RGBColor(10, 25, 49),
        "accent": RGBColor(245, 158, 11),
        "accent_secondary": RGBColor(96, 165, 250),
        "bg_slide": RGBColor(10, 25, 49),
        "card_bg": RGBColor(18, 38, 72),
        "card_border": RGBColor(245, 158, 11),
        "text_dark": RGBColor(255, 255, 255),
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "ROYAL ACADEMIC"
    },
    "academic_phd": {
        "name": "📜 Ilmiy Dissertatsiya & Monografiya",
        "primary": RGBColor(36, 24, 18),
        "accent": RGBColor(217, 119, 6),
        "accent_secondary": RGBColor(251, 191, 36),
        "bg_slide": RGBColor(36, 24, 18),
        "card_bg": RGBColor(52, 34, 26),
        "card_border": RGBColor(217, 119, 6),
        "text_dark": RGBColor(255, 255, 255),
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "PHD DISSERTATION"
    },
    "academic_research": {
        "name": "📚 Ilmiy Maqola & Scopus Jurnallar",
        "primary": RGBColor(21, 30, 46),
        "accent": RGBColor(34, 211, 238),
        "accent_secondary": RGBColor(165, 180, 252),
        "bg_slide": RGBColor(21, 30, 46),
        "card_bg": RGBColor(32, 44, 68),
        "card_border": RGBColor(34, 211, 238),
        "text_dark": RGBColor(255, 255, 255),
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "SCOPUS RESEARCH"
    },
    # ================= 5. TA'LIM & PEDAGOGIKA =================
    "edu_pedagogy": {
        "name": "📚 Zamonaviy Pedagogika & Maktab Metodikasi",
        "primary": RGBColor(60, 22, 8),
        "accent": RGBColor(249, 115, 22),
        "accent_secondary": RGBColor(251, 191, 36),
        "bg_slide": RGBColor(60, 22, 8),
        "card_bg": RGBColor(84, 32, 14),
        "card_border": RGBColor(249, 115, 22),
        "text_dark": RGBColor(255, 255, 255),
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "MODERN PEDAGOGY"
    },
    "edu_psychology": {
        "name": "🧠 Psixologiya & Kognitiv Rivojlanish",
        "primary": RGBColor(32, 20, 53),
        "accent": RGBColor(192, 132, 252),
        "accent_secondary": RGBColor(244, 114, 182),
        "bg_slide": RGBColor(32, 20, 53),
        "card_bg": RGBColor(48, 30, 78),
        "card_border": RGBColor(192, 132, 252),
        "text_dark": RGBColor(255, 255, 255),
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "PSYCHOLOGY"
    },
    "edu_kids": {
        "name": "🎈 Maktabgacha & Bolalar Ta'limi",
        "primary": RGBColor(24, 40, 59),
        "accent": RGBColor(251, 191, 36),
        "accent_secondary": RGBColor(52, 211, 153),
        "bg_slide": RGBColor(24, 40, 59),
        "card_bg": RGBColor(36, 58, 84),
        "card_border": RGBColor(251, 191, 36),
        "text_dark": RGBColor(255, 255, 255),
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "CHILD EDUCATION"
    },
    "edu_languages": {
        "name": "🗣 Xorijiy Tillar & Lingvistika",
        "primary": RGBColor(14, 38, 56),
        "accent": RGBColor(56, 189, 248),
        "accent_secondary": RGBColor(244, 63, 94),
        "bg_slide": RGBColor(14, 38, 56),
        "card_bg": RGBColor(22, 54, 78),
        "card_border": RGBColor(56, 189, 248),
        "text_dark": RGBColor(255, 255, 255),
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "LINGUISTICS"
    },
    # ================= 6. TARIX, HUQUQ & FALSAFA =================
    "history_heritage": {
        "name": "🏛 O'zbekiston Tarixi & Madaniy Meros",
        "primary": RGBColor(56, 30, 13),
        "accent": RGBColor(245, 158, 11),
        "accent_secondary": RGBColor(217, 119, 6),
        "bg_slide": RGBColor(56, 30, 13),
        "card_bg": RGBColor(78, 42, 20),
        "card_border": RGBColor(245, 158, 11),
        "text_dark": RGBColor(255, 255, 255),
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "HISTORY & HERITAGE"
    },
    "law_justice": {
        "name": "⚖️ Yuridik Huquq & Sud Tizimi",
        "primary": RGBColor(28, 25, 23),
        "accent": RGBColor(226, 232, 240),
        "accent_secondary": RGBColor(202, 138, 4),
        "bg_slide": RGBColor(28, 25, 23),
        "card_bg": RGBColor(44, 40, 36),
        "card_border": RGBColor(202, 138, 4),
        "text_dark": RGBColor(255, 255, 255),
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "LAW & JUSTICE"
    },
    "humanities_uzbek": {
        "name": "📖 O'zbek Tili & Milliy Adabiyot",
        "primary": RGBColor(46, 16, 38),
        "accent": RGBColor(244, 114, 182),
        "accent_secondary": RGBColor(234, 179, 8),
        "bg_slide": RGBColor(46, 16, 38),
        "card_bg": RGBColor(68, 24, 56),
        "card_border": RGBColor(244, 114, 182),
        "text_dark": RGBColor(255, 255, 255),
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "UZBEK LITERATURE"
    },
    "humanities_philosophy": {
        "name": "🗿 Falsafa, Mantiq & Jamiyatshunoslik",
        "primary": RGBColor(36, 34, 32),
        "accent": RGBColor(251, 191, 36),
        "accent_secondary": RGBColor(148, 163, 184),
        "bg_slide": RGBColor(36, 34, 32),
        "card_bg": RGBColor(52, 48, 46),
        "card_border": RGBColor(251, 191, 36),
        "text_dark": RGBColor(255, 255, 255),
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "PHILOSOPHY"
    },
    # ================= 7. ANIQ VA TABIIY FANLAR, MUHANDISLIK =================
    "eng_math": {
        "name": "📐 Oliy Matematika & Chizma Geometriya",
        "primary": RGBColor(10, 28, 56),
        "accent": RGBColor(56, 189, 248),
        "accent_secondary": RGBColor(96, 165, 250),
        "bg_slide": RGBColor(10, 28, 56),
        "card_bg": RGBColor(18, 42, 80),
        "card_border": RGBColor(56, 189, 248),
        "text_dark": RGBColor(255, 255, 255),
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "MATH & BLUEPRINT"
    },
    "sci_physics": {
        "name": "🌌 Kosmos, Kvant Fizikasi & Astronomiya",
        "primary": RGBColor(7, 11, 25),
        "accent": RGBColor(129, 140, 248),
        "accent_secondary": RGBColor(192, 132, 252),
        "bg_slide": RGBColor(7, 11, 25),
        "card_bg": RGBColor(16, 24, 48),
        "card_border": RGBColor(129, 140, 248),
        "text_dark": RGBColor(255, 255, 255),
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "SPACE & PHYSICS"
    },
    "sci_chemistry": {
        "name": "🧪 Kimyo & Laboratoriya Reaksiyalari",
        "primary": RGBColor(6, 36, 32),
        "accent": RGBColor(45, 212, 191),
        "accent_secondary": RGBColor(163, 230, 53),
        "bg_slide": RGBColor(6, 36, 32),
        "card_bg": RGBColor(12, 52, 46),
        "card_border": RGBColor(45, 212, 191),
        "text_dark": RGBColor(255, 255, 255),
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "CHEMISTRY LAB"
    },
    "eng_civil": {
        "name": "🏗 Qurilish, Geodeziya & Arxitektura",
        "primary": RGBColor(31, 36, 45),
        "accent": RGBColor(249, 115, 22),
        "accent_secondary": RGBColor(251, 191, 36),
        "bg_slide": RGBColor(31, 36, 45),
        "card_bg": RGBColor(45, 52, 64),
        "card_border": RGBColor(249, 115, 22),
        "text_dark": RGBColor(255, 255, 255),
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "CIVIL ENGINEERING"
    },
    "eng_energy": {
        "name": "⚡️ Energetika & Qayta Tiklanuvchi Quvvat",
        "primary": RGBColor(24, 34, 21),
        "accent": RGBColor(234, 179, 8),
        "accent_secondary": RGBColor(34, 197, 94),
        "bg_slide": RGBColor(24, 34, 21),
        "card_bg": RGBColor(36, 50, 32),
        "card_border": RGBColor(234, 179, 8),
        "text_dark": RGBColor(255, 255, 255),
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "POWER & ENERGY"
    },
    # ================= 8. EKOLOGIYA, QISHLOQ & SUV XO'JALIGI =================
    "eco_green": {
        "name": "🌿 Ekologiya & Yashil Makon",
        "primary": RGBColor(6, 51, 32),
        "accent": RGBColor(16, 185, 129),
        "accent_secondary": RGBColor(52, 211, 153),
        "bg_slide": RGBColor(6, 51, 32),
        "card_bg": RGBColor(10, 72, 46),
        "card_border": RGBColor(16, 185, 129),
        "text_dark": RGBColor(255, 255, 255),
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "ECOLOGY & NATURE"
    },
    "agro_harvest": {
        "name": "🌾 Qishloq Xo'jaligi & Agrotexnologiya",
        "primary": RGBColor(41, 30, 10),
        "accent": RGBColor(234, 179, 8),
        "accent_secondary": RGBColor(132, 204, 22),
        "bg_slide": RGBColor(41, 30, 10),
        "card_bg": RGBColor(58, 42, 16),
        "card_border": RGBColor(234, 179, 8),
        "text_dark": RGBColor(255, 255, 255),
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "AGRICULTURE"
    },
    "water_hydro": {
        "name": "💧 Gidrologiya & Suv Resurslari",
        "primary": RGBColor(8, 44, 60),
        "accent": RGBColor(6, 182, 212),
        "accent_secondary": RGBColor(56, 189, 248),
        "bg_slide": RGBColor(8, 44, 60),
        "card_bg": RGBColor(14, 62, 84),
        "card_border": RGBColor(6, 182, 212),
        "text_dark": RGBColor(255, 255, 255),
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "HYDROLOGY"
    },
    # ================= 9. SAN'AT, SPORT & TURIZM =================
    "art_design": {
        "name": "🎨 Zamonaviy San'at & Grafik Dizayn",
        "primary": RGBColor(40, 17, 34),
        "accent": RGBColor(244, 63, 94),
        "accent_secondary": RGBColor(251, 146, 60),
        "bg_slide": RGBColor(40, 17, 34),
        "card_bg": RGBColor(58, 25, 50),
        "card_border": RGBColor(244, 63, 94),
        "text_dark": RGBColor(255, 255, 255),
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "CREATIVE DESIGN"
    },
    "tourism_uzbek": {
        "name": "🕌 Samarqand Firuzasi & O'zbekiston Turizmi",
        "primary": RGBColor(7, 43, 56),
        "accent": RGBColor(56, 189, 248),
        "accent_secondary": RGBColor(251, 191, 36),
        "bg_slide": RGBColor(7, 43, 56),
        "card_bg": RGBColor(12, 62, 80),
        "card_border": RGBColor(56, 189, 248),
        "text_dark": RGBColor(255, 255, 255),
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "TOURISM & SILK ROAD"
    },
    "sport_fitness": {
        "name": "🏅 Sport, Fitnes & Dinamik Atletika",
        "primary": RGBColor(17, 24, 39),
        "accent": RGBColor(132, 204, 22),
        "accent_secondary": RGBColor(34, 197, 94),
        "bg_slide": RGBColor(17, 24, 39),
        "card_bg": RGBColor(28, 38, 58),
        "card_border": RGBColor(132, 204, 22),
        "text_dark": RGBColor(255, 255, 255),
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "SPORT & FITNESS"
    },
    "art_music": {
        "name": "🎵 Musiqa San'ati & Sahna Madaniyati",
        "primary": RGBColor(34, 14, 46),
        "accent": RGBColor(217, 70, 239),
        "accent_secondary": RGBColor(168, 85, 247),
        "bg_slide": RGBColor(34, 14, 46),
        "card_bg": RGBColor(50, 22, 68),
        "card_border": RGBColor(217, 70, 239),
        "text_dark": RGBColor(255, 255, 255),
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "MUSIC & STAGE"
    },
    # ================= 10. MINIMALIST & DAVLAT BOSHQARUVI =================
    "minimal_platinum": {
        "name": "✨ Toza Monoxrom Tipografika",
        "primary": RGBColor(17, 24, 39),
        "accent": RGBColor(241, 245, 249),
        "accent_secondary": RGBColor(148, 163, 184),
        "bg_slide": RGBColor(17, 24, 39),
        "card_bg": RGBColor(26, 36, 54),
        "card_border": RGBColor(241, 245, 249),
        "text_dark": RGBColor(255, 255, 255),
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "CLEAN MONO"
    },
    "gov_official": {
        "name": "🏛 Davlat Boshqaruvi & Rasmiy Strategiya",
        "primary": RGBColor(13, 30, 56),
        "accent": RGBColor(234, 179, 8),
        "accent_secondary": RGBColor(56, 189, 248),
        "bg_slide": RGBColor(13, 30, 56),
        "card_bg": RGBColor(20, 44, 80),
        "card_border": RGBColor(234, 179, 8),
        "text_dark": RGBColor(255, 255, 255),
        "text_muted": RGBColor(226, 232, 240),
        "white": RGBColor(255, 255, 255),
        "bullet_icon": "✦",
        "tag": "OFFICIAL GOVERNMENT"
    }
}

# Gamma va yo'nalishlar taxalluslar (aliases)
THEMES["gamma_cyber"] = THEMES["cyber"]
THEMES["gamma_violet"] = THEMES["ai_violet"]
THEMES["gamma_obsidian"] = THEMES["biz_pitch"]
THEMES["gamma_ocean"] = THEMES["biz_bank"]
THEMES["gamma_crimson"] = THEMES["biz_lead"]
THEMES["gamma_amber"] = THEMES["history_heritage"]
THEMES["gamma_solar"] = THEMES["edu_pedagogy"]
THEMES["gamma_emerald"] = THEMES["med_clinic"]
THEMES["gamma_nordic"] = THEMES["med_lab"]
THEMES["gamma_pastel"] = THEMES["art_design"]
THEMES["gamma_mono"] = THEMES["minimal_platinum"]
THEMES["gamma_forest"] = THEMES["eco_green"]
THEMES["gamma_space"] = THEMES["sci_physics"]
THEMES["gamma_blueprint"] = THEMES["eng_math"]
THEMES["gamma"] = THEMES["office"]
THEMES["gamma_auto"] = THEMES["office"]
THEMES["auto"] = THEMES["office"]

# Moslik uchun taxalluslar (aliases)
THEMES["tech"] = THEMES["cyber"]
THEMES["business"] = THEMES["biz_pitch"]
THEMES["nature"] = THEMES["eco_green"]
THEMES["science"] = THEMES["sci_physics"]
THEMES["art"] = THEMES["art_design"]
THEMES["history"] = THEMES["history_heritage"]

def detect_theme(topic: str, ai_theme: str = "") -> str:
    """Mavzu matniga qarab har bir yo'nalish uchun mos rang va fon mavzusini aniqlaydi."""
    ai_theme = (ai_theme or "").lower().strip()
    if ai_theme in THEMES:
        return ai_theme
        
    t = topic.lower()
    
    # 1. Sun'iy intellekt va robototexnika (neyron tarmoqlar ham shu yerda)
    if any(k in t for k in ["sun'iy intellekt", " ai", "ai ", "neyron", "robot", "mashinaviy o'rganish", "machine learning", "deep learning", "chatgpt", "generativ"]):
        return "ai_violet"
    # 2. Kiberxavfsizlik va kompyuter tarmoqlari
    if any(k in t for k in ["kiber", "cyber", "xavfsizlik", "tarmoq", "hujum", "hacker", "firewall", "shifrlash", "vpn", "antivirus", "parol"]):
        return "cyber"
    # 3. Dasturlash va axborot texnologiyalari
    if any(k in t for k in ["dastur", "program", "python", "java", "javascript", "c++", "c#", "kod", "algoritm", "backend", "frontend", "devops", "linux", "sql"]):
        return "tech_matrix"
    # 4. Bulutli texnologiyalar va Big Data
    if any(k in t for k in ["bulut", "cloud", "aws", "azure", "katta ma'lumot", "big data", "server", "data science", "infratuzilma"]):
        return "tech_cloud"
    # 5. Mobil dasturlash
    if any(k in t for k in ["mobil", "android", "ios", "flutter", "swift", "kotlin", "smartfon"]):
        return "tech_mobile"
        
    # 6. Tibbiyot - Kardiologiya va jarrohlik
    if any(k in t for k in ["yurak", "qon tomir", "kardiolog", "jarroh", "operatsiya", "infarkt", "qon bosimi"]):
        return "med_cardio"
    # 7. Tibbiyot - Stomatologiya
    if any(k in t for k in ["stomatolog", "tish", "plomba", "karies", "ortodont", "implant"]):
        return "med_dental"
    # 8. Tibbiyot - Farmatsevtika va dori vositalari
    if any(k in t for k in ["farmatsevt", "dori", "preparat", "vaksina", "antibiotik", "farmakologiya"]):
        return "med_pharma"
    # 9. Tibbiyot - Biotexnologiya va genetika
    if any(k in t for k in ["genetika", "dnk", "laboratoriya", "biotexnolog", "hujayra", "gen", "klonlash", "mikrobiolog"]):
        return "med_lab"
    # 10. Tibbiyot - Umumiy terapiya va shifoxona
    if any(k in t for k in ["tibbiyot", "klinika", "vrach", "shifokor", "davolash", "terapiya", "kasallik", "anatomiya", "patologiya"]):
        return "med_clinic"

    # 11. Biznes - Kriptovalyuta va blokcheyn
    if any(k in t for k in ["kripto", "bitcoin", "blokcheyn", "blockchain", "ethereum", "web3", "defi"]):
        return "biz_crypto"
    # 12. Biznes - Startap, pitch deck va investitsiya
    if any(k in t for k in ["pitch deck", "startap", "investitsiya", "biznes reja", "venture", "kapital"]):
        return "biz_pitch"
    # 13. Biznes - Marketing, reklama va savdo
    if any(k in t for k in ["marketing", "reklama", "smm", "savdo", "bozor", "e-commerce", "mijoz", "brend", "pr"]):
        return "biz_marketing"
    # 14. Biznes - Boshqaruv va korporativ liderlik
    if any(k in t for k in ["boshqaruv", "menejment", "liderlik", "rahbar", "strategiya", "korporativ"]):
        return "biz_lead"
    # 15. Biznes - Bank, moliya, sug'urta va hisob
    if any(k in t for k in ["bank", "moliya", "iqtisod", "kredit", "depozit", "sug'urta", "audit", "soliq", "buxgalter"]):
        return "biz_bank"

    # 16. OTM - Dissertatsiya va monografiya
    if any(k in t for k in ["dissertatsiya", "phd", "monografiya", "fan nomzodi", "doktorant"]):
        return "academic_phd"
    # 17. OTM - Ilmiy maqola va scopus
    if any(k in t for k in ["scopus", "maqola", "jurnal", "ilmiy tadqiqot", "retsenziya", "metodologiya"]):
        return "academic_research"
    # 18. OTM - Diplom va talabalik
    if any(k in t for k in ["universitet", "otm", "diplom", "magistr", "bakalavr", "kurs ishi", "talaba"]):
        return "academic_royal"

    # 19. Ta'lim - Psixologiya
    if any(k in t for k in ["psixolog", "ruhiyat", "stress", "temperament", "xarakter", "kognitiv", "munosabat"]):
        return "edu_psychology"
    # 20. Ta'lim - Maktabgacha ta'lim
    if any(k in t for k in ["bog'cha", "maktabgacha", "kichkintoy", "bola"]):
        return "edu_kids"
    # 21. Ta'lim - Xorijiy tillar
    if any(k in t for k in ["ingliz tili", "english", "ielts", "nemis", "fransuz", "rus tili", "tilshunoslik", "tarjima"]):
        return "edu_languages"
    # 22. Ta'lim - Pedagogika va maktab ta'limi
    if any(k in t for k in ["pedagog", "metodika", "dars", "maktab", "o'qituvchi", "ta'lim", "tarbiya", "sinf"]):
        return "edu_pedagogy"

    # 23. Huquq va adliya
    if any(k in t for k in ["huquq", "yuridik", "konstitutsiya", "sud", "qonun", "prokuror", "advokat", "jinoyat", "fuqarolik"]):
        return "law_justice"
    # 24. O'zbek tili va adabiyot
    if any(k in t for k in ["adabiyot", "navoiy", "she'r", "g'azal", "roman", "shoir", "yozuvchi", "ona tili"]):
        return "humanities_uzbek"
    # 25. Falsafa va mantiq
    if any(k in t for k in ["falsafa", "mantiq", "etika", "estetika", "dunyoqarash"]):
        return "humanities_philosophy"
    # 26. Tarix va madaniy meros
    if any(k in t for k in ["tarix", "history", "qadimgi", "sulol", "amir temur", "bobur", "xonlik", "arxeolog", "jadid", "asr"]):
        return "history_heritage"

    # 27. Kimyo va laboratoriya
    if any(k in t for k in ["kimyo", "organik", "molekula", "reaksiya", "eritma", "polimer", "kimyoviy"]):
        return "sci_chemistry"
    # 28. Fizika va kosmos
    if any(k in t for k in ["fizika", "kosmos", "astronom", "koinot", "sayyora", "kvant", "yadro", "optika", "galaktika"]):
        return "sci_physics"
    # 29. Qurilish va arxitektura
    if any(k in t for k in ["qurilish", "arxitektura", "bino", "inshoot", "geodeziya", "loyiha", "chizma"]):
        return "eng_civil"
    # 30. Energetika va quvvat
    if any(k in t for k in ["energetika", "elektr", "quyosh paneli", "atom", "gidroelektro", "neft", "gaz", "yoqilg'i"]):
        return "eng_energy"
    # 31. Oliy matematika va hisoblash
    if any(k in t for k in ["matematika", "algebra", "geometriya", "integral", "tenglama", "differensial", "matritsa"]):
        return "eng_math"

    # 32. Qishloq xo'jaligi va agrar
    if any(k in t for k in ["qishloq xo'jaligi", "agrar", "paxta", "g'alla", "hosil", "dehqon", "chorvachilik", "o'simlik", "urug'"]):
        return "agro_harvest"
    # 33. Gidrologiya va suv resurslari
    if any(k in t for k in ["suv", "gidrolog", "daryo", "ko'l", "sug'orish", "melioratsiya", "kanal"]):
        return "water_hydro"
    # 34. Ekologiya va tabiat
    if any(k in t for k in ["ekolog", "tabiat", "yashil", "atrof-muhit", "iqlim", "atmosfera", "o'rmon"]):
        return "eco_green"

    # 35. Sport va fitnes
    if any(k in t for k in ["sport", "futbol", "fitnes", "mashg'ulot", "olimpiada", "jismoniy", "musobaqa"]):
        return "sport_fitness"
    # 36. Turizm va mehmondo'stlik
    if any(k in t for k in ["turizm", "sayyoh", "mehmonxona", "samarqand", "buxoro", "ipak yo'li"]):
        return "tourism_uzbek"
    # 37. Musiqa va teatr
    if any(k in t for k in ["musiqa", "cholg'u", "qo'shiq", "opera", "teatr", "konsert"]):
        return "art_music"
    # 38. San'at va dizayn
    if any(k in t for k in ["san'at", "dizayn", "grafika", "rang", "tasviriy", "haykaltarosh"]):
        return "art_design"

    # 35. San'at va dizayn
    if any(k in t for k in ["san'at", "dizayn", "grafika", "rang", "tasviriy", "haykaltarosh"]):
        return "art_design"
    # 36. Turizm va mehmondo'stlik
    if any(k in t for k in ["turizm", "sayyoh", "mehmonxona", "samarqand", "buxoro", "ipak yo'li"]):
        return "tourism_uzbek"
    # 37. Sport va fitnes
    if any(k in t for k in ["sport", "futbol", "fitnes", "mashg'ulot", "olimpiada", "jismoniy", "musobaqa"]):
        return "sport_fitness"
    # 38. Musiqa va teatr
    if any(k in t for k in ["musiqa", "cholg'u", "qo'shiq", "opera", "teatr", "konsert"]):
        return "art_music"

    # 39. Davlat boshqaruvi va vazirliklar
    if any(k in t for k in ["davlat", "vazirlik", "hokimiyat", "prezident", "davlat xizmati", "qaror", "farmon"]):
        return "gov_official"

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
    num_agenda = min(num_content, 5) if num_content >= 3 else num_content

    prompt = f"""
Siz universitet va oliy ta'lim talabalari uchun akademik va professional taqdimotlar tayyorlovchi yetuk AI mutaxassisiz.

FOYDALANUVCHI YUBORGAN TAQDIMOT MAVZUSI VA TALABLARI:
\"\"\"
{topic.strip()}
\"\"\"{author_clause}{theme_clause}{context_clause}

======================================================================
ENG ASOSIY TALAB: REJADAGI BARCHA BANDLAR SLAYDLARDA 100% TUSHUNTIRILSIN!
HAR BIR SLAYDDA QAYSI REJA BANDI TUSHUNTIRILAYOTGANI ANIQ BELGILANSIN!
SLAYDDA MUTLAQO BO'SH JOY QOLMASIN!
======================================================================
1. TAQDIMOT REJASI ("agenda") VA SLAYDLAR BIR-BIRIGA 100% MOS KELSIN:
- 'agenda' massivida taqdimot mavzusi bo'yicha RO'PPA-ROSA {num_agenda} ta ketma-ket, bir-birini to'ldiruvchi asosiy ilmiy reja bandi tuzing.
- Reja bandlari mavzuning barcha asosiy qismlarini to'liq qamrab olsin (masalan: 1-reja: Asosiy tushunchalar va topologiyalar; 2-reja: Standartlar va modellar; 3-reja: Aloqa texnologiyalari; 4-reja: Xavfsizlik va himoya).
- 'slides' massividagi BARCHA {num_content} ta slayd aynan 'agenda' dagi reja bandlarini 1-banddan boshlab tartib bilan to'liq, chuqur va bafurja tushuntirib bersin!
- REJADAGI BIRORTA HAM BAND TASHAB KETILMASIN! Foydalanuvchi rejadagi barcha ma'lumotlar slaydlarda to'liq tushuntirilishini talab qildi.

2. HAR BIR SLAYDDA QAYSI REJA TUSHUNTIRILAYOTGANINI ANIQ BELGILASH:
- 'slides' dagi har bir slayd obyektida quyidagi maydonlar qat'iy bo'lsin:
  * "agenda_num": Ushbu slayd qaysi reja bandiga tegishli (1, 2, 3 ...);
  * "agenda_title": Reja bandining to'liq nomi;
  * "title": Shu reja bandini tushuntiruvchi aniq, salmoqli ilmiy sarlavha;

3. SLAYDNING HAR BIR BURCHAGINI MAZMUN BILAN TO'LDIRISH (ZERO EMPTY SPACE):
- Slaydlar hech qachon 1-2 qator qisqa gaplar bilan bo'm-bo'sh, yarim-yorti tashlab ketilmasligi SHART!
- Har bir slayd, har bir kartochka va har bir ustun pastigacha to'liq, mazmunli va mukammal infografik matn bilan to'ldirilishi kerak.

4. HAR BIR LAYOUT UCHUN TO'LIQ VA BOYITILGAN TARKIB:
A) "steps" (Bosqichlar / Jarayonlar / Texnologiyalar) layouti uchun:
  - 'steps_data' ichida roppa-rosa 3 ta asosiy bosqich yoki texnologiya bo'lsin ("step": "01", "02", "03").
  - Har bir bosqichda:
    * "title": Bosqich / texnologiyaning aniq, salmoqli nomi;
    * "desc": Ushbu bosqichning asosiy ilmiy-texnik mohiyati, ishlash mexanizmi va vazifalarini chuqur tahlil qiluvchi 2-3 ta to'liq jumladan iborat KENG QAMROVLI matn (kamida 25-35 so'z!). Shunchaki 2-3 so'z yozish QAT'IYAN TAQIQLANADI!
    * "points": Har bir bosqichning 2 ta asosiy texnik ko'rsatkichi, standarti yoki amaliy xususiyatini yorituvchi bandlar (har biri "Kalit atama: Tushuntirish" shaklida 15-20 so'z).
    Shunda har bir kartochka yuqoridan pastgacha to'liq ma'lumotga to'ladi!

B) "kpi" (Statistika / Asosiy ko'rsatkichlar / Raqamlar) layouti uchun:
  - 'kpi_items' ichida roppa-rosa 3 ta asosiy ko'rsatkich bo'lsin.
  - Har bir elementda:
    * "number": Aniq raqam, foiz, yil yoki texnik ko'rsatkich (masalan: "99.9%", "10 Gbit/s", "1984-yil", "7 qatlam");
    * "label": Ko'rsatkichning aniq ilmiy/texnik nomi;
    * "desc": Ushbu ko'rsatkichning sohadagi roli va ahamiyatini yorituvchi 2-3 ta tahliliy jumladan iborat KENG QAMROVLI matn (kamida 25-35 so'z!).
    * "points": Ushbu ko'rsatkichga oid 2 ta muhim ilmiy-amaliy fakt yoki standart (har biri 15-20 so'z).

C) "comparison" (Taqqoslash / Solishtirish) layouti uchun:
  - 'comparison_data' dagi 'col1_points' va 'col2_points' massivlarining har birida KAMIDA 4 tadan 5 tagacha chuqur tahliliy bandlar bo'lsin.
  - Har bir band: "Kalit mezon: Mazkur jihatning nazariy va amaliy tahlili, aniq parametrlar va taqqoslash xulosasi (25-35 so'z)".

D) "standard" (Umumiy mazmunli slaydlar) layouti uchun:
  - 'bullet_points' massivida KAMIDA 5 tadan 6 tagacha sifatli, chuqur va faktlarga boy bandlar bo'lsin.
  - Har bir band: "Kalit atama / tushuncha: Mazkur tushunchaning ilmiy-nazariy mohiyati, asosiy tamoyillari, aniq dalillar, qonuniyatlar, raqamlar va amaliyotdagi real ahamiyatini tushuntiruvchi 30-45 ta so'zdan iborat to'liq, chuqur tahliliy fikr".

5. SLAYD GIDROLOGIYASI VA STRUKTURASI:
- Titul (muqova), mundarija (reja), xulosa va adabiyotlar slaydlari dastur tomonidan avtomatik yaratiladi.
- Shu sababli 'slides' massividagi BARCHA {num_content} ta slayd 100% BEVOSITA MAVZUNING O'ZIGA bag'ishlansin!
- 'slides' boshida quruq "Kirish" yoki oxirida ortiqcha "Xulosa" kabi slaydlar qo'shilmasin — barcha slaydlar bevosita mavzuni to'liq yoritish uchun ishlatilsin!

6. XULOSA VA ADABIYOTLAR:
- 'conclusion': 4-5 ta chuqur, tahliliy xulosalar (sohaning nazariy, amaliy va kelajakdagi rivojlanishiga doir, har biri 25-35 so'z).
- 'references': 4-5 ta to'liq akademik manbalar (muallif, kitob/maqola nomi, nashriyot, yili).

7. MA'RUZA NUTQI (SPEAKER_NOTES):
- Talaba doskada turib ushbu slaydni himoya qilayotganda gapirib beradigan 3-5 jumlalik jonli, ilmiy, tushunarli va professional ma'ruza matni bo'lsin.

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
  "cover_image_query": "Taqdimot muqovasi (titul slayd) uchun inglizcha 2-3 ta aniq qidiruv so'zi (masalan: 'computer network infrastructure')",
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
    "Foydalanuvchi mavzusining 4-asosiy yo'nalishi",
    "Foydalanuvchi mavzusining 5-asosiy yo'nalishi"
  ],
  "slides": [
    {{
      "slide_number": 1,
      "type": "content",
      "layout": "standard / kpi / comparison / steps",
      "title": "Foydalanuvchi yuborgan mavzuning 1-yo'nalishi bo'yicha aniq mazmuniy sarlavha",
      "kpi_items": [
        {{
          "number": "85%",
          "label": "Ko'rsatkich yoki statistika nomi",
          "desc": "Mazkur ko'rsatkichning sohadagi roli va ahamiyatini yorituvchi 2-3 ta tahliliy jumlali batafsil tushuntirish matni (25-35 so'z).",
          "points": [
            "Asosiy mezon yoki parametr: Texnik standartlar va dalillar tahlili",
            "Amaliyotdagi samaradorligi: Tizimdagi real natijalar va iqtisodiy samara"
          ]
        }},
        {{
          "number": "2.4x",
          "label": "Samaradorlik ko'rsatkichi",
          "desc": "Mazkur ko'rsatkichning sohadagi roli va ahamiyatini yorituvchi 2-3 ta tahliliy jumlali batafsil tushuntirish matni (25-35 so'z).",
          "points": [
            "Asosiy mezon yoki parametr: Texnik standartlar va dalillar tahlili",
            "Amaliyotdagi samaradorligi: Tizimdagi real natijalar va iqtisodiy samara"
          ]
        }},
        {{
          "number": "100+",
          "label": "Qamrov va standartlar",
          "desc": "Mazkur ko'rsatkichning sohadagi roli va ahamiyatini yorituvchi 2-3 ta tahliliy jumlali batafsil tushuntirish matni (25-35 so'z).",
          "points": [
            "Asosiy mezon yoki parametr: Texnik standartlar va dalillar tahlili",
            "Amaliyotdagi samaradorligi: Tizimdagi real natijalar va iqtisodiy samara"
          ]
        }}
      ],
      "comparison_data": {{
        "col1_title": "1-yo'nalish yoki an'anaviy tizim",
        "col1_points": [
          "1-muhim parametr / atama: Mazkur jihatning nazariy va amaliy mohiyati, aniq parametrlar tahlili (25-35 so'z)",
          "2-muhim parametr / atama: Texnik yoki amaliy samaradorlik ko'rsatkichlari (25-35 so'z)",
          "3-muhim parametr / atama: Sohadagi afzalliklari va imkoniyatlari (25-35 so'z)",
          "4-muhim parametr / atama: Cheklovlari yoki kamchiliklari bo'yicha ilmiy tahlil (25-35 so'z)"
        ],
        "col2_title": "2-yo'nalish yoki innovatsion tizim",
        "col2_points": [
          "1-muhim parametr / atama: Zamonaviy va innovatsion yondashuvning asosiy mohiyati (25-35 so'z)",
          "2-muhim parametr / atama: Yuqori tezlik, xavfsizlik va yangi standartlar tahlili (25-35 so'z)",
          "3-muhim parametr / atama: Asosiy afzalliklari va tizimli yutuqlari (25-35 so'z)",
          "4-muhim parametr / atama: Kelajak istiqbollari va rivojlanish tendensiyalari (25-35 so'z)"
        ]
      }},
      "steps_data": [
        {{
          "step": "01",
          "title": "1-bosqich / texnologiya nomi",
          "desc": "Ushbu bosqichning asosiy ilmiy-texnik mohiyati, ishlash mexanizmi va vazifalarini chuqur tahlil qiluvchi 2-3 ta to'liq jumlali tushuntirish (25-35 so'z).",
          "points": [
            "Texnik parametri yoki standarti: Aniq raqamlar va mezonlar tahlili (15-20 so'z)",
            "Amaliy afzalligi va roli: Real tizimlardagi samarasi va qo'llanilishi (15-20 so'z)"
          ]
        }},
        {{
          "step": "02",
          "title": "2-bosqich / texnologiya nomi",
          "desc": "Ushbu bosqichning asosiy ilmiy-texnik mohiyati, ishlash mexanizmi va vazifalarini chuqur tahlil qiluvchi 2-3 ta to'liq jumlali tushuntirish (25-35 so'z).",
          "points": [
            "Texnik parametri yoki standarti: Aniq raqamlar va mezonlar tahlili (15-20 so'z)",
            "Amaliy afzalligi va roli: Real tizimlardagi samarasi va qo'llanilishi (15-20 so'z)"
          ]
        }},
        {{
          "step": "03",
          "title": "3-bosqich / texnologiya nomi",
          "desc": "Ushbu bosqichning asosiy ilmiy-texnik mohiyati, ishlash mexanizmi va vazifalarini chuqur tahlil qiluvchi 2-3 ta to'liq jumlali tushuntirish (25-35 so'z).",
          "points": [
            "Texnik parametri yoki standarti: Aniq raqamlar va mezonlar tahlili (15-20 so'z)",
            "Amaliy afzalligi va roli: Real tizimlardagi samarasi va qo'llanilishi (15-20 so'z)"
          ]
        }}
      ],
      "bullet_points": [
        "1-muhim tushuncha / atama: Mazkur tushunchaning ilmiy-nazariy mohiyati, asosiy tamoyillari, aniq dalillar, qonuniyatlar, raqamlar va amaliyotdagi real ahamiyatini tushuntiruvchi 30-45 ta so'zdan iborat to'liq, chuqur tahliliy fikr.",
        "2-muhim tushuncha / atama: Mazkur yo'nalishning amaliy va texnologik mexanizmlari, standartlari va empirik tahlillarini yorituvchi 30-45 ta so'zdan iborat to'liq fikr.",
        "3-muhim tushuncha / atama: Sohadagi mavjud muammolar, innovatsion yechimlar va samaradorlik ko'rsatkichlari bo'yicha 30-45 ta so'zdan iborat ilmiy xulosa.",
        "4-muhim tushuncha / atama: Zamonaviy rivojlanish omillari, xalqaro tajriba va tatbiq etish mexanizmlari haqida 30-45 ta so'zdan iborat tahlil.",
        "5-muhim tushuncha / atama: Istiqbolli tendensiyalar, xavfsizlik va kelajakdagi rivojlanish yo'nalishlari bo'yicha 30-45 ta so'zdan iborat tahliliy xulosa."
      ],
      "speaker_notes": "Talaba himoya paytida ushbu slaydni tushuntirganda doskada turib aytishi kerak bo'lgan 3-5 jumlalik jonli va ilmiy ma'ruza nutqi.",
      "image_query": "Ushbu slayd uchun mavzuga mos inglizcha 1-3 ta aniq qidiruv so'zi (masalan: 'network topology infrastructure')"
    }}
  ],
  "conclusion": [
    "Asosiy ilmiy/amaliy xulosa 1: Mavzuning nazariy va amaliy asoslari bo'yicha chuqur tahliliy xulosa (25-35 so'z).",
    "Tahlillar natijasi bo'yicha xulosa 2: Sohadagi asosiy qonuniyatlar va samaradorlik ko'rsatkichlari (25-35 so'z).",
    "Amaliyotga tatbiq etish bo'yicha xulosa 3: Real tizimlarda qo'llash va iqtisodiy/texnik samaradorlik (25-35 so'z).",
    "Kelajak istiqbollari bo'yicha takliflar: Sohaning rivojlanish tendensiyalari va istiqbolli yo'nalishlari (25-35 so'z)."
  ],
  "references": [
    "1. Darslik yoki monografiya: Muallif, Kitob nomi, Nashriyot, Yil.",
    "2. Davlat standarti yoki me'yoriy-huquqiy hujjat: Standart nomi va raqami.",
    "3. Ilmiy jurnal maqolasi: Muallif, Maqola nomi, Jurnal nomi, Jild/Son, Yil.",
    "4. Xalqaro nufuzli ilmiy manba yoki rasmiy texnik hujjat (IEEE, ISO, RFC va h.k.)."
  ]
}}

Talablar:
- Jami mazmuniy slaydlar soni ('slides' massivida) roppa-rosa {num_content} taga teng bo'lsin (kam ham, ko'p ham bo'lmasin).
- TAQDIMOT REJASI ("agenda"): QAT'IY RAVISHDA ENG KO'PI 4 TAdan 5 TAgacha umumlashtirilgan asosiy reja bandlaridan iborat bo'lsin (hech qachon 5 tadan oshmasin).
- DIZAYN VA LAYOUT XILMA-XILLIGI (MUHIM): Taqdimot bir xil zerikarli bullet point bo'lib qolmasligi uchun slaydlarga mos layout tanlang:
  * "kpi" — Asosiy raqamlar, statistika yoki foizlar bo'lgan slaydlarga (kamida 1 ta slaydda ishlating, 3 ta ko'rsatkich berilsin, har birida raqam, sarlavha, batafsil desc va 2 ta texnik points bo'lsin);
  * "comparison" — Taqqoslash, solishtirish yoki ijobiy/salbiy tomonlar bo'lgan slaydga (kamida 1 ta slaydda ishlating, har bir tomonda 4-5 tadan chuqur band berilsin);
  * "steps" — Bosqichlar, jarayon yoki ketma-ketlik bo'lgan slaydga (3 ta bosqich, har birida nom, batafsil desc va 2 ta texnik points bo'lsin);
  * "standard" — Boshqa umumiy mazmunli slaydlar uchun (kamida 5 tadan 6 tagacha chuqur bullet_points va rasm).
  Har bir slaydga qaysi layout tanlanganidan qat'i nazar har doim to'liq "bullet_points" va "speaker_notes" ham yozilsin!
- QAT'IY TALAB: Taqdimot sarlavhalarida, reja bandlarida, slayd matnlarida, xulosada, manbalarda va ma'ruza nutqida MUTLAQO HECH QANDAY emoji, stiker, piktogramma yoki smayliklar ISHLATILMASIN! Taqdimot sof akademik, rasmiy va ilmiy uslubda bo'lsin.
- Har bir mazmuniy slayd foydalanuvchi so'ragan mavzularni chuqur, qiziqarli, dalillarga asoslangan holda to'liq yoritib bersin.
- Har bir slaydda 5 tadan 6 tagacha sifatli band (bullet_points) bo'lsin. Har bir band "Kalit so'z: Batafsil tavsif va tahlil" ko'rinishida yozilsin.
- Har bir slaydga talabaning himoyasi uchun speaker_notes (ma'ruza nutqi) yozilsin.
- Har bir slaydga va muqovaga mos inglizcha aniq image_query yozilsin.
- "references" maydonida kamida 4-5 ta haqiqiy va ishonarli adabiyot/manba bo'lsin.
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
    p.line_spacing = 1.18

    clean_txt = re.sub(r"^[\s•\-\*–—\d\.\)]+", "", remove_emojis(str(bullet_text))).strip()
    if not clean_txt:
        return

    # Har doim 100% tiniq oq rang va yorqin aksentlar (qora harflar butunlay chiqarib tashlangan)
    lead_color = theme.get("accent", RGBColor(255, 255, 255))
    body_color = RGBColor(255, 255, 255)

    # Bullet ikonkasi
    r_icon = p.add_run()
    r_icon.text = f"{theme.get('bullet_icon', '✦')}  "
    r_icon.font.bold = True
    r_icon.font.size = font_size
    r_icon.font.color.rgb = theme["accent"]
    r_icon.font.name = "Arial"

    # Kalit so'z va tavsifni ajratish (masalan: "Kalit so'z: Tavsif matni" yoki "Bosqich — Izoh")
    match = re.match(r"^([^:—–\-]{3,55}[:—–\-])\s*(.*)$", clean_txt)
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
    tag_tb = slide.shapes.add_textbox(Inches(0.9), Inches(0.12), Inches(10.0), Inches(0.28))
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

def _create_hero_slide(prs, blank_layout, theme, title_text, subtitle_text, total_slides, is_dark, custom_bg, images_map, lang_info=None, author_details=None):
    """Barcha taqdimotlar uchun 1-slayd: zamonaviy, xalqaro 16:9 Hero Master Slide (referat yoki daftar varog'i shakllisiz)."""
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

    # Capsule Badge on top left
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

    # Muallif ma'lumotlari mavjudligini aniqlash
    has_auth = bool(author_details and any(str(v).strip() for v in author_details.values() if v))
    stud_name = str(author_details.get("student") or "").strip() if has_auth else ""
    teach_name = str(author_details.get("teacher") or "").strip() if has_auth else ""
    uni_name = str(author_details.get("university") or "").strip() if has_auth else ""
    fac_name = str(author_details.get("faculty") or "").strip() if has_auth else ""
    grp_name = str(author_details.get("group") or "").strip() if has_auth else ""
    dir_name = str(author_details.get("direction") or "").strip() if has_auth else ""

    # Subtitle bo'sh bo'lib qolmasligi uchun kafolat
    if not subtitle_text or not subtitle_text.strip():
        subtitle_text = f"Mavzuning nazariy va amaliy asoslari bo'yicha kompleks ilmiy tahlil"

    if cover_img and os.path.exists(cover_img):
        t_box = topic_slide.shapes.add_textbox(Inches(0.9), Inches(1.25), Inches(7.0), Inches(1.8))
        t_tf = t_box.text_frame
        t_tf.word_wrap = True
        p_t = t_tf.paragraphs[0]
        p_t.text = remove_emojis(title_text)
        p_t.font.size = Pt(26 if len(title_text) > 40 else 30)
        p_t.font.bold = True
        p_t.font.color.rgb = theme["accent"]
        p_t.font.name = "Arial"

        p_sub = t_tf.add_paragraph()
        p_sub.text = remove_emojis(subtitle_text)
        p_sub.font.size = Pt(14)
        p_sub.font.color.rgb = theme["text_muted"]
        p_sub.font.name = "Arial"
        p_sub.space_before = Pt(6)

        card_l = Inches(0.9)
        card_t = Inches(3.25)
        card_w = Inches(7.0)
        card_h = Inches(3.8)

        # Chap blok uchun zamonaviy karta konteyneri
        bg_card = topic_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, card_l, card_t, card_w, card_h)
        bg_card.fill.solid()
        bg_card.fill.fore_color.rgb = theme.get("card_bg", RGBColor(24, 34, 58))
        bg_card.line.color.rgb = theme.get("accent", RGBColor(56, 189, 248))
        bg_card.line.width = Pt(1.2)
        try:
            bg_card.adjustments[0] = 0.04
        except Exception:
            pass

        bar_l = topic_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, card_l + Inches(0.3), card_t + Inches(0.12), card_w - Inches(0.6), Inches(0.04))
        bar_l.fill.solid()
        bar_l.fill.fore_color.rgb = theme["accent"]
        bar_l.line.fill.background()

        cl_box = topic_slide.shapes.add_textbox(card_l + Inches(0.2), card_t + Inches(0.22), card_w - Inches(0.4), card_h - Inches(0.32))
        cl_tf = cl_box.text_frame
        cl_tf.word_wrap = True

        if has_auth:
            p_auth_h = cl_tf.paragraphs[0]
            p_auth_h.text = "✦  TAQDIMOTCHI VA ILMIY RAHBAR"
            p_auth_h.font.size = Pt(14)
            p_auth_h.font.bold = True
            p_auth_h.font.color.rgb = theme["accent"]
            p_auth_h.space_after = Pt(10)

            auth_rows = []
            if stud_name:
                auth_rows.append(("Bajardi:", f"{stud_name}" + (f" ({grp_name})" if grp_name else "")))
            if teach_name:
                auth_rows.append(("Qabul qildi:", teach_name))
            if uni_name:
                auth_rows.append(("OTM:", uni_name + (f", {fac_name}" if fac_name else "")))
            if not auth_rows:
                auth_rows = [("Taqdimotchi:", "Talaba"), ("OTM:", "Universitet")]

            for a_lbl, a_val in auth_rows:
                p_r = cl_tf.add_paragraph()
                p_r.space_after = Pt(8)
                r_l = p_r.add_run()
                r_l.text = f"{a_lbl} "
                r_l.font.bold = True
                r_l.font.size = Pt(13)
                r_l.font.color.rgb = theme["accent"]

                r_v = p_r.add_run()
                r_v.text = a_val
                r_v.font.bold = False
                r_v.font.size = Pt(13)
                r_v.font.color.rgb = RGBColor(255, 255, 255)
        else:
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
                r_lbl.font.color.rgb = theme["accent"]

                r_txt = p.add_run()
                r_txt.text = p_desc
                r_txt.font.bold = False
                r_txt.font.size = Pt(13)
                r_txt.font.color.rgb = RGBColor(255, 255, 255)

        try:
            topic_slide.shapes.add_picture(cover_img, Inches(8.3), Inches(1.3), width=Inches(4.1), height=Inches(5.75))
        except Exception:
            pass
    else:
        t_box = topic_slide.shapes.add_textbox(Inches(1.3), Inches(1.5), Inches(10.7), Inches(2.3))
        t_tf = t_box.text_frame
        t_tf.word_wrap = True

        p_t = t_tf.paragraphs[0]
        p_t.text = remove_emojis(title_text)
        p_t.font.size = Pt(30 if len(title_text) > 45 else 35)
        p_t.font.bold = True
        p_t.font.color.rgb = theme["accent"]
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
        p_y = Inches(4.2)
        p_h = Inches(2.6)

        if has_auth:
            auth_cards = [
                ("✦  TALABA (BAJARDI)", stud_name or "Talaba", grp_name or dir_name or "Akademik guruh"),
                ("✦  TAʼLIM MUASSASASI", uni_name or "Universitet", fac_name or dir_name or "Fakultet"),
                ("✦  ILMIY RAHBAR", teach_name or "Oʻqituvchi", "Qabul qildi / Ilmiy maslahatchi")
            ]
            for p_i, (c_tag, c_val1, c_val2) in enumerate(auth_cards):
                px = p_start_x + p_i * (p_w + p_gap)

                p_card = topic_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, px, p_y, p_w, p_h)
                p_card.fill.solid()
                p_card.fill.fore_color.rgb = theme.get("card_bg", RGBColor(24, 34, 58))
                p_card.line.color.rgb = theme.get("accent", RGBColor(56, 189, 248))
                p_card.line.width = Pt(1.2)
                try:
                    p_card.adjustments[0] = 0.05
                except Exception:
                    pass

                c_bar = topic_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, px + Inches(0.25), p_y + Inches(0.12), p_w - Inches(0.5), Inches(0.04))
                c_bar.fill.solid()
                c_bar.fill.fore_color.rgb = theme["accent"]
                c_bar.line.fill.background()

                p_box = topic_slide.shapes.add_textbox(px + Inches(0.15), p_y + Inches(0.22), p_w - Inches(0.3), p_h - Inches(0.32))
                ptf = p_box.text_frame
                ptf.word_wrap = True
                pp1 = ptf.paragraphs[0]
                pp1.text = c_tag
                pp1.font.size = Pt(13)
                pp1.font.bold = True
                pp1.font.color.rgb = theme["accent"]
                pp1.alignment = PP_ALIGN.CENTER
                pp1.space_after = Pt(8)

                pp2 = ptf.add_paragraph()
                pp2.text = c_val1
                pp2.font.size = Pt(16)
                pp2.font.bold = True
                pp2.font.color.rgb = RGBColor(255, 255, 255)
                pp2.alignment = PP_ALIGN.CENTER
                pp2.space_after = Pt(6)

                if c_val2:
                    pp3 = ptf.add_paragraph()
                    pp3.text = c_val2
                    pp3.font.size = Pt(12)
                    pp3.font.color.rgb = theme["text_muted"]
                    pp3.alignment = PP_ALIGN.CENTER
        else:
            pillars = [
                ("Mavzu Maqsadi", "Ushbu tadqiqotda mavzuning nazariy va amaliy asoslari tizimli yoritib beriladi."),
                ("Dolzarbligi", "Zamonaviy rivojlanish bosqichida mazkur sohadagi masalalarga ilmiy yechim topish."),
                ("Kutilayotgan Natija", "Aniq tahlillar, statistik ko'rsatkichlar va amaliy tavsiyalar majmuasi.")
            ]

            for p_i, (p_title, p_body) in enumerate(pillars):
                px = p_start_x + p_i * (p_w + p_gap)

                p_card = topic_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, px, p_y, p_w, p_h)
                p_card.fill.solid()
                p_card.fill.fore_color.rgb = theme.get("card_bg", RGBColor(24, 34, 58))
                p_card.line.color.rgb = theme.get("accent", RGBColor(56, 189, 248))
                p_card.line.width = Pt(1.2)
                try:
                    p_card.adjustments[0] = 0.05
                except Exception:
                    pass

                c_bar = topic_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, px + Inches(0.25), p_y + Inches(0.12), p_w - Inches(0.5), Inches(0.04))
                c_bar.fill.solid()
                c_bar.fill.fore_color.rgb = theme["accent"]
                c_bar.line.fill.background()

                p_box = topic_slide.shapes.add_textbox(px + Inches(0.15), p_y + Inches(0.22), p_w - Inches(0.3), p_h - Inches(0.32))
                ptf = p_box.text_frame
                ptf.word_wrap = True
                pp1 = ptf.paragraphs[0]
                pp1.text = f"✦  {p_title}"
                pp1.font.size = Pt(14)
                pp1.font.bold = True
                pp1.font.color.rgb = theme["accent"]
                pp1.alignment = PP_ALIGN.CENTER
                pp1.space_after = Pt(8)

                pp2 = ptf.add_paragraph()
                pp2.text = p_body
                pp2.font.size = Pt(13)
                pp2.font.color.rgb = RGBColor(255, 255, 255)
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

        # Container card background for agenda item
        ag_card = reja_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), y, card_w, card_h)
        ag_card.fill.solid()
        ag_card.fill.fore_color.rgb = theme.get("card_bg", RGBColor(24, 34, 58))
        ag_card.line.color.rgb = theme.get("accent", RGBColor(56, 189, 248))
        ag_card.line.width = Pt(1.0)
        try:
            ag_card.adjustments[0] = 0.06
        except Exception:
            pass

        # Accent vertical left bar
        ag_bar = reja_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), y, Inches(0.08), card_h)
        ag_bar.fill.solid()
        ag_bar.fill.fore_color.rgb = theme["accent"]
        ag_bar.line.fill.background()

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

        ag_tb = reja_slide.shapes.add_textbox(Inches(2.2), y + (card_h - Inches(0.55)) / 2, Inches(9.1), Inches(0.55))
        ag_tf = ag_tb.text_frame
        ag_tf.word_wrap = True
        ag_tf.margin_top = ag_tf.margin_bottom = ag_tf.margin_left = ag_tf.margin_right = 0
        ag_p = ag_tf.paragraphs[0]
        ag_p.text = item_text
        ag_p.font.size = Pt(16.5 if n_items == 5 else 18)
        ag_p.font.bold = True
        ag_p.font.color.rgb = RGBColor(255, 255, 255)
        ag_p.font.name = "Arial"

        arr_b = reja_slide.shapes.add_textbox(Inches(11.55), y + (card_h - Inches(0.55)) / 2, Inches(0.6), Inches(0.55))
        arr_p = arr_b.text_frame.paragraphs[0]
        arr_p.text = "➔"
        arr_p.font.size = Pt(16)
        arr_p.font.bold = True
        arr_p.font.color.rgb = theme["accent"]
    return reja_slide

def _create_thanks_slide(prs, blank_layout, theme, custom_bg, is_white, is_dark, lang_info, presenter_str: str = ""):
    """Yakuniy Minnatdorchilik slaydi chizadi (daftar varog'i shaklisiz, ochiq va zamonaviy)."""
    end_slide = prs.slides.add_slide(blank_layout)
    if custom_bg and os.path.exists(custom_bg):
        end_slide.shapes.add_picture(custom_bg, 0, 0, width=Inches(13.333), height=Inches(7.5))
    else:
        bg_end = end_slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg_end.fill.solid()
        bg_end.fill.fore_color.rgb = theme["bg_slide"]
        bg_end.line.fill.background()

    end_bar = end_slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(0.35))
    end_bar.fill.solid()
    end_bar.fill.fore_color.rgb = theme["accent"]
    end_bar.line.fill.background()

    card_w = Inches(11.533)
    card_h = Inches(5.4)
    card_l = Inches(0.9)
    card_t = Inches(1.5)

    # Main container card background
    bg_end_card = end_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, card_l, card_t, card_w, card_h)
    bg_end_card.fill.solid()
    bg_end_card.fill.fore_color.rgb = theme.get("card_bg", RGBColor(24, 34, 58))
    bg_end_card.line.color.rgb = theme.get("accent", RGBColor(56, 189, 248))
    bg_end_card.line.width = Pt(1.2)
    try:
        bg_end_card.adjustments[0] = 0.04
    except Exception:
        pass

    bar_end = end_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, card_l + Inches(0.3), card_t + Inches(0.12), card_w - Inches(0.6), Inches(0.05))
    bar_end.fill.solid()
    bar_end.fill.fore_color.rgb = theme["accent"]
    bar_end.line.fill.background()

    end_box = end_slide.shapes.add_textbox(card_l, card_t + Inches(0.2), card_w, Inches(2.8))
    end_tf = end_box.text_frame
    end_tf.word_wrap = True
    end_tf.margin_top = Inches(0.1)
    end_tf.margin_bottom = Inches(0.1)
    end_tf.margin_left = Inches(0.2)
    end_tf.margin_right = Inches(0.2)

    p_badge = end_tf.paragraphs[0]
    p_badge.text = "✦  YAKUNIY MINNATDORCHILIK  ✦"
    p_badge.font.size = Pt(13)
    p_badge.font.bold = True
    p_badge.font.color.rgb = theme["accent"]
    p_badge.font.name = "Arial"
    p_badge.alignment = PP_ALIGN.CENTER
    p_badge.space_after = Pt(10)

    ep1 = end_tf.add_paragraph()
    ep1.text = lang_info["thanks"].upper()
    ep1.font.size = Pt(36)
    ep1.font.bold = True
    ep1.font.color.rgb = RGBColor(255, 255, 255)
    ep1.font.name = "Arial"
    ep1.alignment = PP_ALIGN.CENTER
    ep1.space_after = Pt(10)

    ep2 = end_tf.add_paragraph()
    ep2.text = lang_info.get("questions_welcome", "Savollar, fikr-mulohazalar va muhokama uchun tayyorman")
    ep2.font.size = Pt(16.5)
    ep2.font.bold = False
    ep2.font.color.rgb = theme["accent"]
    ep2.font.name = "Arial"
    ep2.alignment = PP_ALIGN.CENTER
    ep2.space_after = Pt(10)

    if presenter_str:
        ep3 = end_tf.add_paragraph()
        ep3.text = presenter_str
        ep3.font.size = Pt(13.5)
        ep3.font.bold = True
        ep3.font.color.rgb = RGBColor(255, 255, 255)
        ep3.font.name = "Arial"
        ep3.alignment = PP_ALIGN.CENTER

    # 3 ta yakuniy infografik blok (sahifaning pastki qismini chiroyli to'ldirish)
    t_pillars = [
        ("Savollar va Muhokama", "Taqdimot mavzusi yuzasidan fikr-mulohazalaringiz va savollaringizni mamnuniyat bilan qabul qilaman."),
        ("Ilmiy-amaliy Xulosa", "Belgilangan barcha maqsad va vazifalar to'liq yoritildi, mavzu bo'yicha asosli natijalar olindi."),
        ("Aloqa va Hamkorlik", "Tadqiqotni chuqurlashtirish, yangi loyihalarni ishlab chiqish va hamkorlik uchun doim tayyorman.")
    ]
    p_start_x = Inches(1.3)
    p_w = Inches(3.35)
    p_gap = Inches(0.35)
    p_y = Inches(4.75)
    p_h = Inches(1.8)

    for p_i, (p_title, p_body) in enumerate(t_pillars):
        px = p_start_x + p_i * (p_w + p_gap)
        p_card = end_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, px, p_y, p_w, p_h)
        p_card.fill.solid()
        p_card.fill.fore_color.rgb = theme.get("primary", RGBColor(15, 23, 42))
        p_card.line.color.rgb = theme.get("accent", RGBColor(56, 189, 248))
        p_card.line.width = Pt(1.0)
        try:
            p_card.adjustments[0] = 0.06
        except Exception:
            pass

        p_box = end_slide.shapes.add_textbox(px + Inches(0.15), p_y + Inches(0.12), p_w - Inches(0.3), p_h - Inches(0.24))
        ptf = p_box.text_frame
        ptf.word_wrap = True
        ptf.margin_top = ptf.margin_bottom = ptf.margin_left = ptf.margin_right = 0
        pp1 = ptf.paragraphs[0]
        pp1.text = f"✦  {p_title}"
        pp1.font.size = Pt(13)
        pp1.font.bold = True
        pp1.font.color.rgb = theme["accent"]
        pp1.alignment = PP_ALIGN.CENTER
        pp1.space_after = Pt(6)

        pp2 = ptf.add_paragraph()
        pp2.text = p_body
        pp2.font.size = Pt(11.5)
        pp2.font.color.rgb = RGBColor(226, 232, 240)
        pp2.alignment = PP_ALIGN.CENTER
        pp2.line_spacing = 1.15

    return end_slide

def create_pptx_file(content: dict, output_path: str, theme_name: str = "", images_map: dict = None, author_info: str = "", default_student_name: str = "", custom_bg: str = None, language: str = "", target_slide_count: int = 0) -> str:
    """Creates a beautiful 16:9 PowerPoint file with student academic structure, author info, references, and closing slides."""
    content = clean_data_structure(content)
    lang_code = language or content.get("language", "uz")
    lang_info = locales.get_slide_lang_info(lang_code)
    if not theme_name or theme_name not in THEMES:
        theme_name = content.get("theme", "blue")
    theme = THEMES.get(theme_name, THEMES["blue"])
    is_dark = True
    is_white = False
    is_mix_theme = (theme_name == "mix")

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
        student_name = (student_details.get("student") or "").strip()
        teacher_name = (student_details.get("teacher") or "").strip()
        uni_name = (student_details.get("university") or "").strip()
        faculty_name = (student_details.get("faculty") or "").strip()
        group_val = (student_details.get("group") or "").strip()
        direction_val = (student_details.get("direction") or "").strip()

        student_name = clean_prefix(student_name, ["bajardi", "talaba", "talabasi", "muallif", "tayyorladi"])
        teacher_name = clean_prefix(teacher_name, ["qabul qildi", "o'qituvchi", "oʻqituvchi", "ilmiy rahbar", "rahbar", "domla", "ustoz"])
        uni_name = clean_prefix(uni_name, ["otm", "universitet", "institut"])
        faculty_name = clean_prefix(faculty_name, ["fakultet", "fakulteti"])
        group_val = clean_prefix(group_val, ["guruh", "guruhi", "kurs", "kursi"])
        direction_val = clean_prefix(direction_val, ["yo'nalish", "yoʻnalishi"])

        if not student_name and default_student_name:
            student_name = default_student_name

        student_details["student"] = student_name
        student_details["teacher"] = teacher_name
        student_details["university"] = uni_name
        student_details["faculty"] = faculty_name
        student_details["group"] = group_val
        student_details["direction"] = direction_val
    else:
        student_details = {}

    # ================= 1. TITUL SLAYD (ZAMONAVIY 16:9 HERO MASTER SLIDE) =================
    # Qat'iy talab: Daftar varog'i, referat nusxasi yoki vazirlik qog'oz shakli UMUMAN chiqmaydi.
    # Barcha mavzu va fonlarda 1-slayd xalqaro konferensiya va Gamma AI uslubidagi yuksak dizaynda chiqadi.
    _create_hero_slide(
        prs,
        blank_layout,
        theme,
        title_text,
        subtitle_text,
        total_slides,
        is_dark,
        custom_bg,
        images_map,
        lang_info,
        author_details=student_details if has_author else None
    )

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
        if "Русский" in lang_name:
            p_pts = [
                "Теоретические основы: Углубленный анализ фундаментальных концепций и ключевых закономерностей предметной области.",
                "Механизмы реализации: Практические инструменты, протоколы и алгоритмы эффективного внедрения в реальные процессы.",
                "Оценка эффективности: Качественные и количественные показатели результативности, системный анализ преимуществ.",
                "Современные технологии: Использование передовых цифровых инструментов, автоматизации и инновационных решений.",
                "Перспективы развития: Стратегические направления масштабирования, оптимизации и интеграции на долгосрочный период."
            ]
        elif "English" in lang_name:
            p_pts = [
                "Theoretical Foundation: In-depth analysis of core principles, methodologies, and technical frameworks.",
                "Implementation Architecture: Practical deployment workflows, protocols, and standard operational processes.",
                "Performance Evaluation: Quantitative and qualitative benchmarking of key system metrics and strategic value.",
                "Modern Technologies: Leveraging state-of-the-art tools, automation, and intelligent infrastructure.",
                "Future Roadmap: Emerging trends, scalability considerations, and sustainable long-term development."
            ]
        else:
            p_pts = [
                "Nazariy asoslar: Sohaning fundamental ilmiy tushunchalari, tamoyillari va asosiy qonuniyatlari chuqur tahlili.",
                "Amaliy mexanizmlar: Tizimni real jarayonlarga tatbiq etish usullari, standartlari va operatsion yechimlari.",
                "Samaradorlik mezonlari: Aniq ko'rsatkichlar, natijadorlik tahlili va tizimli afzalliklarni empirik baholash.",
                "Zamonaviy texnologiyalar: Ilg'or axborot texnologiyalari, raqamlashtirish va innovatsion vositalarni qo'llash.",
                "Istiqbolli yo'nalishlar: Sohani modernizatsiya qilish, xavfsizlikni kuchaytirish va kelajakdagi rivojlanish omillari."
            ]
        slides_data.append({
            "title": p_title,
            "bullet_points": p_pts,
            "layout": "standard"
        })

    # ================= 3. ASOSIY MAZMUN SLAYDLARI =================
    ppt_mix_sequence = ["office", "facet", "slice", "integral", "droplet", "ion", "circuit", "celestial", "savon", "retrospect"]
    for idx, s_data in enumerate(slides_data, 1):
        if is_mix_theme:
            cur_key = ppt_mix_sequence[(idx - 1) % len(ppt_mix_sequence)]
            curr_theme = THEMES.get(cur_key, theme)
            curr_is_dark = True
        else:
            curr_theme = theme
            curr_is_dark = True

        c_slide = prs.slides.add_slide(blank_layout)
        if custom_bg and os.path.exists(custom_bg):
            c_slide.shapes.add_picture(custom_bg, 0, 0, width=Inches(13.333), height=Inches(7.5))
        else:
            bg_c = c_slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
            bg_c.fill.solid()
            bg_c.fill.fore_color.rgb = curr_theme["bg_slide"]
            bg_c.line.fill.background()

        s_title = s_data.get("title", f"Boʻlim {idx}")
        content_slide_num = len(prs.slides)
        sec_lbl = lang_info.get("section_label", "BOʻLIM")
        reja_lbl = lang_info.get("agenda", "Reja").upper()

        # Har bir slayd qaysi reja bandiga tegishli ekanligini aniq aytib ketish
        ag_list = content.get("agenda") or []
        ag_num = s_data.get("agenda_num")
        if not ag_num or not isinstance(ag_num, int) or ag_num < 1:
            if ag_list and len(slides_data) <= len(ag_list):
                ag_num = idx
            elif ag_list:
                ag_num = min(len(ag_list), max(1, int((idx - 1) * len(ag_list) / len(slides_data)) + 1))
            else:
                ag_num = idx

        ag_title = str(s_data.get("agenda_title") or "").strip()
        if (not ag_title or ag_title.lower().startswith("reja")) and ag_list and 0 < ag_num <= len(ag_list):
            ag_title = ag_list[ag_num - 1]

        if ag_list and 0 < ag_num <= len(ag_list):
            reja_category = f"{reja_lbl} {ag_num}/{len(ag_list)}: {ag_title[:45]}"
        elif ag_list:
            reja_category = f"{reja_lbl} {ag_num}: {ag_title[:45]}"
        else:
            reja_category = f"{sec_lbl} {idx}"

        _add_header(c_slide, s_title, curr_theme, slide_num=content_slide_num, total_slides=total_slides, category=reja_category)

        img_path = images_map.get(idx) if images_map else None
        bullets = s_data.get("bullet_points") or s_data.get("bullets", [])
        layout_type = str(s_data.get("layout", "standard")).lower().strip()
        kpi_items = s_data.get("kpi_items", [])
        comparison_data = s_data.get("comparison_data", {})
        steps_data = s_data.get("steps_data", [])

        if layout_type == "kpi" and isinstance(kpi_items, list) and len(kpi_items) >= 2:
            # 3 ta KPI karta (yuqoridan pastgacha to'liq to'ldirilgan va teng taqsimlangan)
            items = list(kpi_items[:3])
            while len(items) < 3:
                k_pad_idx = len(items) + 1
                items.append({
                    "number": "100%" if k_pad_idx == 3 else "2.5x",
                    "label": f"Tizimli mezon {k_pad_idx}",
                    "desc": f"{s_title}: Mazkur ko'rsatkich sohadagi asosiy texnologik parametrlar va innovatsion samaradorlik mezonlarining to'liq ta'minlanishini aks ettiradi.",
                    "points": [
                        "Standart mezonlari: Xalqaro va milliy talablarga to'liq muvofiqlik tahlili",
                        "Amaliy natija: Real jarayonlarda yuqori ishonchlilik va samaradorlik kafolati"
                    ]
                })
            card_w = Inches(3.6)
            card_h = Inches(5.35)
            gap = Inches(0.366)
            start_x = Inches(0.9)
            y_pos = Inches(1.55)

            for k_idx, item in enumerate(items):
                x_pos = start_x + k_idx * (card_w + gap)

                # Modern glassmorphism card container
                bg_card = c_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x_pos, y_pos, card_w, card_h)
                bg_card.fill.solid()
                bg_card.fill.fore_color.rgb = curr_theme.get("card_bg", RGBColor(24, 34, 58))
                bg_card.line.color.rgb = curr_theme.get("accent", RGBColor(56, 189, 248))
                bg_card.line.width = Pt(1.2)
                try:
                    bg_card.adjustments[0] = 0.05
                except Exception:
                    pass

                # Top color accent bar
                c_bar = c_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x_pos + Inches(0.2), y_pos + Inches(0.1), card_w - Inches(0.4), Inches(0.05))
                c_bar.fill.solid()
                c_bar.fill.fore_color.rgb = curr_theme["accent"]
                c_bar.line.fill.background()

                # Big Number Textbox
                num_box = c_slide.shapes.add_textbox(x_pos + Inches(0.15), y_pos + Inches(0.15), card_w - Inches(0.3), Inches(0.95))
                ntf = num_box.text_frame
                ntf.word_wrap = True
                ntf.margin_top = ntf.margin_bottom = ntf.margin_left = ntf.margin_right = 0
                np = ntf.paragraphs[0]
                raw_num = str(item.get("number", f"#{k_idx+1}"))
                np.text = remove_emojis(raw_num)
                np.font.size = Pt(36)
                np.font.bold = True
                np.font.color.rgb = curr_theme["accent"]
                np.font.name = "Arial"
                np.alignment = PP_ALIGN.CENTER

                # Label Textbox
                lbl_box = c_slide.shapes.add_textbox(x_pos + Inches(0.15), y_pos + Inches(1.05), card_w - Inches(0.3), Inches(0.65))
                ltf = lbl_box.text_frame
                ltf.word_wrap = True
                ltf.margin_top = ltf.margin_bottom = ltf.margin_left = ltf.margin_right = 0
                lp = ltf.paragraphs[0]
                raw_lbl = str(item.get("label", ""))
                lp.text = remove_emojis(raw_lbl)
                lp.font.size = Pt(16)
                lp.font.bold = True
                lp.font.color.rgb = RGBColor(255, 255, 255)
                lp.font.name = "Arial"
                lp.alignment = PP_ALIGN.CENTER

                # Divider line
                div = c_slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x_pos + Inches(0.3), y_pos + Inches(1.75), card_w - Inches(0.6), Inches(0.02))
                div.fill.solid()
                div.fill.fore_color.rgb = curr_theme.get("card_border", curr_theme["accent"])
                div.line.fill.background()

                # Content Box: Desc & Sub-points (to'liq to'ldirish)
                desc_box = c_slide.shapes.add_textbox(x_pos + Inches(0.2), y_pos + Inches(1.85), card_w - Inches(0.4), card_h - Inches(1.95))
                dtf = desc_box.text_frame
                dtf.word_wrap = True
                dtf.margin_top = dtf.margin_bottom = dtf.margin_left = dtf.margin_right = 0

                desc_text = str(item.get("desc", "")).strip()
                if not desc_text and k_idx < len(bullets):
                    desc_text = re.sub(r"^[\s•\-\*–—\d\.\)]+", "", remove_emojis(str(bullets[k_idx]))).strip()
                if not desc_text:
                    desc_text = f"{raw_lbl}: Mavzu doirasida mazkur ko'rsatkich tizimning asosiy samaradorlik omili va mezoniy ko'rsatkichi hisoblanadi."

                dp = dtf.paragraphs[0]
                dp.text = remove_emojis(desc_text)
                dp.font.size = Pt(12.5)
                dp.font.color.rgb = RGBColor(226, 232, 240)
                dp.font.name = "Arial"
                dp.space_after = Pt(8)
                dp.line_spacing = 1.15

                # Additional Points in KPI Card
                kpi_pts = item.get("points") or []
                if not kpi_pts:
                    rem_bullets = [b for b_i, b in enumerate(bullets) if b_i != k_idx]
                    if rem_bullets:
                        kpi_pts = rem_bullets[k_idx * 2 : k_idx * 2 + 2] or rem_bullets[:2]

                for pt in kpi_pts[:2]:
                    pt_clean = re.sub(r"^[\s•\-\*–—\d\.\)]+", "", remove_emojis(str(pt))).strip()
                    if pt_clean:
                        _add_styled_bullet(dtf, pt_clean, curr_theme, font_size=Pt(11.5), space_after=Pt(6))

        elif layout_type == "comparison" and isinstance(comparison_data, dict) and (comparison_data.get("col1_points") or comparison_data.get("col1_title")):
            col1_title = comparison_data.get("col1_title", "1-yondashuv")
            col1_pts = list(comparison_data.get("col1_points", []))
            col2_title = comparison_data.get("col2_title", "2-yondashuv")
            col2_pts = list(comparison_data.get("col2_points", []))

            # Ikkala ustun bir xil teng va mukammal to'liq bo'lishini ta'minlash (kamida 4-5 ta band)
            target_pts = max(4, min(5, max(len(col1_pts), len(col2_pts))))
            while len(col1_pts) < target_pts:
                p_pad = len(col1_pts) + 1
                col1_pts.append(f"Tahliliy mezon {p_pad}: Mazkur tizimning asosiy parametrlari, operatsion xususiyatlari va amaliy samaradorligi chuqur o'rganilgan.")
            while len(col2_pts) < target_pts:
                p_pad = len(col2_pts) + 1
                col2_pts.append(f"Qiyosiy ko'rsatkich {p_pad}: Yangi innovatsion yondashuvning texnologik afzalliklari, tezkorligi va xavfsizlik kafolatlari tahlili.")

            card_w = Inches(5.4)
            card_h = Inches(5.35)
            y_pos = Inches(1.55)

            # Left Column Card Background
            bg_l = c_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), y_pos, card_w, card_h)
            bg_l.fill.solid()
            bg_l.fill.fore_color.rgb = curr_theme.get("card_bg", RGBColor(24, 34, 58))
            bg_l.line.color.rgb = curr_theme.get("accent", RGBColor(56, 189, 248))
            bg_l.line.width = Pt(1.2)
            try:
                bg_l.adjustments[0] = 0.04
            except Exception:
                pass

            bar_l = c_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9) + Inches(0.3), y_pos + Inches(0.12), card_w - Inches(0.6), Inches(0.05))
            bar_l.fill.solid()
            bar_l.fill.fore_color.rgb = curr_theme["accent"]
            bar_l.line.fill.background()

            lt_box = c_slide.shapes.add_textbox(Inches(1.2), y_pos + Inches(0.28), card_w - Inches(0.6), Inches(0.55))
            ltf = lt_box.text_frame
            ltf.word_wrap = True
            ltf.margin_top = ltf.margin_bottom = ltf.margin_left = ltf.margin_right = 0
            lp = ltf.paragraphs[0]
            lp.text = remove_emojis(col1_title)
            lp.font.size = Pt(18)
            lp.font.bold = True
            lp.font.color.rgb = curr_theme["accent"]
            lp.font.name = "Arial"

            div_l = c_slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.2), y_pos + Inches(0.88), card_w - Inches(0.6), Inches(0.02))
            div_l.fill.solid()
            div_l.fill.fore_color.rgb = curr_theme.get("card_border", curr_theme["accent"])
            div_l.line.fill.background()

            lb_box = c_slide.shapes.add_textbox(Inches(1.2), y_pos + Inches(0.98), card_w - Inches(0.6), card_h - Inches(1.15))
            lbtf = lb_box.text_frame
            lbtf.word_wrap = True
            lbtf.margin_top = lbtf.margin_bottom = lbtf.margin_left = lbtf.margin_right = 0
            for p_idx, pt in enumerate(col1_pts[:5]):
                _add_styled_bullet(lbtf, str(pt), curr_theme, font_size=Pt(13), space_after=Pt(8), is_first=(p_idx == 0))

            # Right Column Card Background
            x_r = Inches(7.033)
            bg_r = c_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x_r, y_pos, card_w, card_h)
            bg_r.fill.solid()
            bg_r.fill.fore_color.rgb = curr_theme.get("card_bg", RGBColor(24, 34, 58))
            bg_r.line.color.rgb = curr_theme.get("accent", RGBColor(56, 189, 248))
            bg_r.line.width = Pt(1.2)
            try:
                bg_r.adjustments[0] = 0.04
            except Exception:
                pass

            bar_r = c_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x_r + Inches(0.3), y_pos + Inches(0.12), card_w - Inches(0.6), Inches(0.05))
            bar_r.fill.solid()
            bar_r.fill.fore_color.rgb = curr_theme["accent"]
            bar_r.line.fill.background()

            rt_box = c_slide.shapes.add_textbox(x_r + Inches(0.3), y_pos + Inches(0.28), card_w - Inches(0.6), Inches(0.55))
            rtf = rt_box.text_frame
            rtf.word_wrap = True
            rtf.margin_top = rtf.margin_bottom = rtf.margin_left = rtf.margin_right = 0
            rp = rtf.paragraphs[0]
            rp.text = remove_emojis(col2_title)
            rp.font.size = Pt(18)
            rp.font.bold = True
            rp.font.color.rgb = curr_theme["accent"]
            rp.font.name = "Arial"

            div_r = c_slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x_r + Inches(0.3), y_pos + Inches(0.88), card_w - Inches(0.6), Inches(0.02))
            div_r.fill.solid()
            div_r.fill.fore_color.rgb = curr_theme.get("card_border", curr_theme["accent"])
            div_r.line.fill.background()

            rb_box = c_slide.shapes.add_textbox(x_r + Inches(0.3), y_pos + Inches(0.98), card_w - Inches(0.6), card_h - Inches(1.15))
            rbtf = rb_box.text_frame
            rbtf.word_wrap = True
            rbtf.margin_top = rbtf.margin_bottom = rbtf.margin_left = rbtf.margin_right = 0
            for p_idx, pt in enumerate(col2_pts[:5]):
                _add_styled_bullet(rbtf, str(pt), curr_theme, font_size=Pt(13), space_after=Pt(8), is_first=(p_idx == 0))

            # Central VS Badge
            vs_badge = c_slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(6.25), y_pos + Inches(2.2), Inches(0.8), Inches(0.8))
            vs_badge.fill.solid()
            vs_badge.fill.fore_color.rgb = curr_theme["accent"]
            vs_badge.line.fill.background()
            vs_tf = vs_badge.text_frame
            vsp = vs_tf.paragraphs[0]
            vsp.text = "VS"
            vsp.font.size = Pt(14)
            vsp.font.bold = True
            vsp.font.color.rgb = RGBColor(255, 255, 255)
            vsp.alignment = PP_ALIGN.CENTER

        elif layout_type == "steps" and isinstance(steps_data, list) and len(steps_data) >= 2:
            s_items = list(steps_data[:3])
            while len(s_items) < 3:
                st_pad_idx = len(s_items) + 1
                s_items.append({
                    "step": f"0{st_pad_idx}",
                    "title": f"{st_pad_idx}-bosqich: Monitoring va optimallashtirish",
                    "desc": f"Jarayonlarni bosqichma-bosqich tatbiq etish, samaradorlik ko'rsatkichlarini doimiy tahlil qilish va yangi standartlar asosida takomillashtirish mexanizmi.",
                    "points": [
                        "Texnik nazorat: Tizimning barqaror ishlashi va sifat parametrlari tahlili",
                        "Innovatsion rivoj: Yangi texnologik vositalar orqali tizimni modernizatsiya qilish"
                    ]
                })
            card_w = Inches(3.6)
            card_h = Inches(5.35)
            gap = Inches(0.366)
            start_x = Inches(0.9)
            y_pos = Inches(1.55)

            for st_idx, st in enumerate(s_items):
                x_pos = start_x + st_idx * (card_w + gap)

                # Modern glassmorphism card container
                bg_card = c_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x_pos, y_pos, card_w, card_h)
                bg_card.fill.solid()
                bg_card.fill.fore_color.rgb = curr_theme.get("card_bg", RGBColor(24, 34, 58))
                bg_card.line.color.rgb = curr_theme.get("accent", RGBColor(56, 189, 248))
                bg_card.line.width = Pt(1.2)
                try:
                    bg_card.adjustments[0] = 0.05
                except Exception:
                    pass

                # Top color accent bar
                c_bar = c_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x_pos + Inches(0.2), y_pos + Inches(0.1), card_w - Inches(0.4), Inches(0.05))
                c_bar.fill.solid()
                c_bar.fill.fore_color.rgb = curr_theme["accent"]
                c_bar.line.fill.background()

                # Step Number Pill
                circ = c_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x_pos + Inches(0.25), y_pos + Inches(0.22), Inches(0.9), Inches(0.42))
                circ.fill.solid()
                circ.fill.fore_color.rgb = curr_theme["accent"]
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
                st_title_box = c_slide.shapes.add_textbox(x_pos + Inches(0.25), y_pos + Inches(0.72), card_w - Inches(0.5), Inches(0.72))
                st_tf = st_title_box.text_frame
                st_tf.word_wrap = True
                st_tf.margin_top = st_tf.margin_bottom = st_tf.margin_left = st_tf.margin_right = 0
                tp = st_tf.paragraphs[0]
                tp.text = remove_emojis(str(st.get("title", "")))
                tp.font.size = Pt(16.5)
                tp.font.bold = True
                tp.font.color.rgb = RGBColor(255, 255, 255)
                tp.font.name = "Arial"

                # Divider line
                div = c_slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x_pos + Inches(0.25), y_pos + Inches(1.5), card_w - Inches(0.5), Inches(0.02))
                div.fill.solid()
                div.fill.fore_color.rgb = curr_theme.get("card_border", curr_theme["accent"])
                div.line.fill.background()

                # Content Box: Desc & Sub-points (to'liq to'ldirish)
                desc_box = c_slide.shapes.add_textbox(x_pos + Inches(0.25), y_pos + Inches(1.6), card_w - Inches(0.5), card_h - Inches(1.72))
                dtf = desc_box.text_frame
                dtf.word_wrap = True
                dtf.margin_top = dtf.margin_bottom = dtf.margin_left = dtf.margin_right = 0

                desc_text = str(st.get("desc", "")).strip()
                if not desc_text and st_idx < len(bullets):
                    desc_text = re.sub(r"^[\s•\-\*–—\d\.\)]+", "", remove_emojis(str(bullets[st_idx]))).strip()
                if not desc_text:
                    desc_text = f"{st.get('title', 'Bosqich')}: Mazkur yo'nalish bo'yicha asosiy mexanizmlar va texnik tamoyillar tizimli tatbiq etiladi."

                dp = dtf.paragraphs[0]
                dp.text = remove_emojis(desc_text)
                dp.font.size = Pt(12.5)
                dp.font.color.rgb = RGBColor(226, 232, 240)
                dp.font.name = "Arial"
                dp.space_after = Pt(8)
                dp.line_spacing = 1.15

                # Additional Points in Step Card
                st_pts = st.get("points") or []
                if not st_pts:
                    rem_bullets = [b for b_i, b in enumerate(bullets) if b_i != st_idx]
                    if rem_bullets:
                        st_pts = rem_bullets[st_idx * 2 : st_idx * 2 + 2] or rem_bullets[:2]

                for pt in st_pts[:2]:
                    pt_clean = re.sub(r"^[\s•\-\*–—\d\.\)]+", "", remove_emojis(str(pt))).strip()
                    if pt_clean:
                        _add_styled_bullet(dtf, pt_clean, curr_theme, font_size=Pt(11.5), space_after=Pt(6))

        elif img_path and os.path.exists(img_path):
            box_w = Inches(7.0)
            box_h = Inches(5.4)

            # Left Card Container for content
            bg_content = c_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), Inches(1.5), box_w, box_h)
            bg_content.fill.solid()
            bg_content.fill.fore_color.rgb = curr_theme.get("card_bg", RGBColor(24, 34, 58))
            bg_content.line.color.rgb = curr_theme.get("accent", RGBColor(56, 189, 248))
            bg_content.line.width = Pt(1.2)
            try:
                bg_content.adjustments[0] = 0.04
            except Exception:
                pass

            bar_l = c_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9) + Inches(0.3), Inches(1.5) + Inches(0.12), box_w - Inches(0.6), Inches(0.05))
            bar_l.fill.solid()
            bar_l.fill.fore_color.rgb = curr_theme["accent"]
            bar_l.line.fill.background()

            content_box = c_slide.shapes.add_textbox(Inches(1.2), Inches(1.75), box_w - Inches(0.6), box_h - Inches(0.45))
            ctf = content_box.text_frame
            ctf.word_wrap = True
            ctf.margin_top = ctf.margin_bottom = ctf.margin_left = ctf.margin_right = 0

            # Kamida 5-6 ta sifatli band bilan butun maydonni to'liq to'ldirish
            render_bullets = list(bullets)
            while len(render_bullets) < 5:
                render_bullets.append(f"Qo'shimcha tahlil {len(render_bullets)+1}: {s_title} mavzusining amaliy samaradorligi va xavfsizlik standartlari chuqur o'rganilgan.")

            n_b = len(render_bullets)
            font_sz = Pt(13 if n_b >= 6 else (14 if n_b == 5 else 15))
            space_aft = Pt(8 if n_b >= 6 else (10 if n_b == 5 else 14))

            for b_idx, bullet in enumerate(render_bullets[:6]):
                _add_styled_bullet(ctf, bullet, curr_theme, font_size=font_sz, space_after=space_aft, is_first=(b_idx == 0))

            try:
                img_x = Inches(8.15)
                img_w = Inches(4.28)
                img_h = Inches(5.4)
                img_frame = c_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, img_x, Inches(1.5), img_w, img_h)
                img_frame.fill.solid()
                img_frame.fill.fore_color.rgb = curr_theme.get("card_bg", RGBColor(24, 34, 58))
                img_frame.line.color.rgb = curr_theme.get("accent", RGBColor(56, 189, 248))
                img_frame.line.width = Pt(1.2)
                try:
                    img_frame.adjustments[0] = 0.04
                except Exception:
                    pass
                c_slide.shapes.add_picture(img_path, img_x, Inches(1.5), width=img_w, height=img_h)
            except Exception:
                pass
        else:
            box_w = Inches(11.533)
            box_h = Inches(5.4)

            # Full width content card container
            bg_content = c_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), Inches(1.5), box_w, box_h)
            bg_content.fill.solid()
            bg_content.fill.fore_color.rgb = curr_theme.get("card_bg", RGBColor(24, 34, 58))
            bg_content.line.color.rgb = curr_theme.get("accent", RGBColor(56, 189, 248))
            bg_content.line.width = Pt(1.2)
            try:
                bg_content.adjustments[0] = 0.04
            except Exception:
                pass

            bar_l = c_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9) + Inches(0.3), Inches(1.5) + Inches(0.12), box_w - Inches(0.6), Inches(0.05))
            bar_l.fill.solid()
            bar_l.fill.fore_color.rgb = curr_theme["accent"]
            bar_l.line.fill.background()

            content_box = c_slide.shapes.add_textbox(Inches(1.25), Inches(1.75), box_w - Inches(0.7), box_h - Inches(0.45))
            ctf = content_box.text_frame
            ctf.word_wrap = True
            ctf.margin_top = ctf.margin_bottom = ctf.margin_left = ctf.margin_right = 0

            render_bullets = list(bullets)
            while len(render_bullets) < 5:
                render_bullets.append(f"Qo'shimcha tahlil {len(render_bullets)+1}: {s_title} mavzusining ilmiy-amaliy mohiyati, mezonlari va texnologik istiqbollari chuqur tahlil qilingan.")

            n_b = len(render_bullets)
            font_sz = Pt(14 if n_b >= 6 else (15 if n_b == 5 else 16.5))
            space_aft = Pt(10 if n_b >= 6 else (12 if n_b == 5 else 18))

            for b_idx, bullet in enumerate(render_bullets[:6]):
                _add_styled_bullet(ctf, bullet, curr_theme, font_size=font_sz, space_after=space_aft, is_first=(b_idx == 0))

        # Speaker notes matni alohida doklad fayli sifatida yuboriladi,
        # PPTX slaydlariga ortiqcha daftardek qog'oz varog'i qo'shilmaydi.

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

        # Top Box Card Container: Xulosa
        top_card = end_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), Inches(1.5), Inches(11.533), Inches(2.7))
        top_card.fill.solid()
        top_card.fill.fore_color.rgb = theme.get("card_bg", RGBColor(24, 34, 58))
        top_card.line.color.rgb = theme.get("accent", RGBColor(56, 189, 248))
        top_card.line.width = Pt(1.2)
        try:
            top_card.adjustments[0] = 0.04
        except Exception:
            pass

        top_bar = end_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9) + Inches(0.3), Inches(1.5) + Inches(0.12), Inches(11.533) - Inches(0.6), Inches(0.05))
        top_bar.fill.solid()
        top_bar.fill.fore_color.rgb = theme["accent"]
        top_bar.line.fill.background()

        t_box = end_slide.shapes.add_textbox(Inches(1.15), Inches(1.68), Inches(11.0), Inches(2.4))
        t_tf = t_box.text_frame
        t_tf.word_wrap = True
        t_tf.margin_top = t_tf.margin_bottom = t_tf.margin_left = t_tf.margin_right = 0
        p_ch = t_tf.paragraphs[0]
        p_ch.text = lang_info.get("main_conclusions", "✦  ASOSIY ILMIY-AMALIY XULOSALAR")
        p_ch.font.size = Pt(15)
        p_ch.font.bold = True
        p_ch.font.color.rgb = theme["accent"]
        p_ch.space_after = Pt(6)

        points = conclusion_points[:3] if conclusion_points else [
            "Nazariy xulosa: Mavzu bo'yicha belgilangan barcha fundamental tushunchalar va ilmiy vazifalar to'liq yoritildi.",
            "Amaliy natija: Olingan xulosalar va texnik ko'rsatkichlar tizim samaradorligini oshirish uchun amaliy ahamiyatga ega.",
            "Istiqbol: Sohadagi ilg'or tendensiyalar va xavfsizlik standartlarini tatbiq etish bo'yicha tavsiyalar ishlab chiqildi."
        ]
        for pt in points:
            _add_styled_bullet(t_tf, pt, theme, font_size=Pt(13), space_after=Pt(5))

        # Bottom Box Card Container: E'tiboringiz uchun rahmat
        bot_card = end_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), Inches(4.35), Inches(11.533), Inches(2.6))
        bot_card.fill.solid()
        bot_card.fill.fore_color.rgb = theme.get("card_bg", RGBColor(24, 34, 58))
        bot_card.line.color.rgb = theme.get("accent", RGBColor(56, 189, 248))
        bot_card.line.width = Pt(1.2)
        try:
            bot_card.adjustments[0] = 0.04
        except Exception:
            pass

        bot_bar = end_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9) + Inches(0.3), Inches(4.35) + Inches(0.12), Inches(11.533) - Inches(0.6), Inches(0.05))
        bot_bar.fill.solid()
        bot_bar.fill.fore_color.rgb = theme["accent"]
        bot_bar.line.fill.background()

        b_box = end_slide.shapes.add_textbox(Inches(1.15), Inches(4.5), Inches(11.0), Inches(2.3))
        b_tf = b_box.text_frame
        b_tf.word_wrap = True
        b_tf.margin_top = b_tf.margin_bottom = b_tf.margin_left = b_tf.margin_right = 0
        bp1 = b_tf.paragraphs[0]
        bp1.text = lang_info["thanks"].upper()
        bp1.font.size = Pt(28)
        bp1.font.bold = True
        bp1.font.color.rgb = RGBColor(255, 255, 255)
        bp1.alignment = PP_ALIGN.CENTER
        bp1.space_before = Pt(4)
        bp1.space_after = Pt(6)

        bp2 = b_tf.add_paragraph()
        bp2.text = lang_info.get("questions_welcome", "Savollar, fikr-mulohazalar va muhokama uchun tayyorman")
        bp2.font.size = Pt(14.5)
        bp2.font.color.rgb = theme["accent"]
        bp2.alignment = PP_ALIGN.CENTER
        bp2.space_after = Pt(6)

        if presenter_str:
            bp3 = b_tf.add_paragraph()
            bp3.text = presenter_str
            bp3.font.size = Pt(13)
            bp3.font.bold = True
            bp3.font.color.rgb = RGBColor(255, 255, 255)
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

        card_h = Inches(5.4)

        # Left Column: Xulosa Card
        bg_cl = concl_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), Inches(1.5), Inches(5.6), card_h)
        bg_cl.fill.solid()
        bg_cl.fill.fore_color.rgb = theme.get("card_bg", RGBColor(24, 34, 58))
        bg_cl.line.color.rgb = theme.get("accent", RGBColor(56, 189, 248))
        bg_cl.line.width = Pt(1.2)
        try:
            bg_cl.adjustments[0] = 0.04
        except Exception:
            pass

        bar_cl = concl_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9) + Inches(0.3), Inches(1.5) + Inches(0.12), Inches(5.6) - Inches(0.6), Inches(0.05))
        bar_cl.fill.solid()
        bar_cl.fill.fore_color.rgb = theme["accent"]
        bar_cl.line.fill.background()

        cl_box = concl_slide.shapes.add_textbox(Inches(1.2), Inches(1.75), Inches(5.0), card_h - Inches(0.45))
        cl_tf = cl_box.text_frame
        cl_tf.word_wrap = True
        cl_tf.margin_top = cl_tf.margin_bottom = cl_tf.margin_left = cl_tf.margin_right = 0
        p_lh = cl_tf.paragraphs[0]
        p_lh.text = lang_info.get("main_conclusions", "✦  ASOSIY XULOSALAR")
        p_lh.font.size = Pt(16)
        p_lh.font.bold = True
        p_lh.font.color.rgb = theme["accent"]
        p_lh.space_after = Pt(10)

        points = conclusion_points[:4] if conclusion_points else [
            "Mavzu bo'yicha belgilangan barcha fundamental va amaliy vazifalar to'liq yoritildi.",
            "Olingan natijalar sohaning nazariy va amaliy rivojlanishi uchun muhim ahamiyat kasb etadi.",
            "Tadqiqot natijasida amaliyotga tatbiq qilish mumkin bo'lgan aniq tavsiyalar shakllantirildi.",
            "Zamonaviy texnologiyalar va ilg'or tajribalar asosida tizimni takomillashtirish imkoniyati yaratildi."
        ]
        for pt in points:
            _add_styled_bullet(cl_tf, pt, theme, font_size=Pt(13), space_after=Pt(8))

        # Right Column: Adabiyotlar Card
        bg_cr = concl_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.5), Inches(5.6), card_h)
        bg_cr.fill.solid()
        bg_cr.fill.fore_color.rgb = theme.get("card_bg", RGBColor(24, 34, 58))
        bg_cr.line.color.rgb = theme.get("accent", RGBColor(56, 189, 248))
        bg_cr.line.width = Pt(1.2)
        try:
            bg_cr.adjustments[0] = 0.04
        except Exception:
            pass

        bar_cr = concl_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8) + Inches(0.3), Inches(1.5) + Inches(0.12), Inches(5.6) - Inches(0.6), Inches(0.05))
        bar_cr.fill.solid()
        bar_cr.fill.fore_color.rgb = theme["accent"]
        bar_cr.line.fill.background()

        cr_box = concl_slide.shapes.add_textbox(Inches(7.1), Inches(1.75), Inches(5.0), card_h - Inches(0.45))
        cr_tf = cr_box.text_frame
        cr_tf.word_wrap = True
        cr_tf.margin_top = cr_tf.margin_bottom = cr_tf.margin_left = cr_tf.margin_right = 0
        p_rh = cr_tf.paragraphs[0]
        p_rh.text = f"✦  {lang_info.get('references', 'FOYDALANILGAN MANBALAR').upper()}"
        p_rh.font.size = Pt(16)
        p_rh.font.bold = True
        p_rh.font.color.rgb = theme["accent"]
        p_rh.space_after = Pt(10)

        for r_idx, ref_text in enumerate(clean_refs[:4], 1):
            p = cr_tf.add_paragraph()
            t_cleaned = re.sub(r"^[\d\.\)\-\s•]+", "", remove_emojis(str(ref_text))).strip()
            p.text = f"{r_idx}.  {t_cleaned}"
            p.font.size = Pt(12.5)
            p.font.color.rgb = RGBColor(255, 255, 255)
            p.font.name = "Arial"
            p.space_after = Pt(8)

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

        card_w = Inches(11.533)
        card_h = Inches(5.4)

        bg_concl_card = concl_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), Inches(1.5), card_w, card_h)
        bg_concl_card.fill.solid()
        bg_concl_card.fill.fore_color.rgb = theme.get("card_bg", RGBColor(24, 34, 58))
        bg_concl_card.line.color.rgb = theme.get("accent", RGBColor(56, 189, 248))
        bg_concl_card.line.width = Pt(1.2)
        try:
            bg_concl_card.adjustments[0] = 0.04
        except Exception:
            pass

        bar_concl = concl_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9) + Inches(0.3), Inches(1.5) + Inches(0.12), card_w - Inches(0.6), Inches(0.05))
        bar_concl.fill.solid()
        bar_concl.fill.fore_color.rgb = theme["accent"]
        bar_concl.line.fill.background()

        concl_box = concl_slide.shapes.add_textbox(Inches(1.25), Inches(1.75), card_w - Inches(0.7), card_h - Inches(0.45))
        concl_tf = concl_box.text_frame
        concl_tf.word_wrap = True
        concl_tf.margin_top = concl_tf.margin_bottom = concl_tf.margin_left = concl_tf.margin_right = 0

        c_points = list(conclusion_points) if conclusion_points else [
            "Nazariy xulosa: Mavzuning konseptual va fundamental qonuniyatlari to'liq ilmiy asoslab berildi.",
            "Tahlillar natijasi: Sohadagi mavjud holat, tizimli parametrlar va samaradorlik mezonlari chuqur o'rganildi.",
            "Amaliyotga tatbiq: Real tizimlarda qo'llash va operatsion samaradorlikni oshirish imkoniyatlari aniqlandi.",
            "Kelajak istiqbollari: Sohaning uzoq muddatli barqaror rivojlanishi va modernizatsiyasi bo'yicha tavsiyalar berildi."
        ]
        while len(c_points) < 4:
            c_points.append(f"Qo'shimcha ilmiy xulosa: {title_text} sohasidagi zamonaviy standartlar va amaliy tadqiqotlar tahlili yakunlandi.")

        n_c = len(c_points)
        font_sz = Pt(14 if n_c >= 5 else 15.5)
        space_aft = Pt(10 if n_c >= 5 else 14)

        for c_idx, point in enumerate(c_points[:5]):
            _add_styled_bullet(concl_tf, point, theme, font_size=font_sz, space_after=space_aft, is_first=(c_idx == 0))

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

        bg_ref_card = ref_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), Inches(1.5), card_w, card_h)
        bg_ref_card.fill.solid()
        bg_ref_card.fill.fore_color.rgb = theme.get("card_bg", RGBColor(24, 34, 58))
        bg_ref_card.line.color.rgb = theme.get("accent", RGBColor(56, 189, 248))
        bg_ref_card.line.width = Pt(1.2)
        try:
            bg_ref_card.adjustments[0] = 0.04
        except Exception:
            pass

        bar_ref = ref_slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9) + Inches(0.3), Inches(1.5) + Inches(0.12), card_w - Inches(0.6), Inches(0.05))
        bar_ref.fill.solid()
        bar_ref.fill.fore_color.rgb = theme["accent"]
        bar_ref.line.fill.background()

        ref_box = ref_slide.shapes.add_textbox(Inches(1.25), Inches(1.75), card_w - Inches(0.7), card_h - Inches(0.45))
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
            p.font.color.rgb = RGBColor(255, 255, 255)
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



