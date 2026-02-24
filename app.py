import time
import logging
import threading
from flask import Flask
import telebot

# الإعدادات الأساسية
TOKEN = "8336818567:AAFo-rCZ-LskakZEKfedVMvVkYNfER96wQs"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- أوامر البوت ---
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    print(f"استلمت رسالة من: {message.from_user.id}") # ستظهر في سجلات Render
    bot.reply_to(message, "✅ أهلاً بك! البوت يعمل الآن بنظام الطوارئ.")

# --- تشغيل البوت في الخلفية ---
def run_bot():
    while True:
        try:
            logging.info("Starting Bot Polling...")
            bot.remove_webhook()
            bot.polling(none_stop=True, interval=1, timeout=20)
        except Exception as e:
            logging.error(f"Bot Error: {e}")
            time.sleep(5)

# --- مسار الويب الأساسي ---
@app.route('/')
def health_check():
    return "<h1>NYC Bot is Running!</h1>"

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    # تشغيل البوت
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    # تشغيل السيرفر
    app.run(host='0.0.0.0', port=10000)
