import os
import time
import logging
import threading
from flask import Flask, request, jsonify, render_template_string
import telebot

# استيراد الملفات الأخرى (تأكد من وجودها في GitHub)
from config import Config, RESTAURANTS
from database import Database

# إعداد التنبيهات
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

# إعداد التطبيق والبوت
app = Flask(__name__)
bot = telebot.TeleBot(Config.BOT_TOKEN, parse_mode="HTML")
db = Database(Config.DB_FILE)

# ══════════════════════════════════════════════════════════════
# لوحة التحكم (Dashboard UI)
# ══════════════════════════════════════════════════════════════
DASHBOARD_HTML = """
<!DOCTYPE html>
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>لوحة التحكم | NYC Delivery</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, sans-serif; background: #0f172a; color: white; margin: 0; padding: 20px; }
        .container { max-width: 1000px; margin: auto; }
        .card { background: #1e293b; padding: 25px; border-radius: 15px; border: 1px solid #334155; margin-bottom: 20px; text-align: center; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }
        .stat-val { font-size: 32px; font-weight: bold; color: #38bdf8; }
        .status { display: inline-block; padding: 5px 15px; border-radius: 20px; background: #059669; font-size: 14px; }
        h1 { color: #f8fafc; }
        .rest-list { text-align: right; }
        .btn { background: #38bdf8; color: #0f172a; padding: 10px 20px; text-decoration: none; border-radius: 8px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h1>🗽 NYC Delivery System v5.2</h1>
            <div class="status">● النظام متصل ويعمل</div>
            <p>رابط الويب: <code>{{ web_url }}</code></p>
        </div>
        
        <div class="grid">
            <div class="card"><div class="stat-val">{{ stats.drivers }}</div><div>سائق نشط</div></div>
            <div class="card"><div class="stat-val">{{ stats.orders }}</div><div>إجمالي الطلبات</div></div>
            <div class="card"><div class="stat-val">${{ stats.profit }}</div><div>صافي الأرباح</div></div>
        </div>

        <div class="card rest-list">
            <h3>🏠 المطاعم المسجلة (White Label)</h3>
            <ul>
                {% for slug, rest in restaurants.items() %}
                <li><a href="/{{ slug }}" style="color: #38bdf8;">{{ rest.name }}</a> - الحد الأدنى: ${{ rest.min_order }}</li>
                {% endfor %}
            </ul>
            <p style="margin-top:20px;">🤖 البوت: <a href="https://t.me/NYC_Delivery_Bot" class="btn">افتح التليجرام</a></p>
        </div>
    </div>
</body>
</html>
"""

# ══════════════════════════════════════════════════════════════
# ROUTES (المسارات)
# ══════════════════════════════════════════════════════════════

@app.route('/')
def index():
    """عرض لوحة التحكم"""
    data = db.load()
    stats = {
        "drivers": len(data.get('drivers', {})),
        "orders": data.get('completed', 0),
        "profit": round(data.get('profit', 0.0), 2)
    }
    return render_template_string(DASHBOARD_HTML, stats=stats, restaurants=RESTAURANTS, web_url=Config.WEBHOOK_URL)

@app.route('/<slug>')
def restaurant_page(slug):
    """صفحة المطعم"""
    rest = RESTAURANTS.get(slug)
    if not rest:
        return f"المطعم {slug} غير موجود", 404
    return f"<h1>مرحباً بك في {rest['name']}</h1><p>سيتم تفعيل المنيو هنا قريباً.</p>"

# ══════════════════════════════════════════════════════════════
# BOT LOGIC (التعامل مع البوت)
# ══════════════════════════════════════════════════════════════

@bot.message_handler(commands=['start'])
def handle_start(message):
    welcome_text = (
        "🗽 <b>مرحباً بك في NYC Delivery!</b>\n\n"
        "✅ النظام يعمل بنجاح الآن.\n"
        "🚕 هذا البوت مخصص للسائقين لاستلام الطلبات.\n\n"
        "لوحة التحكم متوفرة الآن على الرابط الخاص بك."
    )
    bot.reply_to(message, welcome_text)

def run_bot_polling():
    """تشغيل البوت بنظام البحث المستمر"""
    while True:
        try:
            log.info("🔄 جاري الاتصال بتليجرام...")
            bot.remove_webhook()
            bot.infinity_polling(timeout=20, long_polling_timeout=5)
        except Exception as e:
            log.error(f"❌ خطأ في اتصال البوت: {e}")
            time.sleep(5)

# ══════════════════════════════════════════════════════════════
# START SERVER
# ══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    # تشغيل البوت في "خيط" منفصل (Thread)
    t = threading.Thread(target=run_bot_polling)
    t.daemon = True
    t.start()
    
    # تشغيل السيرفر
    log.info("🚀 تشغيل النظام v5.2...")
    app.run(host='0.0.0.0', port=10000)
