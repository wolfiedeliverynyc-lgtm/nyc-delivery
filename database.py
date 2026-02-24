"""
database.py - إدارة قاعدة البيانات
Thread-safe JSON database with all operations
"""

import json
import os
import threading
from datetime import datetime, timedelta
from typing import Optional, Dict, List


class Database:
    """قاعدة بيانات JSON محمية بـ threading"""
    
    def __init__(self, db_file: str = "delivery_db.json"):
        self.db_file = db_file
        self._lock = threading.Lock()
        self._ensure_db()
    
    def _default_data(self) -> Dict:
        """البيانات الافتراضية"""
        return {
            "profit": 0.0,
            "completed": 0,
            "cancelled": 0,
            "drivers": {},
            "stats": {},
            "orders": [],
            "restaurants": {},
            "created": datetime.now().isoformat(),
            "version": "5.0"
        }
    
    def _ensure_db(self):
        """إنشاء قاعدة البيانات إذا لم تكن موجودة"""
        if not os.path.exists(self.db_file):
            self._write(self._default_data())
    
    def _read(self) -> Dict:
        """قراءة قاعدة البيانات"""
        try:
            with open(self.db_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return self._default_data()
    
    def _write(self, data: Dict):
        """كتابة قاعدة البيانات"""
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load(self) -> Dict:
        """تحميل البيانات"""
        with self._lock:
            return self._read()
    
    def save(self, data: Dict):
        """حفظ البيانات"""
        with self._lock:
            self._write(data)
    
    # ══════════════════════════════════════════════════════════
    # ORDERS
    # ══════════════════════════════════════════════════════════
    
    def add_order(self, data: Dict, order: Dict):
        """إضافة طلب جديد"""
        data["orders"].append(order)
        self.save(data)
    
    def get_order(self, data: Dict, order_id: str) -> Optional[Dict]:
        """الحصول على طلب"""
        return next((o for o in data["orders"] if o.get("id") == order_id), None)
    
    def update_order(self, data: Dict, order_id: str, updates: Dict) -> bool:
        """تحديث طلب"""
        for order in data["orders"]:
            if order.get("id") == order_id:
                order.update(updates)
                self.save(data)
                return True
        return False
    
    # ══════════════════════════════════════════════════════════
    # DRIVERS
    # ══════════════════════════════════════════════════════════
    
    def set_driver_location(self, data: Dict, name: str, uid: int, location: str):
        """تحديث موقع السائق"""
        if name not in data["drivers"]:
            data["drivers"][name] = {"user_id": uid}
        
        data["drivers"][name].update({
            "user_id": uid,
            "location": location,
            "last_update": datetime.now().isoformat()
        })
        self.save(data)
    
    def is_driver_subscribed(self, data: Dict, name: str) -> bool:
        """التحقق من اشتراك السائق"""
        driver = data["drivers"].get(name, {})
        sub_until = driver.get("subscribed_until")
        
        if not sub_until:
            return False
        
        try:
            return datetime.fromisoformat(sub_until) > datetime.now()
        except:
            return False
    
    def subscribe_driver(self, data: Dict, name: str, uid: int, days: int = 30):
        """تفعيل اشتراك السائق"""
        if name not in data["drivers"]:
            data["drivers"][name] = {"user_id": uid}
        
        until = (datetime.now() + timedelta(days=days)).isoformat()
        data["drivers"][name].update({
            "subscribed_until": until,
            "orders_this_month": 0
        })
        self.save(data)
    
    # ══════════════════════════════════════════════════════════
    # STATS
    # ══════════════════════════════════════════════════════════
    
    def init_driver_stats(self, data: Dict, name: str):
        """تهيئة إحصائيات السائق"""
        if name not in data["stats"]:
            data["stats"][name] = {
                "completed": 0,
                "earned": 0.0,
                "rating": 5.0,
                "ratings_count": 0,
                "distance": 0.0,
                "orders_this_month": 0,
                "joined": datetime.now().isoformat()
            }
    
    def complete_driver_order(self, data: Dict, name: str, 
                             driver_pay: float, distance: float, 
                             platform_profit: float):
        """تسجيل طلب مكتمل للسائق"""
        self.init_driver_stats(data, name)
        
        stats = data["stats"][name]
        stats["completed"] += 1
        stats["earned"] = round(stats["earned"] + driver_pay, 2)
        stats["distance"] = round(stats["distance"] + distance, 2)
        stats["orders_this_month"] = stats.get("orders_this_month", 0) + 1
        
        data["profit"] = round(data["profit"] + platform_profit, 2)
        data["completed"] += 1
        
        self.save(data)
    
    def add_driver_rating(self, data: Dict, name: str, rating: int):
        """إضافة تقييم للسائق"""
        self.init_driver_stats(data, name)
        
        stats = data["stats"][name]
        count = stats["ratings_count"]
        
        # Weighted average
        new_rating = (stats["rating"] * count + rating) / (count + 1)
        stats["rating"] = round(new_rating, 2)
        stats["ratings_count"] = count + 1
        
        self.save(data)
    
    def get_leaderboard(self, data: Dict, limit: int = 10) -> List:
        """الحصول على المتصدرين"""
        return sorted(
            data["stats"].items(),
            key=lambda x: x[1].get("earned", 0),
            reverse=True
        )[:limit]
    
    def get_driver_rank(self, data: Dict, name: str) -> int:
        """الحصول على ترتيب السائق"""
        leaderboard = self.get_leaderboard(data, 9999)
        
        for i, (driver_name, _) in enumerate(leaderboard, 1):
            if driver_name == name:
                return i
        
        return len(leaderboard) + 1
    
    # ══════════════════════════════════════════════════════════
    # RESTAURANTS
    # ══════════════════════════════════════════════════════════
    
    def update_restaurant_stats(self, data: Dict, slug: str, 
                               revenue: float, commission: float):
        """تحديث إحصائيات المطعم"""
        if "restaurants" not in data:
            data["restaurants"] = {}
        
        if slug not in data["restaurants"]:
            data["restaurants"][slug] = {
                "total_orders": 0,
                "total_revenue": 0.0,
                "commission_owed": 0.0
            }
        
        rest = data["restaurants"][slug]
        rest["total_orders"] += 1
        rest["total_revenue"] = round(rest["total_revenue"] + revenue, 2)
        rest["commission_owed"] = round(rest["commission_owed"] + commission, 2)
        
        self.save(data)
