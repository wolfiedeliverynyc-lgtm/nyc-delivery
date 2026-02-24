# 🗽 NYC Delivery System v5.1

نظام توصيل احترافي White Label مع Telegram Bot + Flask + Stripe

---

## 📋 **المميزات**

✅ **نموذج White Label** - كل مطعم له رابطه الخاص  
✅ **نموذج تسعير v5.1** - مع رسوم Stripe + ضمان ربح ≥$4  
✅ **Telegram Bot** - إدارة السائقين + إشعارات  
✅ **Mapbox Integration** - خرائط + مسارات + geocoding  
✅ **Stripe Payments** - دفع إلكتروني آمن  
✅ **SMS Notifications** - عبر Twilio (اختياري)  
✅ **Dashboard** - لوحة تحكم تفاعلية  
✅ **نظام تقييمات** - للسائقين  

---

## 📂 **الهيكل**

```
nyc-delivery-complete/
├── app.py                    # الملف الرئيسي (Flask + Bot)
├── config.py                 # الإعدادات + قاعدة المطاعم
├── database.py               # إدارة قاعدة البيانات (JSON)
├── mapbox_utils.py           # Mapbox أدوات
├── pricing.py                # محرك التسعير v5.1
├── sms_service.py            # خدمة SMS (Twilio)
├── requirements.txt          # المكتبات
├── Procfile                  # Render
├── runtime.txt               # Python 3.11
├── .env.example              # مثال للمتغيرات
└── README.md                 # هذا الملف
```

---

## 🚀 **التثبيت السريع**

### 1️⃣ **Clone/Download**
```bash
# Clone من GitHub أو حمّل الملفات
cd nyc-delivery-complete
```

### 2️⃣ **Environment Variables**
```bash
# انسخ .env.example إلى .env
cp .env.example .env

# املأ المتغيرات المطلوبة:
# - BOT_TOKEN (من @BotFather)
# - DRIVER_CHANNEL_ID (قناة السائقين)
# - REST_CHANNEL_ID (قناة المطاعم)
# - ADMIN_ID (رقمك في تيليجرام)
# - MAPBOX_ACCESS_TOKEN (من mapbox.com)
# - STRIPE_SECRET_KEY (اختياري)
```

### 3️⃣ **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 4️⃣ **Run Locally**
```bash
python app.py
```

**سيعمل على:** http://localhost:5000

---

## 🌐 **النشر على Render**

### خطوات النشر:

1. **GitHub**
   - أنشئ repo جديد
   - ارفع كل الملفات

2. **Render.com**
   - New → Web Service
   - اربط GitHub repo
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`

3. **Environment Variables**
   - أضف كل المتغيرات من `.env.example`
   - `WEBHOOK_URL` = رابط التطبيق من Render

4. **Deploy**
   - اضغط Deploy
   - انتظر 2-3 دقائق
   - افتح الرابط → Webhook يتفعل تلقائياً ✅

---

## 💰 **نموذج التسعير v5.1**

### **فاتورة الزبون:**
```
🍽️  الطعام:         $25.00
🚚 التوصيل:        $7.49  (حسب المسافة)
⚙️  الخدمة (12%):   $3.49
💰 الإجمالي:       $35.98
```

### **رسوم Stripe:**
```
2.9% + $0.30 = $1.34
صافي المنصة: $34.64
```

### **التوزيع:**
```
للمطعم (15% عمولة):  $21.25
للسائق:              $7.60
ربح المنصة:          $5.54 ✅
```

### **الشرائح:**

**رسوم التوصيل:**
- < 2 كم → $4.49
- 2-3 كم → $5.99
- 3-4 كم → $7.49
- 5-7 كم → $10.49
- 7+ كم → $12.49 + $0.50/km

**رسوم الخدمة:**
- < $20 → $4.99 (خاص)
- ≥ $20 → 12% (حد أدنى $3.49)

**عمولة المطعم:**
- < $20 → 18%
- $20-40 → 15%
- $40-80 → 12%
- > $80 → 10%

**أجر السائق:**
```
$3.50 + ($0.70 × km) + ($0.10 × min)
```

---

## 🏪 **إضافة مطعم جديد**

في `config.py` → `RESTAURANTS`:

```python
"pizzanyc": {
    "name": "Pizza NYC",
    "name_en": "Pizza NYC",
    "address": "456 Broadway, Manhattan",
    "coords": [40.7580, -73.9855],  # من Google Maps
    "logo": "🍕",
    "color": "#3498db",
    "description": "Best pizza in NYC",
    "min_order": 15.00,
    "menu": [
        {"id": 1, "name": "Margherita", "price": 18.00, "emoji": "🍕", "cat": "Pizza"},
        {"id": 2, "name": "Pepperoni", "price": 20.00, "emoji": "🍕", "cat": "Pizza"},
    ]
}
```

**رابط المطعم:** `https://your-app.com/pizzanyc`

---

## 🧪 **اختبار النظام**

### Test Pricing:
```bash
python pricing.py
```

سيعرض 5 اختبارات مختلفة مع الحسابات الكاملة.

### Test Mapbox:
```python
from mapbox_utils import MapboxUtils
mapbox = MapboxUtils("your_token")

# Geocode
result = mapbox.geocode("123 Main St, NYC")
print(result)  # {"lat": ..., "lon": ..., "address": ...}

# Directions
route = mapbox.get_directions((40.7128, -74.0060), (40.7580, -73.9855))
print(route)  # {"km": 5.2, "min": 15.3}
```

---

## 📊 **الأرباح المتوقعة**

| المطاعم | الطلبات/يوم | الربح الشهري |
|---------|-------------|---------------|
| 3 | 100 | **$8,600** |
| 5 | 100 | **$14,400** |
| 10 | 100 | **$28,800** |

**الحد الأدنى للطلب:** $10  
**متوسط الربح/طلب:** $5.27

---

## 🔧 **Troubleshooting**

### ❌ "Missing required config"
**الحل:** تأكد من `.env` يحتوي على:
- BOT_TOKEN
- DRIVER_CHANNEL_ID
- REST_CHANNEL_ID
- MAPBOX_ACCESS_TOKEN

### ❌ "Geocoding error"
**الحل:** تحقق من MAPBOX_ACCESS_TOKEN

### ❌ "Webhook failed"
**الحل:** 
1. تأكد WEBHOOK_URL صحيح
2. افتح `https://your-app.com/` مرة
3. تحقق Telegram webhook: `/setWebhook`

---

## 📝 **To-Do**

- [ ] إكمال صفحات المطاعم (HTML/CSS/JS)
- [ ] Stripe Checkout integration
- [ ] Dashboard كامل مع Mapbox
- [ ] نظام التقييمات UI
- [ ] PostgreSQL (بدل JSON)
- [ ] Mobile app للسائقين

---

## 📄 **License**

MIT License - استخدم بحرية!

---

## 💬 **الدعم**

لأي استفسار، افتح Issue في GitHub أو تواصل عبر:
- Telegram: @YourUsername
- Email: your@email.com

---

**Made with 🚀 by NYC Delivery Team**
