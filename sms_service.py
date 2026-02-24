"""
sms_service.py - SMS خدمة
Twilio integration for customer notifications
"""

import os
import logging
from typing import Optional

log = logging.getLogger(__name__)


class SMSService:
    """خدمة إرسال SMS عبر Twilio"""
    
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = os.getenv("TWILIO_PHONE_NUMBER")
        self.enabled = all([self.account_sid, self.auth_token, self.from_number])
        
        if self.enabled:
            try:
                from twilio.rest import Client
                self.client = Client(self.account_sid, self.auth_token)
                log.info("✅ SMS Service enabled (Twilio)")
            except ImportError:
                log.warning("⚠️ Twilio not installed - SMS disabled")
                self.enabled = False
        else:
            log.info("ℹ️ SMS Service disabled (missing credentials)")
    
    def send_sms(self, to_number: str, message: str) -> bool:
        """
        إرسال رسالة SMS
        
        Args:
            to_number: رقم الهاتف (+1234567890)
            message: نص الرسالة
        
        Returns:
            True إذا تم الإرسال بنجاح
        """
        if not self.enabled:
            log.debug(f"SMS disabled - Would send to {to_number}: {message}")
            return False
        
        try:
            message = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number
            )
            
            log.info(f"✅ SMS sent to {to_number} - SID: {message.sid}")
            return True
        
        except Exception as e:
            log.error(f"❌ SMS error to {to_number}: {e}")
            return False
    
    def notify_order_accepted(self, phone: str, order_id: str, 
                             driver_name: str, eta_minutes: int) -> bool:
        """إشعار قبول الطلب"""
        message = (
            f"🚚 NYC Delivery\n"
            f"Order #{order_id} accepted!\n"
            f"Driver: {driver_name}\n"
            f"ETA: ~{eta_minutes} minutes"
        )
        return self.send_sms(phone, message)
    
    def notify_order_completed(self, phone: str, order_id: str) -> bool:
        """إشعار إتمام الطلب"""
        message = (
            f"✅ NYC Delivery\n"
            f"Order #{order_id} delivered!\n"
            f"Thank you for your order!"
        )
        return self.send_sms(phone, message)
    
    def notify_order_cancelled(self, phone: str, order_id: str, 
                              reason: str = "") -> bool:
        """إشعار إلغاء الطلب"""
        message = (
            f"❌ NYC Delivery\n"
            f"Order #{order_id} cancelled"
        )
        
        if reason:
            message += f"\nReason: {reason}"
        
        return self.send_sms(phone, message)
