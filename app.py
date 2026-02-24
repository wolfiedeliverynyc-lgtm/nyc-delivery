"""
app.py - NYC Delivery System v5.2
تحديث: إصلاح البوت + إضافة لوحة التحكم
"""

import os
import time
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# استيراد الموديلات (تأكد من وجود الملفات الأخرى في مشروعك)
from config import Config, RESTAURANTS
from database import Database
from mapbox_utils import MapboxUtils
from pricing import PricingEngine

# الإعدادات الأساسية
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

app = Flask(__name__)
bot = telebot.TeleBot(Config.BOT_TOKEN, parse_mode="HTML")
db = Database(Config.DB_FILE)
data = db.load()

# ══════════════════════════════════════════════════════════════
# لوحة التحكم (DASHBOARD HTML)
# ══════════════════════════════════════════════════════════════
DASHBOARD_HTML = """
<!DOCTYPE html>
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>لوحة التحكم | NYC Delivery</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f4f7f6; margin: 0; padding: 20px; }
        .container { max-width: 900px; margin: auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
        .header { border-bottom: 2px solid #eee; padding-bottom: 20px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }
        .stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
        .stat-card { background: #eef2f3; padding: 20px; border-radius: 10px; text-align: center; }
        .stat-card h3 { margin: 0; color: #555; font-size: 14px; }
        .stat-card p { font-size: 24px; font-weight: bold; margin: 10px 0; color: #2c3e50; }
        .status-ok { color: #27ae60; font-weight: bold; }
        .btn { background: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🗽 لوحة تحكم NYC Delivery</h1>
            <span class="status-ok">● النظام يعمل</span>
        </div>
        <div class="stats-grid">
            <div class="stat-card"><h3>إجمالي الطلبات</h3><p>{{ stats.total_orders }}</p></div>
            <div class="stat-card"><h3>السائقين النشطين</h3><p>{{ stats.active_drivers }}</p></div>
            <div class="stat-card"><h3>إجمالي الأرباح</h3><p>${{ stats.total_earned }}</p></div>
        </div>
        <div style="margin-top:30px;">
            <h3>🔗 روابط سريعة</h3>
            <p>رابط البوت: <a href="https://t.me/{{ bot_username }}">@{{ bot_username }}</a></p>
            <p>رابط الموقع: <code>{{ web_url }}</code></p>
        </div>
    </div>
</body>
</html>
"""

# ══════════════════════════════════════════════════════════════
# ROUTES
# ══════════════════════════════════════════════════════════════

@app.route('/')
def home():
    """تفعيل البوت تلقائياً وعرض إحصائيات بسيطة"""
    try:
        # إعادة ضبط الـ Webhook عند كل زيارة للصفحة الرئيسية للتأكد من عمله
        webhook_url = f"{Config.WEBHOOK_URL}/{Config.BOT_TOKEN}"
        bot.remove_webhook()
        time.sleep(0.1)
        bot.set_webhook(url=webhook_url)
        
        # تجهيز بيانات لوحة التحكم
        stats = {
            "total_orders": sum(d.get('completed', 0) for d in data.get('stats', {}).values()),
            "active_drivers": len(data.get('drivers', {})),
            "total_earned": round(sum(d.get('earned', 0) for d in data.get('stats', {}).values()), 2)
        }
        
        return render_template_string(DASHBOARD_HTML, 
                                    stats=stats, 
                                    bot_username=bot.get_me().username,
                                    web_url=Config.WEBHOOK_URL)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route(f'/{Config.BOT_TOKEN}', methods=['POST'])
def telegram_webhook():
    """استقبال رسائل تليجرام"""
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    else:
        return jsonify({"error": "Unauthorized"}), 403

# مسارات البوت الأساسية
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🗽 <b>مرحباً بك في نظام NYC Delivery!</b>\nالبوت يعمل الآن بنجاح ✅")

@app.route('/<slug>')
def restaurant_page(slug):
    rest = RESTAURANTS.get(slug)
    if not rest: return f"Restaurant {slug} not found", 404
    return f"<h1>Welcome to {rest['name']}</h1>" # (يمكنك وضع كود HTML المطعم هنا)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
# --- استبدل الجزء الأخير من ملف app.py بهذا الكود المطور ---

def start_bot():
    """تشغيل البوت في خلفية السيرفر لتجنب تعليق الموقع"""
    while True:
        try:
            log.info("🔄 جاري محاولة تشغيل البوت بنظام Polling...")
            bot.remove_webhook() # حذف أي ربط قديم معطل
            time.sleep(1)
            bot.infinity_polling(timeout=20, long_polling_timeout=5)
        except Exception as e:
            log.error(f"❌ خطأ في البوت: {e}")
            time.sleep(5) # الانتظار قبل إعادة المحاولة

if __name__ == '__main__':
    # تشغيل البوت في Thread منفصل حتى لا يتوقف الموقع
    import threading
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # تشغيل سيرفر الويب (لوحة التحكم والمطاعم)
    log.info("🚀 تشغيل سيرفر الويب على المنفذ 10000")
    app.run(host='0.0.0.0', port=10000)
