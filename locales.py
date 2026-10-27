# -*- coding: utf-8 -*-
"""
Localization module for slayd_bot.
Supports bot interface in Uzbek, Russian, and English.
Supports presentation generation in 8 languages (Uzbek, Russian, English, Turkish, Kazakh, Kyrgyz, Tajik, German).
"""

# Available Bot Interface Languages
INTERFACE_LANGUAGES = {
    "uz": "🇺🇿 O'zbekcha",
    "ru": "🇷🇺 Русский",
    "en": "🇬🇧 English"
}

# Supported Presentation Languages (used in AI generation and PowerPoint layout)
SLIDE_LANGUAGES = {
    "uz": {
        "name": "🇺🇿 O'zbekcha",
        "prompt": "o'zbek tili (lotin alifbosidagi toza, imlo xatolarisiz akademik va tushunarli o'zbek tili)",
        "agenda": "Reja",
        "conclusion": "Xulosa",
        "thanks": "E'tiboringiz uchun rahmat!",
        "references": "Foydalanilgan adabiyotlar",
        "done_by": "Bajardi",
        "accepted_by": "Qabul qildi",
        "intro_speaker": "Hurmatli ustoz va talabalar, ushbu taqdimot mavzusi:",
        "ministry": "OʻZBEKISTON RESPUBLIKASI OLIY TAʼLIM, FAN VA INNOVATSIYALAR VAZIRLIGI",
        "work_title": "OLIY TAʼLIM MUASSASASI TALABASINING TAQDIMOT ISHI",
        "topic_label": "Mavzu",
        "uni_label": "OTM (Taʼlim muassasasi)",
        "faculty_label": "Fakultet (Kafedra)",
        "direction_label": "Taʼlim yoʻnalishi",
        "group_label": "Akademik guruh",
        "student_label": "Bajardi (Talaba)",
        "teacher_label": "Qabul qildi (Ilmiy rahbar)",
        "city_year": "Toshkent",
        "section_label": "BOʻLIM",
        "concl_title": "Xulosa va Yakun",
        "concl_and_refs": "Xulosa va Foydalanilgan manbalar",
        "main_conclusions": "✦  ASOSIY ILMIY-AMALIY XULOSALAR",
        "questions_welcome": "Savollar, fikr-mulohazalar va muhokama uchun tayyorman",
        "fallback_refs": [
            "Oʻzbekiston Respublikasi qonun hujjatlari va davlat taʼlim standartlari toʻplami.",
            "Mavzu yoʻnalishi boʻyicha oliy taʼlim darsliklari va oʻquv qoʻllanmalari toʻplami.",
            "Xalqaro va respublika nufuzli ilmiy jurnallari materiallari (Scopus, Google Scholar, OAK).",
            "Davlat va xalqaro ochiq ilmiy-axborot resurslari hamda elektron kutubxona bazalari."
        ]
    },
    "ru": {
        "name": "🇷🇺 Русский",
        "prompt": "русский язык (грамотный, академический и современный литературный русский язык)",
        "agenda": "План презентации",
        "conclusion": "Заключение",
        "thanks": "Спасибо за внимание!",
        "references": "Список использованной литературы",
        "done_by": "Выполнил(а)",
        "accepted_by": "Принял(а)",
        "intro_speaker": "Уважаемые преподаватели и студенты, тема презентации:",
        "ministry": "МИНИСТЕРСТВО ВЫСШЕГО ОБРАЗОВАНИЯ, НАУКИ И ИННОВАЦИЙ",
        "work_title": "ПРЕЗЕНТАЦИОННАЯ РАБОТА СТУДЕНТА ВУЗА",
        "topic_label": "Тема",
        "uni_label": "ВУЗ (Учебное заведение)",
        "faculty_label": "Факультет (Кафедра)",
        "direction_label": "Направление обучения",
        "group_label": "Академическая группа",
        "student_label": "Выполнил(а) (Студент)",
        "teacher_label": "Принял(а) (Научный руководитель)",
        "city_year": "Ташкент",
        "section_label": "РАЗДЕЛ",
        "concl_title": "Заключение и выводы",
        "concl_and_refs": "Заключение и список литературы",
        "main_conclusions": "✦  ОСНОВНЫЕ НАУЧНО-ПРАКТИЧЕСКИЕ ВЫВОДЫ",
        "questions_welcome": "Готов(а) ответить на ваши вопросы и замечания",
        "fallback_refs": [
            "Нормативно-правовые акты и государственные образовательные стандарты.",
            "Учебники и методические пособия для высших учебных заведений по данной специальности.",
            "Материалы рецензируемых научных журналов и баз данных (Scopus, Web of Science, РИНЦ).",
            "Электронно-библиотечные системы и открытые научные образовательные платформы."
        ]
    },
    "en": {
        "name": "🇬🇧 English",
        "prompt": "English language (formal, clear, academic and concise American/British English)",
        "agenda": "Agenda & Outline",
        "conclusion": "Conclusion",
        "thanks": "Thank You for Your Attention!",
        "references": "References & Bibliography",
        "done_by": "Prepared by",
        "accepted_by": "Supervised by",
        "intro_speaker": "Dear professors and students, today's presentation topic is:",
        "ministry": "MINISTRY OF HIGHER EDUCATION, SCIENCE AND INNOVATION",
        "work_title": "ACADEMIC STUDENT PRESENTATION PROJECT",
        "topic_label": "Topic",
        "uni_label": "University / Institution",
        "faculty_label": "Faculty / Department",
        "direction_label": "Field of Study",
        "group_label": "Academic Group",
        "student_label": "Prepared by (Student)",
        "teacher_label": "Supervised by (Advisor)",
        "city_year": "Academic Year",
        "section_label": "SECTION",
        "concl_title": "Conclusion & Summary",
        "concl_and_refs": "Conclusion & References",
        "main_conclusions": "✦  KEY FINDINGS & CONCLUSIONS",
        "questions_welcome": "Open for questions, comments and constructive discussion",
        "fallback_refs": [
            "Academic standards, regulatory framework, and educational guidelines.",
            "University textbooks, academic monographs, and specialized lecture materials.",
            "Peer-reviewed academic journals and research databases (Scopus, IEEE, Google Scholar).",
            "International open-access repositories and digital scientific libraries."
        ]
    },
    "tr": {
        "name": "🇹🇷 Türkçe",
        "prompt": "Türkçe (akademik, akıcı, zengin ve profesyonel Türkçe)",
        "agenda": "Sunum Planı / İçindekiler",
        "conclusion": "Sonuç ve Değerlendirme",
        "thanks": "Dikkatiniz için Teşekkür Ederim!",
        "references": "Kaynakça",
        "done_by": "Hazırlayan",
        "accepted_by": "Danışman",
        "intro_speaker": "Sayın hocalarım ve değerli arkadaşlar, bugünkü sunum konusu:",
        "ministry": "YÜKSEKÖĞRETİM, BİLİM VE YENİLİK BAKANLIĞI",
        "work_title": "ÜNİVERSİTE ÖĞRENCİSİ SUNUM ÇALIŞMASI",
        "topic_label": "Konu",
        "uni_label": "Üniversite (Eğitim Kurumu)",
        "faculty_label": "Fakülte (Bölüm)",
        "direction_label": "Öğretim Alanı",
        "group_label": "Akademik Grup",
        "student_label": "Hazırlayan (Öğrenci)",
        "teacher_label": "Danışman (Öğretim Üyesi)",
        "city_year": "Akademik Yıl",
        "section_label": "BÖLÜM",
        "concl_title": "Sonuç ve Değerlendirme",
        "concl_and_refs": "Sonuç ve Kaynakça",
        "main_conclusions": "✦  TEMEL BİLİMSEL VE UYGULAMALI SONUÇLAR",
        "questions_welcome": "Sorularınız ve katkılarınız için teşekkür ederim",
        "fallback_refs": [
            "Yükseköğretim mevzuatı ve ulusal akademik standartlar.",
            "İlgili alandaki temel üniversite ders kitapları ve bilimsel kaynaklar.",
            "Hakemli akademik dergiler ve uluslararası bilimsel veritabanları.",
            "Açık erişimli akademik kütüphane ve dijital bilgi kaynakları."
        ]
    },
    "kk": {
        "name": "🇰🇿 Қазақша",
        "prompt": "Қазақ тілі (академиялық, сауатты және әдеби қазақ тілі)",
        "agenda": "Жоспар",
        "conclusion": "Қорытынды",
        "thanks": "Назарларыңызға рақмет!",
        "references": "Пайдаланылған әдебиеттер тізімі",
        "done_by": "Орындаған",
        "accepted_by": "Тексерген",
        "intro_speaker": "Құрметті ұстаздар мен студенттер, бүгінгі тақырып:",
        "ministry": "ҒЫЛЫМ ЖӘНЕ ЖОҒАРЫ БІЛІМ МИНИСТРЛІГІ",
        "work_title": "ЖОҒАРЫ ОҚУ ОРНЫ СТУДЕНТІНІҢ ТҰСАУКЕСЕР ЖҰМЫСЫ",
        "topic_label": "Тақырып",
        "uni_label": "ЖОО (Оқу орны)",
        "faculty_label": "Факультет (Кафедра)",
        "direction_label": "Білім беру бағыты",
        "group_label": "Академиялық топ",
        "student_label": "Орындаған (Студент)",
        "teacher_label": "Тексерген (Ғылыми жетекші)",
        "city_year": "Астана",
        "section_label": "БӨЛІМ",
        "concl_title": "Қорытынды және Түйін",
        "concl_and_refs": "Қорытынды және пайдаланылған әдебиеттер",
        "main_conclusions": "✦  НЕГІЗГІ ҒЫЛЫМИ-ТӘЖІРИБЕЛІК ҚОРЫТЫНДЫЛАР",
        "questions_welcome": "Сұрақтар мен пікірлерге дайынмын",
        "fallback_refs": [
            "Мемлекеттік жалпыға міндетті білім беру стандарттары.",
            "Жоғары оқу орындарына арналған оқулықтар мен оқу құралдары.",
            "Ғылыми рецензияланатын журналдар мен халықаралық дерекқорлар.",
            "Электронды кітапханалық жүйелер мен ашық білім беру ресурстары."
        ]
    },
    "ky": {
        "name": "🇰🇬 Кыргызча",
        "prompt": "Кыргыз тили (академиялык, так жана адабий кыргыз тили)",
        "agenda": "План",
        "conclusion": "Корутунду",
        "thanks": "Көңүл бурганыңыздарга чоң рахмат!",
        "references": "Колдонулган адабияттар",
        "done_by": "Аткарган",
        "accepted_by": "Кабыл алган",
        "intro_speaker": "Урматтуу агай-эжейлер жана студенттер, презентациянын темасы:",
        "ministry": "БИЛИМ БЕРҮҮ ЖАНА ИЛИМ МИНИСТРЛИГИ",
        "work_title": "ЖОГОРКУ ОКУУ ЖАЙЫНЫН СТУДЕНТИНИН ПРЕЗЕНТАЦИЯЛЫК ИШИ",
        "topic_label": "Тема",
        "uni_label": "ЖОЖ (Окуу жайы)",
        "faculty_label": "Факультет (Кафедра)",
        "direction_label": "Билим берүү багыты",
        "group_label": "Академиялык топ",
        "student_label": "Аткарган (Студент)",
        "teacher_label": "Кабыл алган (Илимий жетекчи)",
        "city_year": "Бишкек",
        "section_label": "БӨЛҮМ",
        "concl_title": "Корутунду жана Жыйынтык",
        "concl_and_refs": "Корутунду жана адабияттар",
        "main_conclusions": "✦  НЕГИЗГИ ИЛИМИЙ-ПРАКТИКАЛЫК КОРУТУНДУЛАР",
        "questions_welcome": "Суроолор жана талкуу үчүн даярмын",
        "fallback_refs": [
            "Мамлекеттик билим берүү стандарттары жана нормативдик актылар.",
            "Жогорку окуу жайлары үчүн негизги окуу китептери жана колдонмолор.",
            "Илимий журналдар жана эл аралык маалымат базалары.",
            "Электрондук китепканалар жана ачык илимий ресурстар."
        ]
    },
    "tg": {
        "name": "🇹🇯 Тоҷикӣ",
        "prompt": "Забони тоҷикӣ (академикӣ, адабӣ ва фаҳмо)",
        "agenda": "Нақшаи презентатсия",
        "conclusion": "Хулоса",
        "thanks": "Барои таваҷҷӯҳатон ташаккур!",
        "references": "Адабиёти истифодашуда",
        "done_by": "Иҷро кард",
        "accepted_by": "Қабул кард",
        "intro_speaker": "Устодони мӯҳтарам ва донишҷӯён, мавзӯи имрӯза:",
        "ministry": "ВАЗОРАТИ МАОРИФ ВА ИЛМ",
        "work_title": "КОРИ ТАҚДИМОТИИ ДОНИШҶӮИ МУАССИСАИ ОЛӢ",
        "topic_label": "Мавзӯъ",
        "uni_label": "ДДО (Муассисаи таълимӣ)",
        "faculty_label": "Факултет (Кафедра)",
        "direction_label": "Самти таълим",
        "group_label": "Гурӯҳи академӣ",
        "student_label": "Иҷро кард (Донишҷӯ)",
        "teacher_label": "Қабул кард (Роҳбари илмӣ)",
        "city_year": "Душанбе",
        "section_label": "ҚИСМИ",
        "concl_title": "Хулоса ва Анҷом",
        "concl_and_refs": "Хулоса ва адабиёти истифодашуда",
        "main_conclusions": "✦  ХУЛОСАҲОИ АСОСИИ ИЛМИЮ АМАЛӢ",
        "questions_welcome": "Барои саволҳо ва муҳокима омодаам",
        "fallback_refs": [
            "Стандартҳои давлатии таҳсилот ва санадҳои меъёрии ҳуқуқӣ.",
            "Китобҳои дарсӣ ва дастурҳои таълимӣ барои муассисаҳои таҳсилоти олии касбӣ.",
            "Маҷаллаҳои илмӣ ва пойгоҳҳои иттилоотии байналмилалӣ.",
            "Китобхонаҳои электронӣ ва захираҳои кушодаи илмӣ."
        ]
    },
    "de": {
        "name": "🇩🇪 Deutsch",
        "prompt": "Deutsche Sprache (akademisches, professionelles Hochdeutsch)",
        "agenda": "Inhaltsverzeichnis / Agenda",
        "conclusion": "Fazit und Ausblick",
        "thanks": "Vielen Dank für Ihre Aufmerksamkeit!",
        "references": "Literaturverzeichnis",
        "done_by": "Vorgelegt von",
        "accepted_by": "Betreuer",
        "intro_speaker": "Sehr geehrte Professoren und Kommilitonen, das Thema der Präsentation lautet:",
        "ministry": "MINISTERIUM FÜR BILDUNG, WISSENSCHAFT UND FORSCHUNG",
        "work_title": "AKADEMISCHE PRÄSENTATIONSARBEIT",
        "topic_label": "Thema",
        "uni_label": "Hochschule / Universität",
        "faculty_label": "Fakultät (Fachbereich)",
        "direction_label": "Studiengang",
        "group_label": "Seminargruppe",
        "student_label": "Vorgelegt von (Student)",
        "teacher_label": "Betreuer (Dozent)",
        "city_year": "Akademisches Jahr",
        "section_label": "ABSCHNITT",
        "concl_title": "Fazit und Ausblick",
        "concl_and_refs": "Fazit und Literaturverzeichnis",
        "main_conclusions": "✦  WICHTIGSTE WISSENSCHAFTLICHE ERKENNTNISSE",
        "questions_welcome": "Bereit für Fragen, Anmerkungen und Diskussion",
        "fallback_refs": [
            "Akademische Richtlinien, Modulhandbücher und Studienordnungen.",
            "Wissenschaftliche Fach- und Lehrbücher für Hochschulen.",
            "Peer-Review-Fachzeitschriften und wissenschaftliche Datenbanken.",
            "Elektronische Bibliothekskataloge und akademische Online-Repositorien."
        ]
    }
}

# UI Translation dictionary
TEXTS = {
    "uz": {
        "choose_lang_title": "🌐 <b>Tilni tanlang / Выберите язык / Choose language:</b>",
        "lang_changed": "✅ <b>Interfeys tili O'zbekchaga o'zgartirildi!</b>",
        "menu_new_slide": "📊 Slayd tayyorlash",
        "menu_profile": "👤 Mening profilim",
        "menu_my_files": "📁 Mening fayllarim",
        "menu_free_limit": "🎁 Bepul limit",
        "menu_tariffs": "💳 Tariflar",
        "menu_about": "ℹ️ Bot haqida",
        "menu_contact": "👨‍💻 Adminga murojaat",
        "menu_change_lang": "🌐 Tilni o'zgartirish",
        "menu_admin": "⚙️ Admin panel",
        "menu_stats": "📈 Statistika",
        "menu_placeholder": "Mavzu yozing yoki menyudan tanlang...",
        "photo_to_slides_btn": "📊 Shu rasmdan taqdimot yasash",
        "doc_to_slides_btn": "📊 Hujjatdan taqdimot yasash",
        "welcome": (
            "Assalomu alaykum, <b>{name}</b>! 👋\n\n"
            "🤖 <b>Slide AI</b> — sun'iy intellekt (Google Gemini) yordamida professional taqdimotlar (<b>PowerPoint .pptx</b>) tayyorlovchi bot.\n\n"
            "✨ <b>Imkoniyatlar:</b>\n"
            "• 🌐 <b>Ko'p tilli slaydlar:</b> O'zbek, Rus, Ingliz va boshqa tillarda\n"
            "• 🎙 <b>Ovozli xabar:</b> Mavzuni audio tarzda aytsangiz, bot o'zi tushunib slayd tuzadi\n"
            "• 📚 <b>Konspekt va kitob:</b> Kitob beti yoki konspekt rasmini yuboring, bot slayd chiqarib beradi\n\n"
            "🎁 Sizda <b>{free_limit} ta bepul taqdimot</b> limiti mavjud!\n"
            "👥 Do'stlaringizni taklif qilib (har 2 ta do'st uchun <b>+1 ta limit</b>) bepul limit olishingiz mumkin.\n\n"
            "👇 Boshlash uchun <b>«📊 Slayd tayyorlash»</b> tugmasini bosing yoki toʻgʻridan-toʻgʻri ovoz/fayl yuboring:"
        ),
        "choose_slide_lang": "🌐 <b>Taqdimot qaysi tilda tayyorlansin?</b>\n\nQuyidagi kerakli tillardan birini tanlang: 👇",
        "prompt_topic": "✍️ <b>Taqdimot mavzusini yozib yuboring:</b>\n\n<i>Masalan: Sun'iy intellektning tibbiyotdagi o'rni va kelajagi</i>",
        "prompt_count": (
            "📌 Mavzu: <b>{topic}</b>\n"
            "🌐 Slayd tili: <b>{slide_lang}</b>\n\n"
            "📊 <b>Nechta slayd tayyorlansin?</b>\n"
            "Quyidagi tugmalardan birini tanlang yoki <b>oʻzingiz xohlagan sonni (5 dan 30 gacha)</b> yozib yuboring:\n"
            "<i>💡 Masalan: 7, 10, 12 yoki 15</i>"
        ),
        "prompt_author": (
            "✅ <b>{count} ta slayd</b> tanlandi!\n\n"
            "🎓 <b>1-slayd: Titul varaqasi uchun ma'lumotlar</b>\n"
            "<i>(OTM, fakultet, yoʻnalish, guruh, talaba va ilmiy rahbar)</i>\n\n"
            "Maʼlumotlarni tagma-tag yoki bir qatorda yozib yuborishingiz mumkin:\n"
            "💡 <i>Masalan:</i>\n"
            "OTM: TATU\n"
            "Fakultet: Dasturiy injiniring\n"
            "Guruh: 210-21\n"
            "Talaba: Nazarbek Turdaliyev\n"
            "O'qituvchi: Eshpolatov Ozodbek\n\n"
            "⏩ Agar maʼlumot kiritishni xohlamasangiz, <b>«O'tkazib yuborish»</b> tugmasini bosing:"
        ),
        "prompt_theme": (
            "🎨 <b>Slaydning orqa fonini (dizaynini) tanlang:</b>\n\n"
            "Oʻzingizga yoqqan orqa fon rangini tanlang yoki <b>oʻz fon rasmingizni</b> yuboring.\n"
            "Taqdimot aynan siz tanlagan fon asosida tayyorlanadi: 👇"
        ),
        "no_limit": (
            "⚠️ <b>Kechirasiz, sizda limitlar tugagan!</b>\n\n"
            "Siz yangi taqdimot yaratish uchun:\n"
            "1️⃣ <b>Limit yoki Oylik obuna xarid qilishingiz mumkin</b> (1 ta taqdimot — 3 000 so'm, oylik cheksiz — 40 000 so'm);\n"
            "2️⃣ <b>Do'stlaringizni taklif qiling</b> — har 2 ta yangi do'st uchun <b>+1 ta bepul limit</b> oling!"
        ),
        "confirm_title": (
            "📋 <b>Taqdimot tayyorlash ma'lumotlari:</b>\n\n"
            "📌 <b>Mavzu:</b> {topic}\n"
            "🌐 <b>Slayd tili:</b> {slide_lang}\n"
            "📊 <b>Slaydlar soni:</b> {count} ta slayd\n"
            "👤 <b>Muallif:</b> {author}\n"
            "🎨 <b>Dizayn foni:</b> {theme}\n\n"
            "🛠 <b>Slayd qanday tayyorlanadi:</b>\n"
            "1️⃣ <b>Akademik reja:</b> Mavzu chuqur tahlil qilinib, kirishdan xulosagacha tizimli reja tuziladi.\n"
            "2️⃣ <b>Mazmun va infografika:</b> Asosiy tushunchalar, taqqoslashlar va statistika yoziladi.\n"
            "3️⃣ <b>Vizual dizayn:</b> Mavzuga mos sifatli rasmlar va tanlangan fon uyg'unlashtiriladi.\n"
            "4️⃣ <b>Spiker nutqi:</b> Taqdimotchi himoyada nima deyishi kerakligi bo'yicha matn shakllantiriladi.\n"
            "5️⃣ <b>Formatlar:</b> PowerPoint (.pptx) va PDF (.pdf) ko'rinishida yuboriladi.\n\n"
            "⏳ <i>Taxminiy tayyorlanish vaqti: ~15-20 soniya</i>\n\n"
            "❓ <b>Slaydni tayyorlashni boshlaymizmi?</b>"
        ),
        "confirm_btn": "🚀 Ha, tayyorlansin",
        "cancel_btn": "❌ Bekor qilish",
        "cancelled": "❌ Amal bekor qilindi.",
        "skip_btn": "⏩ O'tkazib yuborish (Standart)",
        "share_btn": "↗️ Do'stlarga ulashish",
        "pptx_to_pdf_prompt": "📄 <b>PPTX faylingizni yuboring:</b>\n\nBot uni bir necha soniyada yuqori sifatli PDF formatga aylantirib beradi.",
        "image_to_pdf_prompt": "🖼 <b>PDF ga aylantirmoqchi boʻlgan rasmlarni yuboring:</b>\n\nBir yoki bir nechta rasm yuborishingiz mumkin.",
        "edit_in_powerpoint": "📊 PowerPoint-da tahrirlash (Online)",
        "get_pdf": "📄 PDF formatida olish",
        "speech_notes": "🎤 Himoya nutq matni",
        "bonus_limit": "🎁 Bepul limit olish (+1)",
        "profile_title": "👤 <b>Foydalanuvchi ma'lumotlari:</b>",
        "profile_id": "🆔 ID:",
        "profile_tariff": "👑 <b>Tarif:</b>",
        "profile_limit": "✨ <b>Mavjud limit:</b>",
        "profile_total": "📊 <b>Jami yaratilgan slaydlar:</b>",
        "profile_invited": "👥 <b>Taklif qilgan do'stlaringiz:</b>",
        "back_main_menu": "🔙 Asosiy menyu",
        "pay_card_btn": "💳 Karta raqami",
        "send_receipt_btn": "🧾 To'lov chekini yuborish",
        "contact_admin_btn": "👨‍💻 Adminga murojaat",
        "write_to_pm_btn": "💬 Adminga yozish",
        "contact_cancelled": "❌ Adminga murojaat bekor qilindi.",
        "referral_text": (
            "🎁 **Do'stlarni taklif qiling va bepul limit oling!**\n\n"
            "Har **2 ta do'stingiz** ushbu havola orqali botga kirsa, sizga **+1 ta yangi taqdimot yaratish limiti** sovg'a qilinadi!\n\n"
            "📊 **Sizning referal statistikangiz:**\n"
            "👥 Taklif qilingan do'stlar: **{invited_count} nafar**\n"
            "🎁 Olingan bonus limitlar: **{earned_limits} ta**\n"
            "⏳ Keyingi limit uchun kerak: **{needed_for_next} ta do'st**\n\n"
            "🔗 **Sizning shaxsiy referal havolangiz:**\n"
            "`{ref_link}`\n\n"
            "👇 *Quyidagi tugmani bosing va havolani do'stlaringizga yoki guruhlarga yuboring:*"
        ),
        "tariffs_vip": (
            "👑 **Sizning hisobingizda VIP (Cheksiz) ta'rif faol!**\n\n"
            "Sizga to'lov qilish yoki limit sotib olish talab etilmaydi. "
            "Hisobingizda doimiy **cheksiz taqdimotlar yaratish** imkoniyati yoqilgan.\n\n"
            "Marhamat, istalgancha slayd tayyorlashingiz mumkin."
        ),
        "tariffs_text": (
            "💳 **Tariflar va To'lov:**\n\n"
            "🎁 **2 ta bepul taqdimot** — har bir yangi foydalanuvchiga taqdim etiladi!\n\n"
            "2 ta bepul limitdan so'ng:\n"
            "1️⃣ **1 ta taqdimot** — **3 000 so'm**\n"
            "2️⃣ **3 ta taqdimot** — **8 000 so'm** (chegirma bilan)\n"
            "👑 **Oylik obuna (1 oy)** — **40 000 so'm** (1 oy davomida mutlaqo CHEKSIZ taqdimotlar yaratish! 🚀)\n\n"
            "📌 **To'lov qilish tartibi:**\n"
            "1. Quyidagi kartaga kerakli summani o'tkazing:\n"
            "💳 Karta raqami: `{card_number}`\n"
            "👤 Egasi: **{card_holder}**\n\n"
            "2. Pul o'tkazgach, pastdagi **'🧾 To'lov chekini yuborish'** tugmasini bosing va to'lov chekining rasmini (skrinshotini) botga yuboring.\n"
            "3. 5 daqiqa ichida admin chekni tasdiqlaydi va limitingiz avtomatik qo'shiladi!"
        ),
        "about_text": (
            "ℹ️ **Talabalar uchun Slayd & PDF Generator Bot haqida:**\n\n"
            "🎓 **OTM talablari boʻyicha taqdimotlar:**\n"
            "• Titul varaqasi (Universitet, fakultet, talaba va oʻqituvchi maʼlumotlari)\n"
            "• Taqdimot rejasi (Mundarija) va mazmuniy slaydlar\n"
            "• Xulosa va **Foydalanilgan adabiyotlar (manbalar)**\n"
            "• **Himoya nutq matni (doklad / shpargalka)** — darsda nima deb gapirishni toʻliq koʻrsatadi!\n\n"
            "🔹 **Formatlar:** Tahrirlash mumkin boʻlgan zamonaviy **PowerPoint (.pptx)** hamda **PDF**.\n"
            "🔹 **Ko'p tilli slaydlar:** O'zbek, Rus, Ingliz, Turk, Qozoq, Qirg'iz, Tojik, Nemis tillarida!\n"
            "🔹 **Tariflar:** 2 ta bepul taqdimot, so'ngra 1 ta taqdimot — 3 000 so'm, oylik cheksiz — 40 000 so'm.\n"
            "🔹 **Referal:** Har 2 ta do'st taklif qilsangiz, +1 ta bepul limit beriladi!\n\n"
            "Savol va takliflar uchun quyidagi tugma orqali adminga murojaat qilishingiz mumkin."
        ),
        "status_start": "🚀 Slayd tayyorlash boshlandi...",
        "status_plan": "🧠 1/4: Sun'iy intellekt akademik rejani tuzmoqda...",
        "status_images": "🖼 2/4: Mavzuga mos sifatli rasmlar tanlanmoqda...",
        "status_layout": "🎨 3/4: Slaydlar dizayni va infografikalar chizilmoqda...",
        "status_save": "💾 4/4: PowerPoint (.pptx) fayli saqlanmoqda...",
        "no_files_found": "📂 <b>Sizda hali saqlangan slaydlar mavjud emas.</b>\n\nYangi slayd yaratish uchun <b>«📊 Slayd tayyorlash»</b> tugmasini bosing yoki mavzuni toʻgʻridan-toʻgʻri chatga yozib yuboring!",
        "my_files_title": "📁 <b>Siz yaratgan slaydlar to'plami ({count} ta):</b>\n\nFayllar yuborilmoqda, bir oz kuting... ⏳",
        "my_files_done": "✅ <b>Barcha fayllaringiz muvaffaqiyatli yuborildi!</b>"
    },
    "ru": {
        "choose_lang_title": "🌐 <b>Выберите язык / Tilni tanlang / Choose language:</b>",
        "lang_changed": "✅ <b>Язык интерфейса изменен на Русский!</b>",
        "menu_new_slide": "📊 Создать слайды",
        "menu_profile": "👤 Мой профиль",
        "menu_my_files": "📁 Мои файлы",
        "menu_free_limit": "🎁 Бесплатные лимиты",
        "menu_tariffs": "💳 Тарифы",
        "menu_about": "ℹ️ О боте",
        "menu_contact": "👨‍💻 Связаться с админом",
        "menu_change_lang": "🌐 Сменить язык",
        "menu_admin": "⚙️ Админ панель",
        "menu_stats": "📈 Статистика",
        "menu_placeholder": "Введите тему или выберите действие...",
        "photo_to_slides_btn": "📊 Создать презентацию по фото",
        "doc_to_slides_btn": "📊 Создать презентацию из документа",
        "welcome": (
            "Здравствуйте, <b>{name}</b>! 👋\n\n"
            "🤖 <b>Slide AI</b> — создание профессиональных презентаций (<b>PowerPoint .pptx</b>) на базе искусственного интеллекта (Google Gemini).\n\n"
            "✨ <b>Возможности:</b>\n"
            "• 🌐 <b>Многоязычность:</b> Презентации на русском, узбекском, английском и других языках\n"
            "• 🎙 <b>Голосовые сообщения:</b> Назовите тему голосом, и бот составит презентацию\n"
            "• 📚 <b>По фото книги / конспекта:</b> Отправьте фото материала, и бот структурирует слайды\n\n"
            "🎁 У вас есть <b>{free_limit} бесплатных презентаций</b>!\n"
            "👥 Приглашайте друзей (за каждые 2 друга — <b>+1 бесплатный лимит</b>).\n\n"
            "👇 Нажмите <b>«📊 Создать слайды»</b> ниже или отправьте голосовое сообщение:"
        ),
        "choose_slide_lang": "🌐 <b>На каком языке подготовить презентацию?</b>\n\nВыберите нужный язык из списка ниже: 👇",
        "prompt_topic": "✍️ <b>Отправьте тему презентации:</b>\n\n<i>Например: Роль искусственного интеллекта в современной медицине</i>",
        "prompt_count": (
            "📌 Тема: <b>{topic}</b>\n"
            "🌐 Язык слайдов: <b>{slide_lang}</b>\n\n"
            "📊 <b>Сколько слайдов подготовить?</b>\n"
            "Выберите вариант ниже или отправьте число (от 5 до 30):\n"
            "<i>💡 Например: 7, 10, 12 или 15</i>"
        ),
        "prompt_author": (
            "✅ Выбрано: <b>{count} слайдов</b>!\n\n"
            "🎓 <b>1-й слайд: Данные титульного листа</b>\n"
            "<i>(ВУЗ, факультет, направление, группа, студент и преподаватель)</i>\n\n"
            "Вы можете отправить данные одной строкой или списком:\n"
            "💡 <i>Например:</i>\n"
            "ВУЗ: МГУ\n"
            "Факультет: ВМК\n"
            "Группа: 201\n"
            "Студент: Иван Иванов\n"
            "Преподаватель: Петров П.С.\n\n"
            "⏩ Если титульный лист не нужен, нажмите <b>«Пропустить»</b>:"
        ),
        "prompt_theme": (
            "🎨 <b>Выберите стиль / фон презентации:</b>\n\n"
            "Выберите цвет фона из предложенных или отправьте **свое фоновое изображение**: 👇"
        ),
        "no_limit": (
            "⚠️ <b>К сожалению, ваши лимиты закончились!</b>\n\n"
            "Чтобы создать новую презентацию:\n"
            "1️⃣ <b>Приобретите лимиты или подписку</b> (1 презентация — 3 000 сум, безлимит на месяц — 40 000 сум);\n"
            "2️⃣ <b>Пригласите друзей</b> — получайте <b>+1 лимит</b> за каждые 2 приглашенных друга!"
        ),
        "confirm_title": (
            "📋 <b>Параметры создания презентации:</b>\n\n"
            "📌 <b>Тема:</b> {topic}\n"
            "🌐 <b>Язык слайдов:</b> {slide_lang}\n"
            "📊 <b>Количество слайдов:</b> {count}\n"
            "👤 <b>Автор:</b> {author}\n"
            "🎨 <b>Тема оформления:</b> {theme}\n\n"
            "🛠 <b>Как будет создана презентация:</b>\n"
            "1️⃣ <b>Академический план:</b> Анализ темы и составление структуры от введения до заключения.\n"
            "2️⃣ <b>Контент и инфографика:</b> Ключевые тезисы, сравнения и статистика.\n"
            "3️⃣ <b>Визуальный дизайн:</b> Качественные тематические изображения и оформление.\n"
            "4️⃣ <b>Речь спикера:</b> Текст для защиты презентации (заметки докладчика).\n"
            "5️⃣ <b>Форматы:</b> Презентация в форматах PowerPoint (.pptx) и PDF (.pdf).\n\n"
            "⏳ <i>Примерное время: ~15-20 секунд</i>\n\n"
            "❓ <b>Начать создание слайдов?</b>"
        ),
        "confirm_btn": "🚀 Да, создать",
        "cancel_btn": "❌ Отмена",
        "cancelled": "❌ Действие отменено.",
        "skip_btn": "⏩ Пропустить (Стандарт)",
        "share_btn": "↗️ Поделиться с друзьями",
        "pptx_to_pdf_prompt": "📄 <b>Отправьте PPTX файл:</b>\n\nБот мгновенно конвертирует его в качественный PDF документ.",
        "image_to_pdf_prompt": "🖼 <b>Отправьте фотографии для конвертации в PDF:</b>\n\nВы можете отправить одно или несколько фото.",
        "edit_in_powerpoint": "📊 Редактировать в PowerPoint (Online)",
        "get_pdf": "📄 Скачать в PDF",
        "speech_notes": "🎤 Текст речи для защиты",
        "bonus_limit": "🎁 Получить бесплатный лимит (+1)",
        "profile_title": "👤 <b>Информация профиля:</b>",
        "profile_id": "🆔 ID:",
        "profile_tariff": "👑 <b>Тариф:</b>",
        "profile_limit": "✨ <b>Доступный лимит:</b>",
        "profile_total": "📊 <b>Всего создано слайдов:</b>",
        "profile_invited": "👥 <b>Приглашено друзей:</b>",
        "back_main_menu": "🔙 Главное меню",
        "pay_card_btn": "💳 Номер карты",
        "send_receipt_btn": "🧾 Отправить чек оплаты",
        "contact_admin_btn": "👨‍💻 Связаться с админом",
        "write_to_pm_btn": "💬 Написать админу",
        "contact_cancelled": "❌ Обращение к администратору отменено.",
        "referral_text": (
            "🎁 **Приглашайте друзей и получайте бесплатные лимиты!**\n\n"
            "Каждые **2 друга**, которые перейдут по вашей ссылке и запустят бота, принесут вам **+1 бесплатный лимит на создание презентации**!\n\n"
            "📊 **Ваша реферальная статистика:**\n"
            "👥 Приглашено друзей: **{invited_count} чел.**\n"
            "🎁 Получено бонусных лимитов: **{earned_limits} шт.**\n"
            "⏳ Нужно до следующего бонуса: **{needed_for_next} чел.**\n\n"
            "🔗 **Ваша персональная реферальная ссылка:**\n"
            "`{ref_link}`\n\n"
            "👇 *Нажмите кнопку ниже, чтобы переслать ссылку друзьям или в группы:*"
        ),
        "tariffs_vip": (
            "👑 **Для вашего аккаунта активен тариф VIP (Безлимит)!**\n\n"
            "Вам не требуется покупать лимиты или подписку. "
            "На вашем аккаунте включен постоянный **безлимитный доступ** к созданию презентаций.\n\n"
            "Вы можете создавать неограниченное количество слайдов."
        ),
        "tariffs_text": (
            "💳 **Тарифы и Оплата:**\n\n"
            "🎁 **2 бесплатные презентации** — даются каждому пользователю при старте!\n\n"
            "После расходования 2 бесплатных лимитов:\n"
            "1️⃣ **1 презентация** — **3 000 сум**\n"
            "2️⃣ **3 презентации** — **8 000 сум** (со скидкой)\n"
            "👑 **Месячная подписка** — **40 000 сум** (1 месяц полных БЕЗЛИМИТНЫХ презентаций! 🚀)\n\n"
            "📌 **Как оплатить:**\n"
            "1. Переведите нужную сумму на карту:\n"
            "💳 Номер карты: `{card_number}`\n"
            "👤 Получатель: **{card_holder}**\n\n"
            "2. После перевода нажмите кнопку **'🧾 Отправить чек оплаты'** ниже и отправьте скриншот чека.\n"
            "3. Администратор подтвердит чек в течение 5 минут, и лимиты будут начислены автоматически!"
        ),
        "about_text": (
            "ℹ️ **О боте Slide & PDF Generator для студентов:**\n\n"
            "🎓 **Создание презентаций по академическим стандартам:**\n"
            "• Титульный лист (ВУЗ, факультет, группа, студент и преподаватель)\n"
            "• План презентации (содержание) и структурированные слайды\n"
            "• Заключение и **список литературы (источников)**\n"
            "• **Речь для защиты (доклад / шпаргалка)** — готовый текст того, что говорить во время защиты!\n\n"
            "🔹 **Форматы:** Редактируемый **PowerPoint (.pptx)** и документ **PDF**.\n"
            "🔹 **Многоязычность:** Русский, Узбекский, Английский, Турецкий, Казахский, Кыргызский, Таджикский, Немецкий.\n"
            "🔹 **Тарифы:** 2 бесплатные презентации при старте, затем 1 презентация — 3 000 сум, безлимит на месяц — 40 000 сум.\n"
            "🔹 **Рефералы:** За каждые 2 приглашенных друга — **+1 бесплатный лимит**!\n\n"
            "По всем вопросам и предложениям обращайтесь к администратору."
        ),
        "status_start": "🚀 Начинаем подготовку презентации...",
        "status_plan": "🧠 1/4: ИИ составляет академический план и структуру...",
        "status_images": "🖼 2/4: Подбираются качественные тематические изображения...",
        "status_layout": "🎨 3/4: Оформляется дизайн, инфографика и карточки...",
        "status_save": "💾 4/4: Сохраняется файл PowerPoint (.pptx)...",
        "no_files_found": "📂 <b>У вас пока нет сохраненных презентаций.</b>\n\nЧтобы создать слайды, нажмите <b>«📊 Создать слайды»</b> или отправьте тему напрямую в чат!",
        "my_files_title": "📁 <b>Ваши созданные презентации ({count} шт.):</b>\n\nОтправляем файлы, подождите немного... ⏳",
        "my_files_done": "✅ <b>Все ваши файлы успешно отправлены!</b>"
    },
    "en": {
        "choose_lang_title": "🌐 <b>Choose language / Tilni tanlang / Выберите язык:</b>",
        "lang_changed": "✅ <b>Interface language changed to English!</b>",
        "menu_new_slide": "📊 Create Slides",
        "menu_profile": "👤 My Profile",
        "menu_my_files": "📁 My Files",
        "menu_free_limit": "🎁 Free Limits",
        "menu_tariffs": "💳 Plans & Pricing",
        "menu_about": "ℹ️ About Bot",
        "menu_contact": "👨‍💻 Contact Admin",
        "menu_change_lang": "🌐 Change Language",
        "menu_admin": "⚙️ Admin Panel",
        "menu_stats": "📈 Statistics",
        "menu_placeholder": "Type topic or choose from menu...",
        "photo_to_slides_btn": "📊 Create Presentation from Photo",
        "doc_to_slides_btn": "📊 Create Presentation from Document",
        "welcome": (
            "Hello, <b>{name}</b>! 👋\n\n"
            "🤖 <b>Slide AI</b> — professional presentation (<b>PowerPoint .pptx</b>) generator powered by Artificial Intelligence (Google Gemini).\n\n"
            "✨ <b>Features:</b>\n"
            "• 🌐 <b>Multi-language:</b> Generate slides in English, Russian, Uzbek and other languages\n"
            "• 🎙 <b>Voice Input:</b> Speak your topic in an audio note, and AI creates the slides\n"
            "• 📚 <b>From Notes & Books:</b> Send photos of study materials to extract presentations\n\n"
            "🎁 You have <b>{free_limit} free presentations</b>!\n"
            "👥 Invite friends (get <b>+1 free presentation</b> for every 2 friends).\n\n"
            "👇 Tap <b>«📊 Create Slides»</b> below or send an audio note to get started:"
        ),
        "choose_slide_lang": "🌐 <b>What language should the presentation be in?</b>\n\nPlease select the desired language below: 👇",
        "prompt_topic": "✍️ <b>Send your presentation topic:</b>\n\n<i>Example: The Role and Future of Artificial Intelligence in Medicine</i>",
        "prompt_count": (
            "📌 Topic: <b>{topic}</b>\n"
            "🌐 Slide Language: <b>{slide_lang}</b>\n\n"
            "📊 <b>How many slides should be generated?</b>\n"
            "Select an option below or type a custom number (5 to 30):\n"
            "<i>💡 Example: 7, 10, 12 or 15</i>"
        ),
        "prompt_author": (
            "✅ <b>{count} slides</b> selected!\n\n"
            "🎓 <b>Slide 1: Title Card Details</b>\n"
            "<i>(University, faculty, department, student name, and professor)</i>\n\n"
            "You can send the details line by line:\n"
            "💡 <i>Example:</i>\n"
            "University: Oxford\n"
            "Faculty: Computer Science\n"
            "Student: John Doe\n"
            "Professor: Dr. Smith\n\n"
            "⏩ If you don't need title details, click <b>«Skip»</b>:"
        ),
        "prompt_theme": (
            "🎨 <b>Choose presentation theme & background:</b>\n\n"
            "Select your preferred color scheme or send **your custom background image**: 👇"
        ),
        "no_limit": (
            "⚠️ <b>Sorry, you have run out of presentation limits!</b>\n\n"
            "To generate new presentations:\n"
            "1️⃣ <b>Purchase limits or monthly subscription</b> (1 presentation — 3,000 UZS, unlimited month — 40,000 UZS);\n"
            "2️⃣ <b>Invite friends</b> — get <b>+1 free limit</b> for every 2 friends who join!"
        ),
        "confirm_title": (
            "📋 <b>Presentation Details:</b>\n\n"
            "📌 <b>Topic:</b> {topic}\n"
            "🌐 <b>Slide Language:</b> {slide_lang}\n"
            "📊 <b>Slide Count:</b> {count} slides\n"
            "👤 <b>Author:</b> {author}\n"
            "🎨 <b>Design Theme:</b> {theme}\n\n"
            "🛠 <b>How your presentation will be prepared:</b>\n"
            "1️⃣ <b>Academic Outline:</b> In-depth topic analysis and structured agenda.\n"
            "2️⃣ <b>Content & Infographics:</b> Key insights, bullet points, and comparisons.\n"
            "3️⃣ <b>Visual Design:</b> High-resolution contextual images and chosen styling.\n"
            "4️⃣ <b>Speaker Notes:</b> Ready-to-read speech script for your presentation defense.\n"
            "5️⃣ <b>Deliverables:</b> Delivered in PowerPoint (.pptx) and PDF (.pdf).\n\n"
            "⏳ <i>Estimated time: ~15-20 seconds</i>\n\n"
            "❓ <b>Ready to generate your presentation?</b>"
        ),
        "confirm_btn": "🚀 Yes, generate",
        "cancel_btn": "❌ Cancel",
        "cancelled": "❌ Action cancelled.",
        "skip_btn": "⏩ Skip (Default)",
        "share_btn": "↗️ Share with friends",
        "pptx_to_pdf_prompt": "📄 <b>Send your PPTX file:</b>\n\nThe bot will quickly convert it to a high-quality PDF document.",
        "image_to_pdf_prompt": "🖼 <b>Send photos to convert to PDF:</b>\n\nYou can send one or multiple pictures.",
        "edit_in_powerpoint": "📊 Edit in PowerPoint (Online)",
        "get_pdf": "📄 Download as PDF",
        "speech_notes": "🎤 Speaker Defence Script",
        "bonus_limit": "🎁 Get free limit (+1)",
        "profile_title": "👤 <b>Profile Details:</b>",
        "profile_id": "🆔 ID:",
        "profile_tariff": "👑 <b>Plan:</b>",
        "profile_limit": "✨ <b>Available limit:</b>",
        "profile_total": "📊 <b>Total slides created:</b>",
        "profile_invited": "👥 <b>Invited friends:</b>",
        "back_main_menu": "🔙 Main Menu",
        "pay_card_btn": "💳 Card Number",
        "send_receipt_btn": "🧾 Submit Receipt",
        "contact_admin_btn": "👨‍💻 Contact Admin",
        "write_to_pm_btn": "💬 Message Admin",
        "contact_cancelled": "❌ Contacting administrator cancelled.",
        "referral_text": (
            "🎁 **Invite friends and get free presentations!**\n\n"
            "Every **2 friends** who start the bot via your referral link will reward you with **+1 free presentation limit**!\n\n"
            "📊 **Your Referral Statistics:**\n"
            "👥 Invited friends: **{invited_count}**\n"
            "🎁 Earned bonus limits: **{earned_limits}**\n"
            "⏳ Needed for next bonus: **{needed_for_next} friends**\n\n"
            "🔗 **Your personal referral link:**\n"
            "`{ref_link}`\n\n"
            "👇 *Click the button below to share your link with friends or group chats:*"
        ),
        "tariffs_vip": (
            "👑 **VIP (Unlimited) Plan is active on your account!**\n\n"
            "No payments or limit purchases are required. "
            "Permanent **unlimited presentation creation** is enabled for you.\n\n"
            "Feel free to create as many presentations as you need."
        ),
        "tariffs_text": (
            "💳 **Plans & Payment:**\n\n"
            "🎁 **2 free presentations** for every new user!\n\n"
            "After your free limits:\n"
            "1️⃣ **1 presentation** — **3,000 UZS**\n"
            "2️⃣ **3 presentations** — **8,000 UZS** (discounted)\n"
            "👑 **Monthly Unlimited** — **40,000 UZS** (unlimited presentations for 30 days! 🚀)\n\n"
            "📌 **How to pay:**\n"
            "1. Transfer the amount to the card:\n"
            "💳 Card Number: `{card_number}`\n"
            "👤 Recipient: **{card_holder}**\n\n"
            "2. After payment, click **'🧾 Submit Receipt'** below and send a screenshot of the receipt.\n"
            "3. The admin will verify within 5 minutes and limits will be activated automatically!"
        ),
        "about_text": (
            "ℹ️ **About Slide & PDF Generator Bot:**\n\n"
            "🎓 **Academic presentations compliant with university standards:**\n"
            "• Title slide (University, faculty, student name, and supervisor)\n"
            "• Agenda outline and informative content slides\n"
            "• Conclusion and **academic references/bibliography**\n"
            "• **Speaker Defence Script** — full script of what to say while presenting!\n\n"
            "🔹 **Formats:** Editable **PowerPoint (.pptx)** and high quality **PDF**.\n"
            "🔹 **Multi-language:** English, Russian, Uzbek, Turkish, Kazakh, Kyrgyz, Tajik, German.\n"
            "🔹 **Plans:** 2 free presentations, then 1 presentation — 3,000 UZS, unlimited monthly — 40,000 UZS.\n"
            "🔹 **Referral:** Invite friends (+1 free limit for every 2 friends)!\n\n"
            "For inquiries and support, feel free to contact the administrator."
        ),
        "status_start": "🚀 Starting presentation preparation...",
        "status_plan": "🧠 1/4: AI is composing academic structure and agenda...",
        "status_images": "🖼 2/4: Selecting matching high-resolution imagery...",
        "status_layout": "🎨 3/4: Rendering infographic cards and layout...",
        "status_save": "💾 4/4: Saving PowerPoint (.pptx) presentation...",
        "no_files_found": "📂 <b>You don't have any saved presentations yet.</b>\n\nTo create slides, click <b>«📊 Create Slides»</b> or send your topic directly in chat!",
        "my_files_title": "📁 <b>Your generated presentations ({count}):</b>\n\nSending files, please wait... ⏳",
        "my_files_done": "✅ <b>All your files have been successfully sent!</b>"
    }
}

def get_text(key: str, lang: str = "uz", **kwargs) -> str:
    """Returns localized string, falling back to Uzbek if not found."""
    if lang not in TEXTS:
        lang = "uz"
    template = TEXTS[lang].get(key, TEXTS["uz"].get(key, key))
    if kwargs:
        try:
            return template.format(**kwargs)
        except Exception:
            return template
    return template

def get_slide_lang_info(lang_code: str) -> dict:
    """Returns presentation language settings, falling back to Uzbek."""
    return SLIDE_LANGUAGES.get(lang_code, SLIDE_LANGUAGES["uz"])
