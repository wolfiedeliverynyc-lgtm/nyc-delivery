"""
app.py - الملف الرئيسي لنظام توصيل NYC v5.2
تجميع كامل: Bot + Flask + Database + Pricing
"""

import os
import time
import logging
import threading
from flask import Flask, render_template_string, request, jsonify

import telebot
from telebot import types

# استيراد الملفات التي رفعتها (تأكد أنها في نفس المجلد)
from config import Config, RESTAURANTS
from database import Database
from pricing import PricingEngine

# ══════════════════════════════════════════════════════════════
# 1. الإعدادات والربط
# ══════════════════════════════════════════════════════════════
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# التوكن الصحيح الخاص بك
TOKEN = "8336818567:AAFo-rCZ-LskakZEKfedVMvVkYNfER96wQs"
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# تهيئة المحركات
db = Database(Config.DB_FILE)
pricing = PricingEngine()

# ══════════════════════════════════════════════════════════════
# 2. واجهة لوحة التحكم (DASHBOARD)
# ══════════════════════════════════════════════════════════════
DASH_HTML = """
<!DOCTYPE html>
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>لوحة تحكم NYC Delivery</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }
        .container { max-width: 1000px; margin: auto; }
        .header { background: #1e293b; padding: 20px; border-radius: 15px; border-bottom: 4px solid #38bdf8; margin-bottom: 20px; text-align: center; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
        .stat-card { background: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155; text-align: center; }
        .stat-val { font-size: 28px; font-weight: bold; color: #38bdf8; display: block; }
        .stat-label { font-size: 14px; color: #94a3b8; }
        .rest-card { background: #1e293b; padding: 15px; border-radius: 10px; margin-top: 10px; display: flex; justify-content: space-between; align-items: center; border: 1px solid #334155; }
        .btn { background: #38bdf8; color: #0f172a; padding: 8px 15px; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 14px; }
        .status-tag { background: #059669; color: white; padding: 4px 10px; border-radius: 20px; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🗽 NYC Delivery System v5.2</h1>
            <span class="status-tag">النظام نشط ومتصل بالتليجرام ✅</span>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card"><span class="stat-val">${{ stats.profit }}</span><span class="stat-label">إجمالي الأرباح</span></div>
            <div class="stat-card"><span class="stat-val">{{ stats.completed }}</span><span class="stat-label">طلبات مكتملة</span></div>
            <div class="stat-card"><span class="stat-val">{{ stats.drivers }}</span><span class="stat-label">سائقين نشطين</span></div>
        </div>

        <h2 style="margin-top: 40px;">🏠 إدارة المطاعم (White Label)</h2>
        {% for slug, rest in restaurants.items() %}
        <div class="rest-card">
            <div><strong>{{ rest.logo }} {{ rest.name }}</strong><br><small style="color:#94a3b8;">الحد الأدنى: ${{ rest.min_order }}</small></div>
            <a href="/{{ slug }}" class="btn">معاينة الصفحة</a>
        </div>
        {% endfor %}
        
        <div style="margin-top: 50px; text-align: center; color: #94a3b8;">
            <p>🤖 البوت: @NYC_Delivery_Bot | التوكن: مثبت ومحمي</p>
        </div>
    </div>
</body>
</html>
"""

# ══════════════════════════════════════════════════════════════
# 3. مسارات ويب (FLASK ROUTES)
# ══════════════════════════════════════════════════════════════

@app.route('/')
def dashboard():
    data = db.load()
    stats = {
        "profit": round(data.get('profit', 0), 2),
        "completed": data.get('completed', 0),
        "drivers": len(data.get('drivers', {}))
    }
    return render_template_string(DASH_HTML, stats=stats, restaurants=RESTAURANTS)

@app.route('/<slug>')
def restaurant_landing(slug):
    rest = RESTAURANTS.get(slug)
    if not rest: return "المطعم غير موجود", 404
    return f"<h1>صفحة مطعم {rest['name']}</h1><p>هنا سيظهر منيو الطلبات للزبائن.</p>"

# ══════════════════════════════════════════════════════════════
# 4. منطق البوت (TELEGRAM BOT)
# ══════════════════════════════════════════════════════════════

@bot.message_handler(commands=['start'])
def welcome_message(message):
    welcome_text = (
        f"🗽 <b>أهلاً بك يا {message.from_user.first_name}!</b>\n\n"
        "✅ البوت متصل الآن بسيرفر NYC Delivery.\n"
        "🚕 هذا القسم مخصص لإدارة السائقين واستلام الطلبات.\n\n"
        "لوحة التحكم الخاصة بك تعمل الآن على الرابط الخاص بـ Render."
    )
    bot.reply_to(message, welcome_text)

def bot_worker():
    """تشغيل البوت في الخلفية مع تنظيف شامل للويب هوك"""
    while True:
        try:
            logger.info("🔄 جاري تنظيف الاتصالات القديمة وبدء Polling...")
            bot.remove_webhook(drop_pending_updates=True) # حذف كل الرسائل القديمة العالقة
            time.sleep(2)
            bot.infinity_polling(timeout=20, long_polling_timeout=5)
        except Exception as e:
            logger.error(f"❌ خطأ في البوت: {e}")
            time.sleep(10)

# ══════════════════════════════════════════════════════════════
# 5. التشغيل النهائي
# ══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    # تشغيل البوت في Thread منفصل
    bot_thread = threading.Thread(target=bot_worker, daemon=True)
    bot_thread.start()
    
    # تشغيل السيرفر
    logger.info("🚀 تشغيل نظام NYC v5.2 على المنفذ 10000")
    app.run(host='0.0.0.0', port=10000)
