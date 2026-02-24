"""
config.py - الإعدادات المركزية
All configuration in one place
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """الإعدادات المركزية"""
    
    # ══════════════════════════════════════════════════════════
    # TELEGRAM
    # ══════════════════════════════════════════════════════════
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")
    DRIVER_CHANNEL_ID = int(os.getenv("DRIVER_CHANNEL_ID", "0"))
    REST_CHANNEL_ID = int(os.getenv("REST_CHANNEL_ID", "0"))
    ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
    
    # ══════════════════════════════════════════════════════════
    # WEB & DEPLOYMENT
    # ══════════════════════════════════════════════════════════
    WEBHOOK_URL = os.getenv("WEBHOOK_URL", "http://localhost:5000").rstrip("/")
    PORT = int(os.getenv("PORT", "5000"))
    
    # ══════════════════════════════════════════════════════════
    # MAPBOX
    # ══════════════════════════════════════════════════════════
    MAPBOX_TOKEN = os.getenv("MAPBOX_ACCESS_TOKEN", "")
    
    # ══════════════════════════════════════════════════════════
    # STRIPE
    # ══════════════════════════════════════════════════════════
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    CURRENCY = os.getenv("CURRENCY", "usd")
    
    # ══════════════════════════════════════════════════════════
    # TWILIO (SMS)
    # ══════════════════════════════════════════════════════════
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
    
    # ══════════════════════════════════════════════════════════
    # PLATFORM
    # ══════════════════════════════════════════════════════════
    PLATFORM_NAME = os.getenv("PLATFORM_NAME", "NYC Delivery")
    VERSION = "5.0"
    
    # ══════════════════════════════════════════════════════════
    # DATABASE
    # ══════════════════════════════════════════════════════════
    DB_FILE = "delivery_db.json"
    
    # ══════════════════════════════════════════════════════════
    # VALIDATION
    # ══════════════════════════════════════════════════════════
    
    @classmethod
    def validate(cls) -> bool:
        """التحقق من الإعدادات الضرورية"""
        required = {
            "BOT_TOKEN": cls.BOT_TOKEN,
            "DRIVER_CHANNEL_ID": cls.DRIVER_CHANNEL_ID,
            "REST_CHANNEL_ID": cls.REST_CHANNEL_ID,
            "MAPBOX_TOKEN": cls.MAPBOX_TOKEN,
        }
        
        missing = [k for k, v in required.items() if not v or v == "0"]
        
        if missing:
            print(f"❌ Missing required config: {', '.join(missing)}")
            print("💡 Check your .env file!")
            return False
        
        return True
    
    @classmethod
    def summary(cls) -> str:
        """ملخص الإعدادات"""
        return f"""
╔══════════════════════════════════════════════════════════╗
║  {cls.PLATFORM_NAME} v{cls.VERSION} - Configuration
╚══════════════════════════════════════════════════════════╝

✅ Telegram Bot:      {'Configured' if cls.BOT_TOKEN else '❌ Missing'}
✅ Mapbox:            {'Configured' if cls.MAPBOX_TOKEN else '❌ Missing'}
✅ Stripe:            {'Configured' if cls.STRIPE_SECRET_KEY else '⚠️  Optional'}
✅ Twilio SMS:        {'Configured' if cls.TWILIO_ACCOUNT_SID else '⚠️  Optional'}

🌐 Webhook URL:       {cls.WEBHOOK_URL}
🚀 Port:              {cls.PORT}
💾 Database:          {cls.DB_FILE}
"""


# ══════════════════════════════════════════════════════════════
# RESTAURANTS DATABASE
# ══════════════════════════════════════════════════════════════

RESTAURANTS = {
    "demo": {
        "name": "مطعم التجربة",
        "name_en": "Demo Restaurant",
        "address": "123 Main Street, Manhattan, NY 10001",
        "coords": [40.7128, -74.0060],  # [lat, lon]
        "logo": "🍕",
        "color": "#e74c3c",
        "description": "أشهى الوجبات في نيويورك",
        "min_order": 10.00,
        "menu": [
            {"id": 1, "name": "بيتزا مارغريتا", "price": 18.00, "emoji": "🍕", "cat": "بيتزا"},
            {"id": 2, "name": "بيتزا بيبروني", "price": 20.00, "emoji": "🍕", "cat": "بيتزا"},
            {"id": 3, "name": "برغر كلاسيك", "price": 15.00, "emoji": "🍔", "cat": "برغر"},
            {"id": 4, "name": "برغر جبن", "price": 17.00, "emoji": "🍔", "cat": "برغر"},
            {"id": 5, "name": "شاورما دجاج", "price": 14.00, "emoji": "🌯", "cat": "شاورما"},
            {"id": 6, "name": "شاورما لحم", "price": 16.00, "emoji": "🌯", "cat": "شاورما"},
            {"id": 7, "name": "سلطة سيزر", "price": 12.00, "emoji": "🥗", "cat": "سلطات"},
            {"id": 8, "name": "بطاطس مقلية", "price": 6.00, "emoji": "🍟", "cat": "إضافات"},
            {"id": 9, "name": "مشروب غازي", "price": 3.00, "emoji": "🥤", "cat": "مشروبات"},
            {"id": 10, "name": "عصير طبيعي", "price": 5.00, "emoji": "🍹", "cat": "مشروبات"},
        ],
    },
    
    # ─────────────────────────────────────────────────────────
    # أضف مطاعم جديدة هنا:
    # ─────────────────────────────────────────────────────────
    # "pizzanyc": {
    #     "name": "Pizza NYC",
    #     "coords": [40.7580, -73.9855],
    #     "logo": "🍕",
    #     "color": "#3498db",
    #     "min_order": 15.00,
    #     "menu": [...]
    # },
}
