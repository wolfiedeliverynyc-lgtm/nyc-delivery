import os
import time
import logging
import threading
from flask import Flask, render_template_string, request

import telebot
from config import Config, RESTAURANTS
from database import Database
from pricing import PricingEngine

# 1. إعداد التنبيهات والسيرفر
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

app = Flask(__name__)
# استخدم التوكن الذي أرسلته مباشرة لضمان العمل
TOKEN = "8336818567:AAFo-rCZ-LskakZEKfedVMvVkYNfER96wQs"
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")
db = Database(Config.DB_FILE)
pricing = PricingEngine()

# 2. واجهة لوحة التحكم (Dashboard)
DASH_HTML = """
<!DOCTYPE html>
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>لوحة تحكم NYC Delivery</title>
    <style>
        body { font-family: sans-serif; background: #0f172a; color: white; text-align: center; padding: 20px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 30px; }
        .card { background: #1e293b; padding: 20px; border-radius: 15px; border: 1px solid #38bdf8; }
        .btn { background: #38bdf8; color: #0f172a; padding: 10px 20px; text-decoration: none; border-radius: 8px; font-weight: bold; }
        h1 { color: #38bdf8; }
        .status { color: #4ade80; }
    </style>
</head>
<body>
    <h1>🗽 نظام توصيل NYC v5.2</h1>
    <p class="status">● حالة النظام: يعمل الآن بالتوكن الصحيح</p>
    
    <div class="grid">
        <div class="card"><h3>💰 الأرباح</h3><p>${{ stats.profit }}</p></div>
        <div class="card"><h3>📦 الطلبات</h3><p>{{ stats.completed }}</p></div>
        <div class="card"><h3>🚕 السائقين</h3><p>{{ stats.drivers_count }}</p></div>
    </div>

    <div style="margin-top: 50px;">
        <h3>🏠 المطاعم المتاحة:</h3>
        {% for slug, rest in restaurants.items() %}
            <p>{{ rest.logo }} {{ rest.name }} - <a href="/{{ slug }}" style="color:#38bdf8;">فتح الصفحة</a></p>
        {% endfor %}
    </div>
</body>
</html>
"""

# 3. مسارات الموقع
@app.route('/')
def home():
    data = db.load()
    stats = {
        "profit": round(data.get('profit', 0), 2),
        "completed": data.get('completed', 0),
        "drivers_count": len(data.get('drivers', {}))
    }
    return render_template_string(DASH_HTML, stats=stats, restaurants=RESTAURANTS)

@app.route('/<slug>')
def restaurant(slug):
    rest = RESTAURANTS.get(slug)
    if not rest: return "المطعم غير موجود", 404
    return f"<h1>Welcome to {rest['name']} {rest['logo']}</h1><p>الحد الأدنى للطلب: ${rest['min_order']}</p>"

# 4. أوامر البوت
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.first_name
    bot.reply_to(message, f"✅ <b>مرحباً {user_name}!</b>\n\nتم تفعيل البوت بنجاح على سيرفر Render.\nالنظام جاهز لاستقبال طلبات التوصيل.")

# 5. تشغيل البوت والسيرفر معاً
def start_polling():
    while True:
        try:
            bot.remove_webhook()
            bot.polling(none_stop=True, timeout=60)
        except Exception as e:
            log.error(f"خطأ في البوت: {e}")
            time.sleep(5)

if __name__ == '__main__':
    # تشغيل البوت في الخلفية
    threading.Thread(target=start_polling, daemon=True).start()
    # تشغيل السيرفر
    app.run(host='0.0.0.0', port=10000)
