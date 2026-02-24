"""
app.py - NYC Delivery System v5.1
الملف الرئيسي - Flask + Telegram Bot
"""

import os
import time
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Import our modules
from config import Config, RESTAURANTS
from database import Database
from mapbox_utils import MapboxUtils
from pricing import PricingEngine
from sms_service import SMSService

# ══════════════════════════════════════════════════════════════
# LOGGING
# ══════════════════════════════════════════════════════════════
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════
# VALIDATION
# ══════════════════════════════════════════════════════════════
if not Config.validate():
    log.error("❌ Configuration validation failed!")
    exit(1)

log.info(Config.summary())

# ══════════════════════════════════════════════════════════════
# INITIALIZATION
# ══════════════════════════════════════════════════════════════
app = Flask(__name__)
bot = telebot.TeleBot(Config.BOT_TOKEN, parse_mode="HTML")
db = Database(Config.DB_FILE)
mapbox = MapboxUtils(Config.MAPBOX_TOKEN)
pricing = PricingEngine()
sms = SMSService()

# Load database
data = db.load()

log.info(f"🚀 {Config.PLATFORM_NAME} v{Config.VERSION} - System ready!")

# ══════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════

def new_order_id():
    return f"NYC{int(time.time())}"

def timestamp():
    return datetime.now().strftime("%I:%M %p")

# ══════════════════════════════════════════════════════════════
# TELEGRAM BOT - COMMANDS
# ══════════════════════════════════════════════════════════════

@bot.message_handler(commands=['start'])
def cmd_start(msg):
    name = msg.from_user.first_name
    is_sub = db.is_driver_subscribed(data, name)
    
    text = f"""
🗽 <b>مرحباً {name}!</b>

<b>{Config.PLATFORM_NAME} v{Config.VERSION}</b>
نظام التوصيل الاحترافي

<b>📊 حالة حسابك:</b>
{'✅ مشترك' if is_sub else '❌ غير مشترك - /subscribe'}

<b>💰 نموذج الأجر:</b>
• Base: $3.50
• +$0.70 لكل كم
• +$0.10 لكل دقيقة

<b>مثال:</b> 3 كم / 15 دقيقة = <b>$7.10</b>

<b>🚀 ابدأ الآن:</b>
1. /subscribe ($30/شهر)
2. أرسل موقعك
3. استقبل الطلبات!
"""
    
    bot.send_message(msg.chat.id, text)


@bot.message_handler(commands=['subscribe'])
def cmd_subscribe(msg):
    name = msg.from_user.first_name
    uid = msg.from_user.id
    
    # تفعيل تجريبي (في الإنتاج: اربط مع Stripe)
    db.subscribe_driver(data, name, uid, days=30)
    data = db.load()
    
    bot.send_message(msg.chat.id,
        f"✅ <b>تم تفعيل اشتراكك!</b>\n"
        f"صالح لمدة 30 يوماً\n\n"
        f"🚀 جهّز نفسك للطلبات!")


@bot.message_handler(commands=['stats'])
def cmd_stats(msg):
    name = msg.from_user.first_name
    stats = data["stats"].get(name, {})
    
    if not stats or stats.get("completed", 0) == 0:
        bot.send_message(msg.chat.id,
            "📊 <b>لم تكمل أي طلبات بعد</b>\n\n"
            "ابدأ الآن! 🚀")
        return
    
    text = f"""
📊 <b>إحصائيات {name}</b>

✅ طلبات مكتملة: <b>{stats['completed']}</b>
💰 إجمالي الأرباح: <b>${stats['earned']:.2f}</b>
⭐ التقييم: <b>{stats['rating']:.1f}/5.0</b>
🚗 المسافة: <b>{stats['distance']:.1f} كم</b>
🏆 ترتيبك: <b>#{db.get_driver_rank(data, name)}</b>
"""
    
    bot.send_message(msg.chat.id, text)


@bot.message_handler(commands=['leaderboard'])
def cmd_leaderboard(msg):
    leaderboard = db.get_leaderboard(data, 10)
    
    if not leaderboard:
        bot.send_message(msg.chat.id, "لا توجد بيانات بعد")
        return
    
    medals = ["🥇", "🥈", "🥉"]
    text = "🏆 <b>متصدرو السائقين</b>\n\n"
    
    for i, (name, stats) in enumerate(leaderboard, 1):
        medal = medals[i-1] if i <= 3 else f"{i}."
        text += (
            f"{medal} <b>{name}</b>\n"
            f"   💰 ${stats['earned']:.2f} | "
            f"✅ {stats['completed']} | "
            f"⭐ {stats['rating']:.1f}\n\n"
        )
    
    bot.send_message(msg.chat.id, text)


@bot.message_handler(content_types=['location'])
def handle_location(msg):
    name = msg.from_user.first_name
    uid = msg.from_user.id
    lat = msg.location.latitude
    lon = msg.location.longitude
    
    db.set_driver_location(data, name, uid, f"{lat},{lon}")
    data = db.load()
    
    bot.send_message(msg.chat.id,
        f"✅ <b>تم تحديث موقعك</b>\n"
        f"📍 {lat:.4f}, {lon:.4f}\n"
        f"🕐 {timestamp()}")


# ══════════════════════════════════════════════════════════════
# FLASK - ROUTES
# ══════════════════════════════════════════════════════════════

@app.route('/')
def index():
    """Setup webhook and show status"""
    try:
        bot.remove_webhook()
        webhook_url = f"{Config.WEBHOOK_URL}/{Config.BOT_TOKEN}"
        bot.set_webhook(url=webhook_url)
        
        return jsonify({
            "status": f"✅ {Config.PLATFORM_NAME} v{Config.VERSION}",
            "webhook": webhook_url,
            "restaurants": list(RESTAURANTS.keys()),
            "dashboard": f"{Config.WEBHOOK_URL}/dashboard"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route(f'/{Config.BOT_TOKEN}', methods=['POST'])
def webhook():
    """Telegram webhook"""
    try:
        update = telebot.types.Update.de_json(request.get_data().decode('utf-8'))
        bot.process_new_updates([update])
        return "OK", 200
    except Exception as e:
        log.error(f"Webhook error: {e}")
        return "Error", 500


@app.route('/<slug>')
def restaurant_page(slug):
    """صفحة طلب المطعم - White Label"""
    rest = RESTAURANTS.get(slug)
    
    if not rest:
        return f"<h2>❌ Restaurant '{slug}' not found</h2>", 404
    
    # HTML template (simplified - in production use templates/)
    return f"""<!DOCTYPE html>
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>{rest['name']}</title>
    <style>
        body {{ font-family: Arial; max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: {rest['color']}; color: white; padding: 30px; text-align: center; border-radius: 10px; }}
        .menu {{ margin-top: 20px; }}
        .item {{ padding: 15px; border: 1px solid #ddd; margin: 10px 0; border-radius: 8px; cursor: pointer; }}
        .item:hover {{ background: #f5f5f5; }}
    </style>
</head>
<body>
    <div class="header">
        <div style="font-size: 60px;">{rest['logo']}</div>
        <h1>{rest['name']}</h1>
        <p>{rest.get('description', '')}</p>
    </div>
    
    <div class="menu">
        <h2>📋 المنيو</h2>
        <p>الحد الأدنى: ${rest['min_order']:.2f}</p>
        <!-- Menu items here -->
    </div>
    
    <div style="margin-top: 30px; padding: 20px; background: #f0f0f0; border-radius: 10px;">
        <p>🚧 <b>صفحة الطلب قيد الإنشاء</b></p>
        <p>سيتم إضافة نظام الطلب الكامل قريباً...</p>
    </div>
</body>
</html>"""


@app.route('/health')
def health():
    """Health check"""
    return jsonify({
        "status": "ok",
        "version": Config.VERSION,
        "time": datetime.now().isoformat()
    })


# ══════════════════════════════════════════════════════════════
# RUN
# ══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    log.info(f"🚀 Starting server on port {Config.PORT}...")
    app.run(host='0.0.0.0', port=Config.PORT, debug=False)
