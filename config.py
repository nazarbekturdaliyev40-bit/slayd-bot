import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GAMMA_API_KEY = os.getenv("GAMMA_API_KEY", "").strip()
ADMIN_ID = int(os.getenv("ADMIN_ID", "8597458619"))
CARD_NUMBER = os.getenv("CARD_NUMBER", "8600 0000 0000 0000")
CARD_HOLDER = os.getenv("CARD_HOLDER", "Karta egasi")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "").strip().lstrip("@")
PRICE_PER_SLIDE = os.getenv("PRICE_PER_SLIDE", "3 000 so'm")
PRICE_MONTHLY_SUBSCRIPTION = os.getenv("PRICE_MONTHLY_SUBSCRIPTION", "40 000 so'm")

# Cheksiz (Unlimited / VIP) huquqiga ega bo'lgan foydalanuvchilar
UNLIMITED_USERS = [8597458619, 6792644733, 8774376812]
extra_vips = os.getenv("VIP_USERS", "") or os.getenv("UNLIMITED_USERS", "")
if extra_vips:
    for v in extra_vips.split(","):
        v = v.strip()
        if v.isdigit() and int(v) not in UNLIMITED_USERS:
            UNLIMITED_USERS.append(int(v))

# Asosiy adminlar (Botni boshqarish, to'lovlar va buyruqlar huquqiga ega)
ADMIN_USERS = [ADMIN_ID]
if 6792644733 not in ADMIN_USERS:
    ADMIN_USERS.append(6792644733)

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_USERS or user_id == ADMIN_ID

def is_unlimited(user_id: int) -> bool:
    return user_id in UNLIMITED_USERS or user_id in ADMIN_USERS or user_id == ADMIN_ID

