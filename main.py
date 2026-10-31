import asyncio
import logging
import sys
import aiohttp
import json
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.exceptions import TelegramNetworkError
from aiogram.types import BotCommand, BotCommandScopeDefault, MenuButtonWebApp, WebAppInfo

import config
import database
from handlers import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

MAIN_LOOP = None
BOT_INSTANCE = None
DP_INSTANCE = None


THEMES_HTML = """<!DOCTYPE html>
<html lang="uz">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
  <title>🪄 Gamma AI Taqdimot Shablonlari</title>
  <script src="https://telegram.org/js/telegram-web-app.js"></script>
  <style>
    :root {
      --bg: var(--tg-theme-bg-color, #0b1120);
      --card-bg: var(--tg-theme-secondary-bg-color, #1e293b);
      --text: var(--tg-theme-text-color, #f8fafc);
      --hint: var(--tg-theme-hint-color, #94a3b8);
      --button: var(--tg-theme-button-color, #38bdf8);
      --button-text: var(--tg-theme-button-text-color, #0f172a);
      --border: #334155;
      --accent: #38bdf8;
    }
    * {
      box-sizing: border-box;
      -webkit-tap-highlight-color: transparent;
    }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
      margin: 0;
      padding: 12px 14px 40px;
    }
    header {
      text-align: center;
      margin-bottom: 14px;
    }
    h1 {
      font-size: 20px;
      font-weight: 700;
      margin: 0 0 4px;
      background: linear-gradient(135deg, #38bdf8, #818cf8);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    p.subtitle {
      font-size: 13px;
      color: var(--hint);
      margin: 0;
      line-height: 1.4;
    }
    .search-box {
      margin: 12px 0 10px;
    }
    .search-box input {
      width: 100%;
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 10px 14px;
      color: var(--text);
      font-size: 14px;
      outline: none;
      transition: border-color 0.2s;
    }
    .search-box input:focus {
      border-color: var(--accent);
    }
    .categories-bar {
      display: flex;
      gap: 8px;
      overflow-x: auto;
      padding-bottom: 8px;
      margin-bottom: 14px;
      scrollbar-width: none;
    }
    .categories-bar::-webkit-scrollbar {
      display: none;
    }
    .category-chip {
      flex: 0 0 auto;
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 20px;
      padding: 7px 14px;
      font-size: 13px;
      font-weight: 500;
      color: var(--hint);
      cursor: pointer;
      transition: all 0.2s ease;
    }
    .category-chip.active {
      background: var(--accent);
      color: #0b1120;
      font-weight: 700;
      border-color: var(--accent);
      box-shadow: 0 2px 8px rgba(56, 189, 248, 0.35);
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 14px;
    }
    .theme-card {
      background: var(--card-bg);
      border: 1.5px solid var(--border);
      border-radius: 14px;
      overflow: hidden;
      cursor: pointer;
      transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
      display: flex;
      flex-direction: column;
    }
    .theme-card:active {
      transform: scale(0.98);
      border-color: var(--accent);
    }
    .slide-preview-wrap {
      width: 100%;
      aspect-ratio: 16 / 9;
      position: relative;
      background: #0f172a;
      overflow: hidden;
      border-bottom: 1px solid var(--border);
    }
    .slide-preview-img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
      transition: transform 0.25s ease;
    }
    .theme-card:hover .slide-preview-img {
      transform: scale(1.03);
    }
    .slide-badge {
      position: absolute;
      top: 10px;
      right: 10px;
      background: rgba(0, 0, 0, 0.65);
      backdrop-filter: blur(6px);
      padding: 4px 10px;
      border-radius: 8px;
      font-size: 11px;
      font-weight: 700;
      color: #f8fafc;
      border: 1px solid rgba(255,255,255,0.25);
      box-shadow: 0 2px 6px rgba(0,0,0,0.3);
      z-index: 2;
    }
    .card-content {
      padding: 14px;
      display: flex;
      flex-direction: column;
      flex: 1;
    }
    .category-tag {
      font-size: 11px;
      font-weight: 700;
      color: var(--accent);
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 4px;
    }
    .theme-title {
      font-size: 16px;
      font-weight: 700;
      color: var(--text);
      margin-bottom: 6px;
    }
    .theme-desc {
      font-size: 12px;
      color: var(--hint);
      line-height: 1.45;
      margin-bottom: 10px;
      flex: 1;
    }
    .tags {
      display: flex;
      flex-wrap: wrap;
      gap: 4px;
      margin-bottom: 12px;
    }
    .tag {
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 4px;
      font-size: 10px;
      padding: 2px 6px;
      color: var(--hint);
    }
    .select-btn {
      background: var(--button);
      color: var(--button-text);
      border: none;
      border-radius: 8px;
      padding: 10px 14px;
      font-size: 13px;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      transition: opacity 0.2s ease;
    }
    .select-btn:active {
      opacity: 0.85;
    }
    .theme-card.gamma-card {
      border: 1.5px solid rgba(168, 85, 247, 0.45);
      box-shadow: 0 4px 14px rgba(168, 85, 247, 0.12);
    }
    .theme-card.gamma-card:hover {
      border-color: #c084fc;
      box-shadow: 0 6px 20px rgba(168, 85, 247, 0.28);
    }
    .select-btn.gamma-btn {
      background: linear-gradient(135deg, #7c3aed 0%, #db2777 100%);
      color: #ffffff;
      box-shadow: 0 3px 10px rgba(124, 58, 237, 0.35);
    }
    .overlay {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(11, 17, 32, 0.85);
      backdrop-filter: blur(8px);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      z-index: 999;
      padding: 20px;
      text-align: center;
      opacity: 1;
      transition: opacity 0.25s ease;
    }
    .overlay.hidden {
      display: none;
    }
    .spinner {
      width: 44px;
      height: 44px;
      border: 3.5px solid rgba(56, 189, 248, 0.2);
      border-top-color: var(--accent);
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
      margin-bottom: 16px;
    }
    @keyframes spin {
      to { transform: rotate(360deg); }
    }
    .overlay-title {
      font-size: 18px;
      font-weight: 700;
      color: #f8fafc;
      margin-bottom: 6px;
    }
    .overlay-sub {
      font-size: 13px;
      color: #94a3b8;
    }
  </style>
</head>
<body>
  <header>
    <h1>🪄 Gamma AI — Barcha Shablonlar</h1>
    <p class="subtitle">Barcha taqdimot shablonlari to'liq Gamma AI neyrotarmog'i orqali shakllantiriladi.<br>O'zingizga yoqqan Gamma uslubini tanlang!</p>
  </header>

  <div class="search-box">
    <input type="text" id="searchInput" placeholder="🔍 Gamma shablonlarini qidirish (IT, Tibbiyot, Biznes, OTM)..." oninput="filterThemes()">
  </div>

  <div class="categories-bar" id="categoriesBar"></div>
  <div class="grid" id="themesGrid"></div>

  <div id="loadingOverlay" class="overlay hidden">
    <div class="spinner"></div>
    <div class="overlay-title" id="overlayTitle">Gamma Shablon Tanlandi!</div>
    <div class="overlay-sub">🪄 Gamma AI taqdimotingizni shakllantirmoqda...</div>
  </div>

  <script>
    const tg = window.Telegram?.WebApp;
    const API_BASE = window.location.origin.includes("github.io") ? "https://slayd-bot-2.onrender.com" : "";
    if (tg) {
      tg.ready();
      tg.expand();
      try { tg.enableClosingConfirmation(); } catch(e){}
    }

    const categories = [
      { id: "all", name: "🪄 Barcha Fonlar (40+)" },
      { id: "tech", name: "⚡️ IT & Dasturlash" },
      { id: "med", name: "🩺 Tibbiyot & Salomatlik" },
      { id: "business", name: "💼 Biznes & Moliya" },
      { id: "academic", name: "🎓 OTM & Diplom Ishlari" },
      { id: "education", name: "📚 Ta'lim & Pedagogika" },
      { id: "humanities", name: "🏛 Tarix, Til & Huquq" },
      { id: "engineering", name: "📐 Aniq Fanlar & Texnika" },
      { id: "nature", name: "🌿 Agrar & Ekologiya" },
      { id: "creative", name: "🎨 San'at, Sport & Turizm" },
      { id: "minimal", name: "✨ Minimalist & Rasmiy" }
    ];

    const themes = [
      // ================= AUTO & SMART =================
      {
        id: "gamma",
        category: "all",
        categoryTitle: "🪄 Gamma AI — Universal & Intellektual",
        title: "Gamma AI (Universal Auto)",
        badge: "🪄 Gamma Smart",
        desc: "Gamma neyrotarmog'i mavzuni tahlil qilib, eng optimal infografika, kartalar va premium dizaynni o'zi tanlaydi.",
        tags: ["#GammaAI", "#AutoDesign", "#Universal", "#Infografika"],
        bg: "linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #db2777 100%)",
        accent: "#c084fc",
        isGamma: true
      },

      // ================= 1. IT, DASTURLASH & KIBERXAVFSIZLIK =================
      {
        id: "cyber",
        category: "tech",
        categoryTitle: "⚡️ IT, Kiberxavfsizlik & Tarmoqlar",
        title: "Cyber Dark & Neon Cyan",
        badge: "⚡️ Kiber & Tarmoq",
        desc: "Kiberxavfsizlik, axborot himoyasi, tarmoq arxitekturasi va pentesting mavzulari uchun qorong'u kiber-neon fon.",
        tags: ["#Kiberxavfsizlik", "#Tarmoqlar", "#Firewall", "#Cyber", "#DarkNeon"],
        bg: "linear-gradient(135deg, #020617 0%, #083344 50%, #0e7490 100%)",
        accent: "#06b6d4",
        isGamma: true
      },
      {
        id: "ai_violet",
        category: "tech",
        categoryTitle: "⚡️ Sun'iy Intellekt & Robototexnika",
        title: "AI Future & Neural Violet",
        badge: "🤖 Sun'iy Intellekt",
        desc: "Mashinaviy o'rganish, neyrotarmoqlar, robototexnika, ChatGPT va generativ AI mavzulari uchun neon binafsha fon.",
        tags: ["#AI", "#Neyron", "#Robototexnika", "#MachineLearning", "#DeepLearning"],
        bg: "linear-gradient(135deg, #1e1035 0%, #3b0764 50%, #6b21a8 100%)",
        accent: "#a855f7",
        isGamma: true
      },
      {
        id: "tech_matrix",
        category: "tech",
        categoryTitle: "⚡️ Dasturlash & Algoritmlar",
        title: "Terminal Code & Matrix Green",
        badge: "💻 Dasturlash & Kod",
        desc: "Python, Java, C++, algoritmlar, backend, Linux va DevOps bo'yicha amaliy dasturlash taqdimotlari.",
        tags: ["#Dasturlash", "#Python", "#Backend", "#Linux", "#DevOps"],
        bg: "linear-gradient(135deg, #02140d 0%, #064e3b 50%, #047857 100%)",
        accent: "#10b981",
        isGamma: true
      },
      {
        id: "tech_cloud",
        category: "tech",
        categoryTitle: "⚡️ Bulutli Tizimlar & Big Data",
        title: "Azure Cloud & Big Data",
        badge: "☁️ Bulutli Tizimlar",
        desc: "Katta ma'lumotlar (Big Data), AWS, Azure bulutli infratuzilmasi, serverlar va ma'lumotlar bazasi arxitekturasi.",
        tags: ["#Cloud", "#BigData", "#Azure", "#AWS", "#DataScience"],
        bg: "linear-gradient(135deg, #081d38 0%, #0f3d6b 50%, #0284c7 100%)",
        accent: "#38bdf8",
        isGamma: true
      },
      {
        id: "tech_mobile",
        category: "tech",
        categoryTitle: "⚡️ Mobil Ilovalar & UI/UX",
        title: "Mobile Dev & Flutter Coral",
        badge: "📱 Mobil UI/UX",
        desc: "Android, iOS, Flutter, React Native mobil dasturlar va zamonaviy ilovalar dizayni bo'yicha taqdimotlar.",
        tags: ["#Mobile", "#Android", "#iOS", "#Flutter", "#UIUX"],
        bg: "linear-gradient(135deg, #1f1124 0%, #4a154b 50%, #be185d 100%)",
        accent: "#fb7185",
        isGamma: true
      },

      // ================= 2. TIBBIYOT & SALOMATLIK =================
      {
        id: "med_clinic",
        category: "med",
        categoryTitle: "🩺 Tibbiyot, Anatomiya & Terapiya",
        title: "Clinical Teal & Shifoxona",
        badge: "🩺 Terapiya & Klinika",
        desc: "Umumiy tibbiyot, ichki kasalliklar terapiyasi, diagnostika va shifoxona tizimlari uchun toza tibbiy teal fon.",
        tags: ["#Tibbiyot", "#Klinika", "#Terapiya", "#Diagnostika", "#Shifokor"],
        bg: "linear-gradient(135deg, #042621 0%, #065f46 50%, #0d9488 100%)",
        accent: "#14b8a6",
        isGamma: true
      },
      {
        id: "med_pharma",
        category: "med",
        categoryTitle: "🩺 Farmatsevtika & Dorishunoslik",
        title: "Farmatsevtika & Bio Yalpiz",
        badge: "💊 Dori Vositalari",
        desc: "Farmakologiya, dori vositalari texnologiyasi, kimyoviy preparatlar va vaksinalar ishlab chiqarish tadqiqotlari.",
        tags: ["#Farmatsevtika", "#Dori", "#Vaksina", "#BioMint", "#Farmakologiya"],
        bg: "linear-gradient(135deg, #05241b 0%, #044e3b 50%, #059669 100%)",
        accent: "#10b981",
        isGamma: true
      },
      {
        id: "med_cardio",
        category: "med",
        categoryTitle: "🩺 Kardiologiya & Shoshilinch Yordam",
        title: "Kardiologiya & Qon Tomir Qizil",
        badge: "🫀 Kardiologiya & Jarrohlik",
        desc: "Yurak-qon tomir kasalliklari, kardiologiya, shoshilinch tez yordam va reanimatsiya mavzulari uchun pulsatsiyali qizil fon.",
        tags: ["#Kardiologiya", "#Yurak", "#Jarrohlik", "#Reanimatsiya", "#QonTomir"],
        bg: "linear-gradient(135deg, #2b080f 0%, #5c0f1e 50%, #9f1239 100%)",
        accent: "#f43f5e",
        isGamma: true
      },
      {
        id: "med_dental",
        category: "med",
        categoryTitle: "🩺 Stomatologiya & Ortodontiya",
        title: "Stomatologiya & Marvarid Oq",
        badge: "🦷 Stomatologiya",
        desc: "Tish davolash, karies profilaktikasi, implantatsiya, ortodontiya va og'iz bo'shlig'i gigiyenasi uchun pokiza dengiz foni.",
        tags: ["#Stomatologiya", "#TishDavolash", "#Ortodontiya", "#Implant"],
        bg: "linear-gradient(135deg, #081c2e 0%, #0c3658 50%, #0369a1 100%)",
        accent: "#38bdf8",
        isGamma: true
      },
      {
        id: "med_lab",
        category: "med",
        categoryTitle: "🩺 Biotexnologiya & Genetika",
        title: "Biotexnologiya & Genetika",
        badge: "🔬 Bio Laboratoriya",
        desc: "DNK tadqiqotlari, inson genomi, klinik laboratoriya tahlillari va hujayra biotexnologiyasi.",
        tags: ["#Genetika", "#DNK", "#Laboratoriya", "#Biotexnologiya", "#Mikrobiologiya"],
        bg: "linear-gradient(135deg, #091322 0%, #152945 50%, #1d4ed8 100%)",
        accent: "#60a5fa",
        isGamma: true
      },

      // ================= 3. BIZNES & MOLIYA =================
      {
        id: "biz_pitch",
        category: "business",
        categoryTitle: "💼 Biznes, Startap & Investitsiya",
        title: "Obsidian & Oltin Lux (Pitch Deck)",
        badge: "💼 Startap & Pitch Deck",
        desc: "Startap pitch deck, venchur investitsiyalar, biznes-reja va investorlar oldidagi nufuzli namoyishlar.",
        tags: ["#PitchDeck", "#Startap", "#Investitsiya", "#BiznesReja", "#Obsidian"],
        bg: "linear-gradient(135deg, #121214 0%, #222226 50%, #a16207 100%)",
        accent: "#eab308",
        isGamma: true
      },
      {
        id: "biz_bank",
        category: "business",
        categoryTitle: "💼 Bank, FinTech & Katta Moliya",
        title: "FinTech, Bank & Katta Moliya",
        badge: "📊 FinTech & Bank",
        desc: "Tijorat banklari, moliyaviy hisobotlar, kredit-depozit siyosati, audit va to'lov tizimlari.",
        tags: ["#Bank", "#Moliya", "#FinTech", "#Audit", "#Buxgalteriya"],
        bg: "linear-gradient(135deg, #061933 0%, #0c3866 50%, #0284c7 100%)",
        accent: "#38bdf8",
        isGamma: true
      },
      {
        id: "biz_crypto",
        category: "business",
        categoryTitle: "💼 Kriptovalyuta, Blokcheyn & Web3",
        title: "Kriptovalyuta & Blokcheyn",
        badge: "🪙 Web3 & Kripto",
        desc: "Kriptovalyutalar bozor tahlili, Bitcoin, aqlli shartnomalar, DeFi va markazlashmagan Web3 moliya tizimlari.",
        tags: ["#Kripto", "#Bitcoin", "#Blokcheyn", "#Web3", "#DeFi"],
        bg: "linear-gradient(135deg, #091b1a 0%, #064036 50%, #047857 100%)",
        accent: "#10b981",
        isGamma: true
      },
      {
        id: "biz_marketing",
        category: "business",
        categoryTitle: "💼 Marketing, Savdo & E-Commerce",
        title: "Marketing, Savdo & E-Commerce",
        badge: "🚀 SMM & Reklama",
        desc: "Raqamli marketing, maqsadli reklama (Target), brending, konversiya voronkasi va internet savdo.",
        tags: ["#Marketing", "#SMM", "#Reklama", "#Savdo", "#ECommerce"],
        bg: "linear-gradient(135deg, #2b0b1a 0%, #631238 50%, #be123c 100%)",
        accent: "#fb7185",
        isGamma: true
      },
      {
        id: "biz_lead",
        category: "business",
        categoryTitle: "💼 Boshqaruv & Korporativ Liderlik",
        title: "Korporativ Boshqaruv & Liderlik",
        badge: "🏆 Top Boshqaruv",
        desc: "Boshqaruv strategiyasi, kadrlar siyosati (HRM), inqirozga qarshi choralar va korporativ yetakchilik.",
        tags: ["#Menejment", "#Liderlik", "#HRM", "#Strategiya", "#Boshqaruv"],
        bg: "linear-gradient(135deg, #2b080a 0%, #580d13 50%, #991b1b 100%)",
        accent: "#ef4444",
        isGamma: true
      },

      // ================= 4. OTM & ILMIY TADQIQOTLAR =================
      {
        id: "academic_royal",
        category: "academic",
        categoryTitle: "🎓 OTM, Diplom & Magistratura",
        title: "Royal Academic Blue (OTM & Diplom)",
        badge: "🎓 Diplom & OTM",
        desc: "Oliy ta'lim muassasalari diplom ishi, bitiruv malakaviy ishi (BMI) va magistrlik dissertatsiyalari.",
        tags: ["#Diplom", "#Universitet", "#BMI", "#Magistratura", "#OTM"],
        bg: "linear-gradient(135deg, #081730 0%, #102a54 50%, #1e40af 100%)",
        accent: "#f59e0b",
        isGamma: true
      },
      {
        id: "academic_phd",
        category: "academic",
        categoryTitle: "🎓 Dissertatsiya & Monografiya",
        title: "Ilmiy Dissertatsiya & Monografiya",
        badge: "📜 PhD & Monografiya",
        desc: "Fan doktori (DSc), PhD ilmiy darajasi, monografiyalar va nufuzli ilmiy seminarlar uchun tantanali akademik fon.",
        tags: ["#PhD", "#Dissertatsiya", "#Monografiya", "#Doktorantura", "#IlmiyKengash"],
        bg: "linear-gradient(135deg, #211208 0%, #45210d 50%, #92400e 100%)",
        accent: "#d97706",
        isGamma: true
      },
      {
        id: "academic_research",
        category: "academic",
        categoryTitle: "🎓 Ilmiy Maqolalar & Scopus",
        title: "Ilmiy Maqola & Scopus Jurnallar",
        badge: "📚 Scopus & Tadqiqot",
        desc: "Xalqaro ilmiy jurnallar, Scopus / Web of Science indeksli maqolalar, ilmiy tajribalar va tahliliy hisobotlar.",
        tags: ["#Scopus", "#IlmiyMaqola", "#Jurnal", "#Tadqiqot", "#Tahlil"],
        bg: "linear-gradient(135deg, #0d1624 0%, #1a2c49 50%, #2563eb 100%)",
        accent: "#22d3ee",
        isGamma: true
      },

      // ================= 5. TA'LIM & PEDAGOGIKA =================
      {
        id: "edu_pedagogy",
        category: "education",
        categoryTitle: "📚 Zamonaviy Pedagogika & Maktab",
        title: "Zamonaviy Pedagogika & Metodika",
        badge: "📚 Maktab & Metodika",
        desc: "Innovatsion pedagogik texnologiyalar, namunali ochiq darslar, maktab metodikasi va dars ishlanmalari.",
        tags: ["#Pedagogika", "#Metodika", "#OchiqDars", "#Maktab", "#Talim"],
        bg: "linear-gradient(135deg, #300f04 0%, #682208 50%, #c2410c 100%)",
        accent: "#f97316",
        isGamma: true
      },
      {
        id: "edu_psychology",
        category: "education",
        categoryTitle: "📚 Psixologiya & Kognitiv Ta'lim",
        title: "Psixologiya & Kognitiv Rivojlanish",
        badge: "🧠 Psixologiya",
        desc: "Shaxs psixologiyasi, ruhiy salomatlik, stressni yengish, xulq-atvor tahlili va empatiya qonuniyatlari.",
        tags: ["#Psixologiya", "#Ruhiyat", "#Stress", "#Kognitiv", "#Munosabatlar"],
        bg: "linear-gradient(135deg, #180d28 0%, #351458 50%, #7e22ce 100%)",
        accent: "#c084fc",
        isGamma: true
      },
      {
        id: "edu_kids",
        category: "education",
        categoryTitle: "📚 Maktabgacha & Boshlang'ich Ta'lim",
        title: "Maktabgacha & Bolalar Ta'limi",
        badge: "🎈 Bolalar Ta'limi",
        desc: "Maktabgacha ta'lim (bog'cha), boshlang'ich sinf ta'limi, ertaklar, o'yin metodikalari va bolalar rivojlanishi.",
        tags: ["#Bogcha", "#Maktabgacha", "#Bolalar", "#Boshlangich", "#Oyinchroq"],
        bg: "linear-gradient(135deg, #101c2c 0%, #173854 50%, #0284c7 100%)",
        accent: "#fbbf24",
        isGamma: true
      },
      {
        id: "edu_languages",
        category: "education",
        categoryTitle: "📚 Xorijiy Tillar & Lingvistika",
        title: "Xorijiy Tillar & Lingvistika",
        badge: "🗣 IELTS & Tillar",
        desc: "Ingliz tili (IELTS / CEFR), nemis, rus, xitoy tillari va qiyosiy tilshunoslik fanlari bo'yicha darslar.",
        tags: ["#InglizTili", "#IELTS", "#CEFR", "#Tillar", "#Lingvistika"],
        bg: "linear-gradient(135deg, #091c2b 0%, #103c5e 50%, #0369a1 100%)",
        accent: "#38bdf8",
        isGamma: true
      },

      // ================= 6. TARIX, HUQUQ & ADABIYOT =================
      {
        id: "history_heritage",
        category: "humanities",
        categoryTitle: "🏛 Tarix, Arxeologiya & Madaniy Meros",
        title: "O'zbekiston Tarixi & Madaniy Meros",
        badge: "🏛 Tarix & Meros",
        desc: "Qadimgi davlatlar, Amir Temur saltanati, xonliklar, Jadidchilik harakati va moddiy-madaniy yodgorliklar.",
        tags: ["#Tarix", "#AmirTemur", "#Jadidlar", "#Xonliklar", "#Arxeologiya"],
        bg: "linear-gradient(135deg, #291407 0%, #542407 50%, #92400e 100%)",
        accent: "#f59e0b",
        isGamma: true
      },
      {
        id: "law_justice",
        category: "humanities",
        categoryTitle: "🏛 Huquqshunoslik & Adliya",
        title: "Yuridik Huquq & Sud Tizimi",
        badge: "⚖️ Huquq & Sud",
        desc: "Konstitutsiyaviy huquq, jinoyat qonunchiligi, sud-huquq islohoti, advokatura va adolat tamoyillari.",
        tags: ["#Huquq", "#Konstitutsiya", "#Sud", "#Adolat", "#Advokatura"],
        bg: "linear-gradient(135deg, #141312 0%, #292524 50%, #57534e 100%)",
        accent: "#e2e8f0",
        isGamma: true
      },
      {
        id: "humanities_uzbek",
        category: "humanities",
        categoryTitle: "🏛 O'zbek Tili & Mumtoz Adabiyot",
        title: "O'zbek Tili & Milliy Adabiyot",
        badge: "📖 Adabiyot & Til",
        desc: "Alisher Navoiy g'azallari, Bobur, mumtoz va zamonaviy o'zbek adabiyoti, badiiy asarlar tahlili.",
        tags: ["#Adabiyot", "#Navoiy", "#OnaTili", "#Sheriyat", "#BadiiyAsar"],
        bg: "linear-gradient(135deg, #240c1d 0%, #50133c 50%, #9d174d 100%)",
        accent: "#f472b6",
        isGamma: true
      },
      {
        id: "humanities_philosophy",
        category: "humanities",
        categoryTitle: "🏛 Falsafa, Mantiq & Jamiyatshunoslik",
        title: "Falsafa, Mantiq & Jamiyat",
        badge: "🗿 Falsafa & Mantiq",
        desc: "Sharq va G'arb falsafiy tafakkuri, formal mantiq, axloqshunoslik (etika) va zamonaviy ijtimoiy ong.",
        tags: ["#Falsafa", "#Mantiq", "#Etika", "#IjtimoiyOng", "#Jamiyat"],
        bg: "linear-gradient(135deg, #1c1a17 0%, #36322b 50%, #57534e 100%)",
        accent: "#fbbf24",
        isGamma: true
      },

      // ================= 7. ANIQ VA TABIIY FANLAR, MUHANDISLIK =================
      {
        id: "eng_math",
        category: "engineering",
        categoryTitle: "📐 Matematika & Muhandislik Grafikasi",
        title: "Oliy Matematika & Chizma Geometriya",
        badge: "📐 Matematika & Chizma",
        desc: "Matematik analiz, chiziqli algebra, differensial tenglamalar, muhandislik grafikasi va chizmachilik.",
        tags: ["#Matematika", "#Algebra", "#Geometriya", "#Chizma", "#Integral"],
        bg: "linear-gradient(135deg, #07152b 0%, #0e2d5c 50%, #1d4ed8 100%)",
        accent: "#38bdf8",
        isGamma: true
      },
      {
        id: "sci_physics",
        category: "engineering",
        categoryTitle: "📐 Fizika, Astronomiya & Kosmos",
        title: "Kosmos, Kvant Fizikasi & Astronomiya",
        badge: "🌌 Kosmos & Fizika",
        desc: "Nazariy fizika, astrofizika, kvant mexanikasi, elementar zarralar va koinotning paydo bo'lishi.",
        tags: ["#Fizika", "#Kosmos", "#Astronomiya", "#Kvant", "#Yadro"],
        bg: "linear-gradient(135deg, #030612 0%, #0a112c 50%, #312e81 100%)",
        accent: "#818cf8",
        isGamma: true
      },
      {
        id: "sci_chemistry",
        category: "engineering",
        categoryTitle: "📐 Kimyo & Laboratoriya Texnologiyalari",
        title: "Kimyo & Laboratoriya Reaksiyalari",
        badge: "🧪 Kimyo Fanlari",
        desc: "Organik va anorganik kimyo, kimyoviy texnologiyalar, polimerlar va sanoat kataliz jarayonlari.",
        tags: ["#Kimyo", "#Reaksiya", "#Molekula", "#Polimer", "#KimyoviyLab"],
        bg: "linear-gradient(135deg, #041c19 0%, #07423a 50%, #0f766e 100%)",
        accent: "#2dd4bf",
        isGamma: true
      },
      {
        id: "eng_civil",
        category: "engineering",
        categoryTitle: "📐 Qurilish, Arxitektura & Bino",
        title: "Qurilish, Geodeziya & Arxitektura",
        badge: "🏗 Qurilish & Bino",
        desc: "Zamonaviy binolar loyihalash, seysmik xavfsizlik, geodeziya, temir-beton konstruksiyalar va shaharsozlik.",
        tags: ["#Qurilish", "#Arxitektura", "#Bino", "#Geodeziya", "#Loyiha"],
        bg: "linear-gradient(135deg, #151a22 0%, #242c38 50%, #475569 100%)",
        accent: "#f97316",
        isGamma: true
      },
      {
        id: "eng_energy",
        category: "engineering",
        categoryTitle: "📐 Energetika & Qayta Tiklanuvchi Quvvat",
        title: "Energetika & Yashil Quvvat",
        badge: "⚡️ Energetika",
        desc: "Quyosh elektr stansiyalari, shamol energetikasi, atom va gidroenergetika hamda yuqori voltli tarmoqlar.",
        tags: ["#Energetika", "#QuyoshPaneli", "#Atom", "#Elektr", "#YashilEnergiya"],
        bg: "linear-gradient(135deg, #121c0e 0%, #1e3814 50%, #15803d 100%)",
        accent: "#eab308",
        isGamma: true
      },

      // ================= 8. EKOLOGIYA & QISHLOQ XO'JALIGI =================
      {
        id: "eco_green",
        category: "nature",
        categoryTitle: "🌿 Ekologiya & Yashil Makon",
        title: "Ekologiya & Yashil Makon",
        badge: "🌿 Ekologiya",
        desc: "Global iqlim o'zgarishi, Yashil Makon loyihasi, bio-xilma-xillik va atrof-muhitni muhofaza qilish choralari.",
        tags: ["#Ekologiya", "#YashilMakon", "#Iqlim", "#Tabiat", "#Biologiya"],
        bg: "linear-gradient(135deg, #042417 0%, #064e3b 50%, #047857 100%)",
        accent: "#10b981",
        isGamma: true
      },
      {
        id: "agro_harvest",
        category: "nature",
        categoryTitle: "🌿 Qishloq Xo'jaligi & Agrotexnologiya",
        title: "Qishloq Xo'jaligi & Agrotexnologiya",
        badge: "🌾 Agrar & Dehqonchilik",
        desc: "Paxtachilik, g'allachilik, zamonaviy issiqxona xo'jaliklari, tomchilatib sug'orish va urug'chilik genetikasi.",
        tags: ["#QishloqXojaligi", "#Agrar", "#Hosildorlik", "#Dehqon", "#Issiqxona"],
        bg: "linear-gradient(135deg, #1f1505 0%, #3d2c08 50%, #854d0e 100%)",
        accent: "#eab308",
        isGamma: true
      },
      {
        id: "water_hydro",
        category: "nature",
        categoryTitle: "🌿 Gidrologiya & Suv Resurslari",
        title: "Gidrologiya & Suv Resurslari",
        badge: "💧 Suv Xo'jaligi",
        desc: "Orol fojiasi va tiklash choralari, daryolar oqimi, suv omborlari, ichimlik suvi filtrlash va gidrologiya.",
        tags: ["#Gidrologiya", "#SuvXojaligi", "#Orol", "#Daryo", "#Melioratsiya"],
        bg: "linear-gradient(135deg, #051e2b 0%, #09405c 50%, #0284c7 100%)",
        accent: "#06b6d4",
        isGamma: true
      },

      // ================= 9. SAN'AT, SPORT & TURIZM =================
      {
        id: "art_design",
        category: "creative",
        categoryTitle: "🎨 Zamonaviy San'at & Grafik Dizayn",
        title: "Zamonaviy San'at & Grafik Dizayn",
        badge: "🎨 Grafik Dizayn",
        desc: "Vizual kommunikatsiya, ranglar nazariyasi, kompozitsiya, tipografika va raqamli illyustratsiya san'ati.",
        tags: ["#Dizayn", "#Sanat", "#Grafika", "#Ranglar", "#Illyustratsiya"],
        bg: "linear-gradient(135deg, #240a1c 0%, #52103d 50%, #be123c 100%)",
        accent: "#f43f5e",
        isGamma: true
      },
      {
        id: "tourism_uzbek",
        category: "creative",
        categoryTitle: "🎨 Turizm & Milliy Mehmondo'stlik",
        title: "Samarqand Firuzasi & Sayyohlik",
        badge: "🕌 Milliy Turizm",
        desc: "Buyuk Ipak Yo'li, Samarqand, Buxoro, Xiva obidalari, milliy mehmondo'stlik va turizm infratuzilmasi.",
        tags: ["#Turizm", "#Samarqand", "#Buxoro", "#IpakYoli", "#Sayyohlik"],
        bg: "linear-gradient(135deg, #05202b 0%, #084359 50%, #0284c7 100%)",
        accent: "#38bdf8",
        isGamma: true
      },
      {
        id: "sport_fitness",
        category: "creative",
        categoryTitle: "🎨 Jismoniy Tarbiya, Sport & Fitnes",
        title: "Sport, Fitnes & Dinamik Atletika",
        badge: "🏅 Sport & Salomatlik",
        desc: "Olimpiada o'yinlari, futbol taktikasi, fitnes mashg'ulotlari, sog'lom turmush tarzi va jismoniy tarbiya.",
        tags: ["#Sport", "#Futbol", "#Fitnes", "#Olimpiada", "#JismoniyTarbiya"],
        bg: "linear-gradient(135deg, #0c141e 0%, #172a38 50%, #15803d 100%)",
        accent: "#84cc16",
        isGamma: true
      },
      {
        id: "art_music",
        category: "creative",
        categoryTitle: "🎨 Musiqa, Estrada & Teatr",
        title: "Musiqa San'ati & Sahna Madaniyati",
        badge: "🎵 Musiqa & Teatr",
        desc: "Mumtoz musiqa, maqom san'ati, cholg'u asboblari, zamonaviy estrada va teatr sahna bezaklari.",
        tags: ["#Musiqa", "#Estrada", "#Maqom", "#Teatr", "#Cholgu"],
        bg: "linear-gradient(135deg, #1d0729 0%, #430c5e 50%, #9333ea 100%)",
        accent: "#d946ef",
        isGamma: true
      },

      // ================= 10. MINIMALIST & DAVLAT BOSHQARUVI =================
      {
        id: "minimal_platinum",
        category: "minimal",
        categoryTitle: "✨ Tipografika & Rasmiy Monoxrom",
        title: "Toza Monoxrom Tipografika",
        badge: "✨ Minimalist",
        desc: "Shveysariya uslubidagi toza tipografika, ortiqcha bezaklarsiz jiddiy va aniq ma'lumot beruvchi monoxrom fon.",
        tags: ["#Minimalizm", "#Monoxrom", "#Tipografika", "#Toza", "#Shveysariya"],
        bg: "linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%)",
        accent: "#f1f5f9",
        isGamma: true
      },
      {
        id: "gov_official",
        category: "minimal",
        categoryTitle: "✨ Davlat Organlari & Strategik Hisobot",
        title: "Davlat Boshqaruvi & Rasmiy Strategiya",
        badge: "🏛 Davlat & Strategiya",
        desc: "Vazirliklar, davlat organlari hisobotlari, qonunchilik qarorlari va rasmiy brifinglar uchun davlat darajasidagi fon.",
        tags: ["#Davlat", "#Vazirlik", "#Rasmiy", "#Strategiya", "#PrezidentQarori"],
        bg: "linear-gradient(135deg, #071730 0%, #0f2c59 50%, #1d4ed8 100%)",
        accent: "#eab308",
        isGamma: true
      }
    ];

    let currentCategory = "all";

    function renderCategories() {
      const container = document.getElementById("categoriesBar");
      container.innerHTML = "";
      categories.forEach(cat => {
        const chip = document.createElement("div");
        chip.className = `category-chip ${cat.id === currentCategory ? "active" : ""}`;
        chip.textContent = cat.name;
        chip.onclick = () => {
          currentCategory = cat.id;
          renderCategories();
          filterThemes();
        };
        container.appendChild(chip);
      });
    }

    function renderThemes(list) {
      const container = document.getElementById("themesGrid");
      container.innerHTML = "";
      if (list.length === 0) {
        container.innerHTML = `<div style="grid-column: 1 / -1; text-align: center; color: var(--hint); padding: 40px 0;">Hech qanday shablon topilmadi 🔍</div>`;
        return;
      }
      list.forEach(t => {
        const card = document.createElement("div");
        card.className = `theme-card ${t.isGamma ? "gamma-card" : ""}`;
        card.onclick = () => selectTheme(t);
        const btnText = t.isGamma ? "🪄 Gamma AI bilan tayyorlash" : "🚀 Ushbu fonga tayyorlash";
        const btnClass = t.isGamma ? "select-btn gamma-btn" : "select-btn";
        card.innerHTML = `
          <div class="slide-preview-wrap" style="background: ${t.bg};">
            <div style="position:absolute; inset:0; padding:12px; display:flex; flex-direction:column; justify-content:space-between; pointer-events:none; background: linear-gradient(180deg, rgba(0,0,0,0.15) 0%, rgba(0,0,0,0.65) 100%);">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:10px; font-weight:800; letter-spacing:0.8px; color:${t.accent}; text-transform:uppercase; background:rgba(0,0,0,0.5); padding:2px 8px; border-radius:4px; border:1px solid ${t.accent}44;">✦ ${t.badge}</span>
              </div>
              <div>
                <div style="font-size:13px; font-weight:700; color:#fff; text-shadow:0 1px 4px rgba(0,0,0,0.8);">${t.title}</div>
                <div style="height:3px; width:45px; background:${t.accent}; border-radius:2px; margin-top:4px;"></div>
              </div>
            </div>
            <img src="previews/${t.id.replace(':', '_')}.png" alt="${t.title}" class="slide-preview-img" style="opacity:0.2; mix-blend-mode:overlay;" onerror="this.style.display='none'" />
            <div class="slide-badge">${t.badge}</div>
          </div>
          <div class="card-content">
            <div class="category-tag">${t.categoryTitle}</div>
            <div class="theme-title">${t.title}</div>
            <div class="theme-desc">${t.desc}</div>
            <div class="tags">${t.tags.map(tag => `<span class="tag">${tag}</span>`).join("")}</div>
            <button class="${btnClass}" onclick="event.stopPropagation(); selectThemeById('${t.id}')">
              ${btnText}
            </button>
          </div>
        `;
        container.appendChild(card);
      });
    }

    function selectThemeById(id) {
      const t = themes.find(x => x.id === id);
      if (t) selectTheme(t);
    }

    function filterThemes() {
      const q = document.getElementById("searchInput").value.toLowerCase().trim();
      let list = themes;
      if (currentCategory !== "all") {
        list = list.filter(t => t.category === currentCategory);
      }
      if (q) {
        list = list.filter(t =>
          t.title.toLowerCase().includes(q) ||
          t.desc.toLowerCase().includes(q) ||
          t.categoryTitle.toLowerCase().includes(q) ||
          t.tags.some(tag => tag.toLowerCase().includes(q))
        );
      }
      renderThemes(list);
    }

    function selectTheme(theme) {
      if (tg?.HapticFeedback) {
        try { tg.HapticFeedback.notificationOccurred("success"); } catch(e){}
      }
      const overlay = document.getElementById("loadingOverlay");
      document.getElementById("overlayTitle").textContent = `${theme.title} tanlandi!`;
      const overlaySub = overlay.querySelector(".overlay-sub");
      if (overlaySub) {
        overlaySub.textContent = theme.isGamma
          ? "🪄 Gamma AI taqdimotingizni shakllantirmoqda..."
          : "🚀 Taqdimotingiz tayyorlanmoqda...";
      }
      overlay.classList.remove("hidden");

      const user = tg?.initDataUnsafe?.user;
      const userId = user ? user.id : null;

      // 1. Telegram WebApp sendData orqali yuborish (KeyboardButton ochilganda)
      try {
        if (tg && typeof tg.sendData === "function") {
          tg.sendData(theme.id);
        }
      } catch(e) {
        console.log("tg.sendData:", e);
      }

      // 2. HTTP POST orqali yuborish (Inline button ochilganda ham 100% ishlaydi)
      if (userId) {
        fetch(API_BASE + "/api/select-theme", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ user_id: userId, theme: theme.id, initData: tg?.initData || "" })
        }).finally(() => {
          setTimeout(() => { if (tg) tg.close(); }, 350);
        });
      } else {
        setTimeout(() => { if (tg) tg.close(); }, 400);
      }
    }

    renderCategories();
    renderThemes(themes);

    // Asinxron ravishda Gamma hisobidagi maxsus temalarni yuklash
    async function loadWorkspaceGammaThemes() {
      try {
        const resp = await fetch(API_BASE + "/api/gamma-themes");
        if (!resp.ok) return;
        const data = await resp.json();
        if (data.themes && Array.isArray(data.themes) && data.themes.length > 0) {
          if (!categories.some(c => c.id === "workspace")) {
            categories.splice(1, 0, { id: "workspace", name: "🪄 Mening Gamma Temalarim" });
            renderCategories();
          }
          data.themes.forEach(gt => {
            const customId = `gamma:${gt.id}`;
            if (!themes.some(x => x.id === customId)) {
              themes.unshift({
                id: customId,
                category: "workspace",
                categoryTitle: `🪄 Gamma Workspace — ${gt.type === "custom" ? "Maxsus Tema" : "Standart"}`,
                title: gt.name || "Gamma Custom Theme",
                badge: "🪄 Gamma Theme",
                desc: `Sizning Gamma hisobingizdagi brend uslubi (${(gt.colorKeywords || []).join(", ") || "Gamma uslubi"}).`,
                tags: ["#GammaTheme", "#Workspace", "#Custom", "#AI"],
                bg: "linear-gradient(135deg, #1e1b4b 0%, #4338ca 50%, #7c3aed 100%)",
                accent: "#c084fc",
                isGamma: true
              });
            }
          });
          filterThemes();
        }
      } catch(e) {
        console.log("Gamma themes load error:", e);
      }
    }
    loadWorkspaceGammaThemes();
  </script>
</body>
</html>
"""

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Render yoki Uptime xizmatlari salomatlik tekshiruvi uchun
        if self.path.startswith("/health") or self.path.startswith("/ping"):
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(b"Bot is running 24/7!")
            return

        # Gamma hisobidagi mavjud temalar ro'yxatini qaytarish
        if self.path.startswith("/api/gamma-themes"):
            import gamma_service
            themes_list = []
            if gamma_service.is_gamma_available():
                if MAIN_LOOP and not MAIN_LOOP.is_closed():
                    try:
                        fut = asyncio.run_coroutine_threadsafe(gamma_service.get_gamma_themes(), MAIN_LOOP)
                        themes_list = fut.result(timeout=6)
                    except Exception as e:
                        logger.warning(f"Error fetching gamma themes: {e}")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"themes": themes_list}).encode("utf-8"))
            return

        # Slayd fonlari rasmlarini ko'rsatish (/preview/circuit.png yoki /previews/...)
        if self.path.startswith("/preview/") or self.path.startswith("/previews/"):
            fname = os.path.basename(self.path.split("?")[0])
            fpath = os.path.join(os.path.dirname(__file__), "previews", fname)
            if os.path.exists(fpath):
                self.send_response(200)
                if fname.endswith(".png"):
                    self.send_header("Content-Type", "image/png")
                else:
                    self.send_header("Content-Type", "image/jpeg")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Cache-Control", "public, max-age=86400")
                self.end_headers()
                with open(fpath, "rb") as fp:
                    self.wfile.write(fp.read())
                return
            else:
                self.send_response(404)
                self.end_headers()
                return

        # Barcha so'rovlar (/, /themes, /index.html, /?tgWebApp... va boshqalar)
        # to'g'ridan-to'g'ri Slayd Fonlari Mini Ilovasini to'liq ko'rsatadi
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(THEMES_HTML.encode("utf-8"))

    def do_POST(self):
        if self.path.startswith("/api/select-theme"):
            try:
                content_len = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_len).decode("utf-8")
                payload = json.loads(body)
                user_id = int(payload.get("user_id", 0))
                theme_id = payload.get("theme", "mix")

                if user_id and BOT_INSTANCE and MAIN_LOOP and not MAIN_LOOP.is_closed():
                    from handlers import handle_theme_from_webapp
                    asyncio.run_coroutine_threadsafe(
                        handle_theme_from_webapp(user_id=user_id, theme_id=theme_id, bot=BOT_INSTANCE, dp=DP_INSTANCE),
                        MAIN_LOOP
                    )

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(b'{"status":"ok"}')
                return
            except Exception as e:
                logger.error(f"Error in /api/select-theme: {e}")
                self.send_response(500)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(b'{"status":"error"}')
                return

        self.send_response(404)
        self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

    def log_message(self, format, *args):
        # Don't clutter logs with pings
        pass

def start_health_server():
    port = int(os.environ.get("PORT", 10000))
    try:
        server = HTTPServer(("0.0.0.0", port), HealthHandler)
        logger.info(f"Healthcheck va WebApp server 0.0.0.0:{port} da ishga tushdi.")
        server.serve_forever()
    except Exception as e:
        logger.error(f"Health server xatosi: {e}")

threading.Thread(target=start_health_server, daemon=True).start()


_ADMIN_NOTIFIED = False

async def render_keep_alive_loop():
    """Render Free tier xizmatini uyquga (spin-down) ketib qolishdan asrash uchun har 8 daqiqada o'zini ping qilib turadi."""
    render_url = os.getenv("RENDER_EXTERNAL_URL") or "https://slayd-bot-2.onrender.com"
    health_url = f"{render_url.rstrip('/')}/health"
    await asyncio.sleep(60)  # Ishga tushgandan 1 daqiqa o'tgach boshlaymiz
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(health_url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status == 200:
                        logger.debug("Render keep-alive ping muvaffaqiyatli yuborildi.")
        except Exception as e:
            logger.debug(f"Render keep-alive ping ogohlantirish: {e}")
        await asyncio.sleep(480)  # Har 8 daqiqada takrorlanadi (Render 15 daqiqada o'chadi)

async def setup_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="🚀 Qayta ishga tushirish / Start"),
        BotCommand(command="slayd", description="📊 Slayd tayyorlash / Create slides"),
        BotCommand(command="lang", description="🌐 Tilni o'zgartirish / Language"),
        BotCommand(command="profil", description="👤 Profil / Profile"),
        BotCommand(command="fayllarim", description="📁 Mening fayllarim / My files"),
        BotCommand(command="tariffs", description="💳 Tariflar / Plans"),
        BotCommand(command="haqida", description="ℹ️ Bot haqida / About"),
        BotCommand(command="murojaat", description="👨‍💻 Adminga murojaat / Contact"),
    ]
    try:
        await bot.set_my_commands(commands, scope=BotCommandScopeDefault())
        logger.info("Bot buyruqlari (Menu) muvaffaqiyatli o'rnatildi.")
    except Exception as e:
        logger.warning(f"Bot buyruqlarini o'rnatishda xatolik: {e}")

    try:
        await bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(
                text="🪄 Gamma AI Shablonlari",
                web_app=WebAppInfo(url=config.THEMES_WEBAPP_URL)
            )
        )
        logger.info("Chat MenuButtonWebApp muvaffaqiyatli o'rnatildi.")
    except Exception as e:
        logger.warning(f"MenuButtonWebApp o'rnatishda xatolik: {e}")

    global _ADMIN_NOTIFIED
    if not _ADMIN_NOTIFIED:
        try:
            render_url = os.getenv("RENDER_EXTERNAL_URL", "https://slayd-bot-2.onrender.com")
            await bot.send_message(
                config.ADMIN_ID,
                f"🚀 <b>Bot muvaffaqiyatli ishga tushdi!</b>\n\n"
                f"🌐 <b>Render URL:</b> <code>{render_url}</code>\n"
                f"📱 <b>THEMES_WEBAPP_URL:</b> <code>{config.THEMES_WEBAPP_URL}</code>\n"
                f"✨ Asosiy menyu va pastki chat menyusida Mini ilova tugmasi faollashtirildi!",
                parse_mode="HTML"
            )
            _ADMIN_NOTIFIED = True
        except Exception as e:
            logger.warning(f"Admin startup xabari xatosi: {e}")

async def main():
    if not config.BOT_TOKEN:
        logger.error("DIQQAT: BOT_TOKEN aniqlanmadi! Render Environment Variables bo'limiga BOT_TOKEN qo'shing.")
        while True:
            await asyncio.sleep(3600)

    if not config.GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY kiritilmagan! Slayd generatsiyasi ishlamasligi mumkin.")

    # Init SQLite DB
    try:
        await database.init_db()
        logger.info("Ma'lumotlar bazasi tayyorlandi.")
    except Exception as e:
        logger.error(f"Baza xatoligi: {e}")

    # Bot & Dispatcher
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    dp.include_router(router)

    global MAIN_LOOP, BOT_INSTANCE, DP_INSTANCE
    MAIN_LOOP = asyncio.get_running_loop()
    BOT_INSTANCE = bot
    DP_INSTANCE = dp

    # Render bulutida botni 24/7 uyg'oq (faol) ushlab turish uchun keep-alive
    asyncio.create_task(render_keep_alive_loop())


    try:
        while True:
            try:
                try:
                    await setup_bot_commands(bot)
                except Exception as e:
                    logger.warning(f"Menu o'rnatish xatoligi: {e}")

                logger.info("Bot polling ishga tushmoqda...")
                await dp.start_polling(bot)
                break
            except (TelegramNetworkError, aiohttp.ClientError, asyncio.TimeoutError) as net_err:
                logger.warning(f"Tarmoqqa ulanishda xatolik ({net_err}). 5 soniyadan so'ng qayta urinib ko'riladi...")
                await asyncio.sleep(5)
            except (KeyboardInterrupt, SystemExit):
                break
            except Exception as e:
                logger.error(f"Kutilmagan xatolik yuz berdi: {e}")
                await asyncio.sleep(5)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
