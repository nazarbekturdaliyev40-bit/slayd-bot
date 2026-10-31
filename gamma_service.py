import os
import asyncio
import logging
import aiohttp
import tempfile
import config

logger = logging.getLogger(__name__)

GAMMA_API_BASE = "https://public-api.gamma.app/v1.0"

GAMMA_THEME_PROMPTS = {
    "gamma": "Universal, zamonaviy va professional korporativ infografika dizayni.",
    "gamma_auto": "Universal, zamonaviy va professional korporativ infografika dizayni.",
    # 1. IT & Kiber
    "cyber": "Qorong'u kiber-texnologiya, IT, dasturlash va neon vizual aksentlar uslubida (Dark Neon Tech / Cyberpunk). Yuqori texnologik ikonka va kartalar.",
    "gamma_cyber": "Qorong'u kiber-texnologiya, IT, dasturlash va neon vizual aksentlar uslubida (Dark Neon Tech / Cyberpunk). Yuqori texnologik ikonka va kartalar.",
    "ai_violet": "Kelajak texnologiyalari, neon binafsha, sun'iy intellekt, robototexnika va startaplar (Neon Violet & Future AI).",
    "gamma_violet": "Kelajak texnologiyalari, neon binafsha, sun'iy intellekt, robototexnika va startaplar (Neon Violet & Future AI).",
    "tech_matrix": "Qorong'u terminal, kodlash, backend va dasturchilar kodi yashil neon uslubi (Terminal Code & Matrix Green).",
    "tech_cloud": "Bulutli infratuzilma, Azure, katta ma'lumotlar oqimi va server tahlili (Azure Cloud & Big Data Stream).",
    "tech_mobile": "Zamonaviy mobil interfeys, Flutter va React Native UI/UX uslubi (Mobile Dev Coral & Sleek UI).",

    # 2. Tibbiyot & Salomatlik
    "med_clinic": "Toza zumrad yashil, ochiq tibbiyot, biologiya, ekologiya va salomatlik uslubida (Fresh Emerald & Clean Health).",
    "gamma_emerald": "Toza zumrad yashil, ochiq tibbiyot, biologiya, ekologiya va salomatlik uslubida (Fresh Emerald & Clean Health).",
    "med_pharma": "Farmatsevtika laboratoriyasi, bio-yalpiz va xavfsiz dori vositalari ishlab chiqarish (Pharmaceutical Mint & Clinical Drug).",
    "med_cardio": "Yurak pulsi, kardiogramma chiziqlari, qizil aksentlar va hayotiy muhim tibbiyot (Pulse Cardio & Vascular Life).",
    "med_dental": "Toza marvarid oq, stomatologiya uskunalari va mukammal tabassum gigiyenasi (Dental Pearl & Orthodontic Care).",
    "med_lab": "Klinik laboratoriyalar, genetika, stomatologiya, biotexnologiya va yuqori aniqlikdagi tibbiy tadqiqotlar.",
    "gamma_nordic": "Klinik laboratoriyalar, genetika, stomatologiya, biotexnologiya va yuqori aniqlikdagi tibbiy tadqiqotlar.",

    # 3. Biznes & Moliya
    "biz_pitch": "Premium hashamatli qora obsidian, oltin aksentlar va professional biznes pitch-deck uslubida (Obsidian & Gold Lux).",
    "gamma_obsidian": "Premium hashamatli qora obsidian, oltin aksentlar va professional biznes pitch-deck uslubida (Obsidian & Gold Lux).",
    "biz_bank": "To'q moviy okean, firuza neon, bulutli hisoblash, moliya va tahliliy diagrammalar (Ocean Teal & FinTech Analytics).",
    "gamma_ocean": "To'q moviy okean, firuza neon, bulutli hisoblash, moliya va tahliliy diagrammalar (Ocean Teal & FinTech Analytics).",
    "biz_crypto": "Blokcheyn, kriptovalyuta, zamonaviy Web3 va raqamli aktivlar grafikalari (Crypto Blockchain & DeFi).",
    "biz_marketing": "Vibratsiyali to'q sariq va pushti gradyent, e-commerce, raqamli marketing va savdo konversiyasi (Vibrant Marketing & Growth).",
    "biz_lead": "Kuchli liderlik, to'q qizil rubin aksentlar, strategik boshqaruv va biznes marketing (Crimson Bold & Strategic Impact).",
    "gamma_crimson": "Kuchli liderlik, to'q qizil rubin aksentlar, strategik boshqaruv va biznes marketing (Crimson Bold & Strategic Impact).",

    # 4. OTM & Diplom
    "academic_royal": "Oksford qirollik to'q moviy va oltin aksentlari, OTM akademik anjumani va diplom ishi (Royal Academic & University).",
    "academic_phd": "Qadimiy qora shokolad, iliq bronza, ilmiy dissertatsiya va nufuzli monografiya (PhD Dissertation & Scholar Heritage).",
    "academic_research": "Cambridge to'q kulrang, Scopus indeksli ilmiy maqolalar va yuqori ilmiy tahlil (Scopus Research & Empirical Study).",

    # 5. Ta'lim & Pedagogika
    "edu_pedagogy": "Quyoshli yorqin to'q sariq va sariq energiya, zamonaviy pedagogika, motivatsiya va ta'lim metodikasi (Solar Citrus & Dynamic Edu).",
    "gamma_solar": "Quyoshli yorqin to'q sariq va sariq energiya, zamonaviy pedagogika, motivatsiya va ta'lim metodikasi (Solar Citrus & Dynamic Edu).",
    "edu_psychology": "Tinchlantiruvchi lavanda, kognitiv rivojlanish, miya faoliyati va shaxs psixologiyasi (Calm Lavender & Mind Psychology).",
    "edu_kids": "Yorqin quvnoq ranglar, bolalar psixologiyasi, boshlang'ich sinf va qiziqarli ta'lim (Playful Pastel & Child Learning).",
    "edu_languages": "Xalqaro aloqalar, lingvistika, IELTS va xorijiy tillarni o'rganish xaritalari (Global Linguistics & Language Arts).",

    # 6. Tarix, Huquq & Falsafa
    "history_heritage": "Qadimiy pergament, iliq oltin-bronza, tarix, arxeologiya, falsafa va madaniy meros (Vintage Amber & Heritage).",
    "gamma_amber": "Qadimiy pergament, iliq oltin-bronza, tarix, arxeologiya, falsafa va madaniy meros (Vintage Amber & Heritage).",
    "law_justice": "Sud zali, qonun va adolat tarozisi, to'q kulrang tosh va platina uslubi (Judicial Law & Scale of Justice).",
    "humanities_uzbek": "Nafis milliy naqshlar, ipak ipakligi, Alisher Navoiy va o'zbek mumtoz adabiyoti (Poetic Mulberry & Uzbek Classics).",
    "humanities_philosophy": "Qadimiy antik haykallar, bronza, falsafiy tafakkur va mantiq (Philosophical Bronze & Socratic Wisdom).",

    # 7. Aniq Fanlar & Texnika
    "eng_math": "Muhandislik chizmalari, geometrik to'rlar, oliy matematika, arxitektura va loyihalash (Geometric Blueprint & Engineering).",
    "gamma_blueprint": "Muhandislik chizmalari, geometrik to'rlar, oliy matematika, arxitektura va loyihalash (Geometric Blueprint & Engineering).",
    "sci_physics": "Chuqur kosmik qorong'ulik, binafsha neon, yulduzli tumanliklar, kvant fizikasi va astronomiya (Deep Cosmos & Astro Science).",
    "gamma_space": "Chuqur kosmik qorong'ulik, binafsha neon, yulduzli tumanliklar, kvant fizikasi va astronomiya (Deep Cosmos & Astro Science).",
    "sci_chemistry": "Laboratoriya kolbalari, kimyoviy elementlar reaksiyasi, neft-kimyo va zamonaviy materiallar (Chemical Reagent & Lab Science).",
    "eng_civil": "Qurilish kranlari, zamonaviy megastrukturalar, geodeziya va beton-metall arxitekturasi (Civil Architecture & High-Rise Steel).",
    "eng_energy": "Elektr transformatorlari, quyosh batareyalari, shamol turbinalari va yashil energetika (Power Grid & Renewable Energy).",

    # 8. Ekologiya & Agrar
    "eco_green": "Zich o'rmon yashilligi, ekologiya, agrar soha, bio-xilma-xillik va tabiatni muhofaza qilish (Deep Forest & Sustainable Nature).",
    "gamma_forest": "Zich o'rmon yashilligi, ekologiya, agrar soha, bio-xilma-xillik va tabiatni muhofaza qilish (Deep Forest & Sustainable Nature).",
    "agro_harvest": "Oltin boshoqlar, hosildor yer, qishloq xo'jaligi texnikasi va issiqxona agronomiyasi (Golden Harvest & Modern Agrotech).",
    "water_hydro": "Kristal toza suv to'lqinlari, gidroinshootlar, tomchilatib sug'orish va suv balansi (Crystal Hydrology & Water Ecology).",

    # 9. San'at, Sport & Turizm
    "art_design": "Yumshoq pastel ranglar, zamonaviy dizayn, san'at va marketing infografikasi uslubida (Pastel Prism & Creative Art).",
    "gamma_pastel": "Yumshoq pastel ranglar, zamonaviy dizayn, san'at va marketing infografikasi uslubida (Pastel Prism & Creative Art).",
    "tourism_uzbek": "Registon maydoni feruza gumbazlari, Buyuk Ipak Yo'li va O'zbekiston sayyohlik salohiyati (Silk Road Turquoise & Heritage Tourism).",
    "sport_fitness": "Dinamik sport harakati, yuqori energiya, lime-neon va atletik quvvat (Dynamic Athletics & High Energy Sport).",
    "art_music": "Konsert sahnasi chiroqlari, orkestr partituralari va zamonaviy musiqa to'lqinlari (Stage Spotlight & Acoustic Sound).",

    # 10. Minimalist & Rasmiy
    "minimal_platinum": "Minimalist oq-qora monoxrom, zamonaviy tipografika, yuridik va nufuzli rasmiy uslub (Platinum Monochrome & Clean Typography).",
    "gamma_mono": "Minimalist oq-qora monoxrom, zamonaviy tipografika, yuridik va nufuzli rasmiy uslub (Platinum Monochrome & Clean Typography).",
    "gov_official": "Davlat gerbi aksenti, chuqur to'q ko'k, rasmiy hisobotlar va milliy strategiyalar (State Governance & Official Briefing)."
}

LEGACY_TO_GAMMA = {
    "circuit": "gamma_cyber",
    "cyber": "gamma_cyber",
    "slice": "gamma_cyber",
    "tech_matrix": "gamma_cyber",
    "tech_cloud": "gamma_cyber",
    "tech_mobile": "gamma_cyber",
    "ai_violet": "gamma_violet",
    "tech_neon": "gamma_cyber",
    "it_dark_code": "gamma_cyber",
    "cyber_matrix": "gamma_cyber",
    "it": "gamma_cyber",
    "office": "gamma_obsidian",
    "biz_pitch": "gamma_obsidian",
    "biz_bank": "gamma_ocean",
    "biz_crypto": "gamma_obsidian",
    "biz_marketing": "gamma_solar",
    "biz_lead": "gamma_crimson",
    "academic_royal": "gamma_obsidian",
    "academic_phd": "gamma_amber",
    "academic_research": "gamma_nordic",
    "dark": "gamma_obsidian",
    "econ_emerald": "gamma_obsidian",
    "economy": "gamma_obsidian",
    "droplet": "gamma_emerald",
    "blue": "gamma_emerald",
    "med_clinic": "gamma_emerald",
    "med_pharma": "gamma_emerald",
    "med_cardio": "gamma_crimson",
    "med_dental": "gamma_nordic",
    "med_lab": "gamma_nordic",
    "medical_teal": "gamma_emerald",
    "medical_clean": "gamma_emerald",
    "medicine": "gamma_emerald",
    "facet": "gamma_forest",
    "green": "gamma_forest",
    "eco_forest": "gamma_forest",
    "eco_green": "gamma_forest",
    "agro_harvest": "gamma_amber",
    "water_hydro": "gamma_ocean",
    "biology": "gamma_forest",
    "academic_gold": "gamma_obsidian",
    "academic_navy": "gamma_ocean",
    "history": "gamma_amber",
    "history_heritage": "gamma_amber",
    "law_justice": "gamma_mono",
    "humanities_uzbek": "gamma_pastel",
    "humanities_philosophy": "gamma_amber",
    "vintage": "gamma_amber",
    "retrospect": "gamma_amber",
    "integral": "gamma_blueprint",
    "eng_math": "gamma_blueprint",
    "sci_chemistry": "gamma_emerald",
    "eng_civil": "gamma_blueprint",
    "eng_energy": "gamma_solar",
    "math_slate": "gamma_blueprint",
    "math": "gamma_blueprint",
    "physics": "gamma_space",
    "sci_physics": "gamma_space",
    "celestial": "gamma_space",
    "purple": "gamma_violet",
    "canva_pastel": "gamma_pastel",
    "art_design": "gamma_pastel",
    "tourism_uzbek": "gamma_ocean",
    "sport_fitness": "gamma_solar",
    "art_music": "gamma_violet",
    "art": "gamma_pastel",
    "white": "gamma_mono",
    "minimal_platinum": "gamma_mono",
    "gov_official": "gamma_ocean",
    "navy": "gamma_ocean",
    "savon": "gamma_obsidian",
    "ion": "gamma_solar",
    "edu_pedagogy": "gamma_solar",
    "edu_psychology": "gamma_violet",
    "edu_kids": "gamma_pastel",
    "edu_languages": "gamma_ocean",
    "pedagogy_warm": "gamma_solar",
    "law_burgundy": "gamma_crimson",
    "modern_crimson": "gamma_crimson",
    "mix": "gamma",
    "auto": "gamma"
}

def is_gamma_available() -> bool:
    """Tekshiradi: Gamma API kaliti sozlanganmi?"""
    return bool(config.GAMMA_API_KEY and len(config.GAMMA_API_KEY.strip()) > 5)

async def get_gamma_themes(limit: int = 50) -> list:
    """Gamma API dan barcha mavjud temalarni (standard va custom) tortib oladi."""
    if not is_gamma_available():
        return []

    headers = {
        "X-API-KEY": config.GAMMA_API_KEY,
        "Content-Type": "application/json"
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{GAMMA_API_BASE}/themes?limit={limit}",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=15)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("data", [])
                else:
                    logger.warning(f"Gamma get_themes HTTP {resp.status}")
    except Exception as e:
        logger.error(f"Gamma get_themes error: {e}")
    return []

def save_gamma_key(new_key: str) -> bool:
    """Yangi Gamma API kalitini saqlaydi va konfiguratsiyani yangilaydi."""
    new_key = new_key.strip()
    config.GAMMA_API_KEY = new_key
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            found = False
            new_lines = []
            for line in lines:
                if line.startswith("GAMMA_API_KEY="):
                    new_lines.append(f"GAMMA_API_KEY={new_key}\n")
                    found = True
                else:
                    new_lines.append(line)
            if not found:
                new_lines.append(f"GAMMA_API_KEY={new_key}\n")
            with open(env_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            return True
        except Exception as e:
            logger.error(f".env ga GAMMA_API_KEY yozishda xatolik: {e}")
            return False
    return False

async def generate_gamma_presentation(
    topic: str,
    num_cards: int = 8,
    export_as: str = "pptx",
    author_info: str = "",
    status_callback = None,
    language: str = "uz",
    theme_choice: str = "gamma",
    theme_id: str = None
) -> dict:
    """
    Gamma.app API (v1.0) orqali professional taqdimot yaratadi.
    Natijada .pptx fayli va jonli veb havola (gammaUrl) qaytaradi.
    """
    if not is_gamma_available():
        return {
            "success": False,
            "error": "GAMMA_API_KEY sozlanmagan. Iltimos, gamma.app API kalitini kiriting."
        }

    api_key = config.GAMMA_API_KEY
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }

    import locales
    lang_info = locales.get_slide_lang_info(language)

    # Maxsus vizual uslub va dizayn tavsifi
    clean_choice = theme_choice.split(":")[0] if ":" in theme_choice else theme_choice
    if clean_choice in LEGACY_TO_GAMMA:
        clean_choice = LEGACY_TO_GAMMA[clean_choice]
    visual_style = GAMMA_THEME_PROMPTS.get(
        clean_choice,
        "Zamonaviy, yuqori sifatli va professional korporativ infografika dizayni."
    )

    full_prompt = (
        f"Mavzu: {topic}\n"
        f"Til: {lang_info['prompt']}\n"
        f"Dizayn va vizual estetika: {visual_style}\n"
        f"Talab: Matn harflari va sarlavhalar har doim to'q fonda aniq va tiniq ko'rinishi uchun OQ rangda (white font) bo'lsin, qora xira harflardan foydalanilmasin. Slaydlar daftarning oq varag'iga o'xshab qolmasin, balki zamonaviy hashamatli infografik taqdimot uslubida shakllantirilsin.\n"
        f"Uslub: OTM talabalari uchun akademik, professional, boy ilmiy ma'lumotlar va jozibador vizual infografikalar bilan.\n"
    )
    if author_info:
        full_prompt += f"Muallif va OTM rekvizitlari: {author_info}\n"

    # numCards clamp between 5 and 30
    clamped_cards = max(5, min(num_cards, 30))

    payload = {
        "inputText": full_prompt,
        "textMode": "generate",
        "format": "presentation",
        "numCards": clamped_cards,
        "exportAs": export_as
    }
    if theme_id:
        payload["themeId"] = theme_id

    async with aiohttp.ClientSession() as session:
        # 1. Start generation
        logger.info(f"Gamma API ga so'rov yuborilmoqda: topic='{topic}', cards={clamped_cards}")
        try:
            async with session.post(
                f"{GAMMA_API_BASE}/generations",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                resp_text = await resp.text()
                if resp.status not in (200, 201):
                    logger.error(f"Gamma API generation start failed ({resp.status}): {resp_text}")
                    return {
                        "success": False,
                        "error": f"Gamma API xatolik qaytardi ({resp.status}): {resp_text}"
                    }
                data = await resp.json()
        except Exception as e:
            logger.error(f"Gamma API connection error: {e}")
            return {
                "success": False,
                "error": f"Gamma serveriga ulanishda xatolik: {e}"
            }

        generation_id = data.get("generationId")
        if not generation_id:
            return {
                "success": False,
                "error": f"Gamma javobida generationId topilmadi: {data}"
            }

        logger.info(f"Gamma generatsiya boshlandi, ID: {generation_id}")
        if status_callback:
            try:
                await status_callback("🎨 Gamma AI taqdimot kartalarini yaratmoqda va dizayn bermoqda...")
            except Exception:
                pass

        # 2. Polling for completion
        max_attempts = 35  # 35 * 4s = 140s
        poll_interval = 4
        result_data = None

        for attempt in range(max_attempts):
            await asyncio.sleep(poll_interval)
            try:
                async with session.get(
                    f"{GAMMA_API_BASE}/generations/{generation_id}",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=20)
                ) as poll_resp:
                    if poll_resp.status != 200:
                        logger.warning(f"Gamma poll warning status {poll_resp.status}")
                        continue
                    poll_data = await poll_resp.json()
                    status = poll_data.get("status", "").lower()
                    logger.info(f"Gamma poll #{attempt+1}: status={status}")

                    if status == "completed":
                        result_data = poll_data
                        break
                    elif status in ("failed", "error"):
                        err_msg = poll_data.get("error", "Noma'lum xatolik")
                        return {
                            "success": False,
                            "error": f"Gamma generatsiyasi muvaffaqiyatsiz tugadi: {err_msg}"
                        }
                    else:
                        if status_callback and attempt % 3 == 0:
                            try:
                                await status_callback(f"✨ Gamma AI slaydlar va grafiklarni tayyorlamoqda... ({attempt * 4}s)")
                            except Exception:
                                pass
            except asyncio.CancelledError:
                raise
            except Exception as e:
                logger.warning(f"Gamma poll exception: {e}")

        if not result_data:
            return {
                "success": False,
                "error": "Gamma generatsiyasi kutilgan vaqtdan oshib ketdi (timeout)."
            }

        export_url = result_data.get("exportUrl")
        gamma_url = result_data.get("gammaUrl")
        gamma_id = result_data.get("gammaId")

        if not export_url:
            return {
                "success": False,
                "gamma_url": gamma_url,
                "error": "Taqdimot yaratildi, lekin yuklab olish havolasi (exportUrl) mavjud emas."
            }

        # 3. Download the PPTX / export file
        if status_callback:
            try:
                await status_callback("📥 Tayyor taqdimot fayli Gamma serveridan yuklab olinmoqda...")
            except Exception:
                pass

        try:
            async with session.get(export_url, timeout=aiohttp.ClientTimeout(total=60)) as file_resp:
                if file_resp.status == 200:
                    content_bytes = await file_resp.read()
                    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f".{export_as}")
                    tmp_file.write(content_bytes)
                    tmp_file.close()
                    logger.info(f"Gamma fayli muvaffaqiyatli yuklandi: {tmp_file.name} ({len(content_bytes)} bytes)")
                    return {
                        "success": True,
                        "file_path": tmp_file.name,
                        "gamma_url": gamma_url,
                        "gamma_id": gamma_id,
                        "generation_id": generation_id,
                        "error": None
                    }
                else:
                    return {
                        "success": False,
                        "gamma_url": gamma_url,
                        "error": f"Gamma eksport faylini yuklab bo'lmadi (HTTP {file_resp.status})"
                    }
        except Exception as e:
            return {
                "success": False,
                "gamma_url": gamma_url,
                "error": f"Faylni yuklab olishda xatolik: {e}"
            }
