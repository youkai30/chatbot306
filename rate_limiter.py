#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام تحديد معدل الطلبات (Rate Limiting)
يمنع إساءة استخدام APIs ويحمي من الهجمات
"""

import time
import sqlite3
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from secure_config import config
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """فئة تحديد معدل الطلبات"""
    
    def __init__(self):
        self.per_minute_limit = config.rate_limit_per_minute
        self.per_hour_limit = config.rate_limit_per_hour
        self.setup_rate_limit_database()
    
    def setup_rate_limit_database(self):
        """إعداد قاعدة بيانات Rate Limiting"""
        try:
            conn = sqlite3.connect('rate_limits.db')
            cursor = conn.cursor()
            
            # جدول طلبات الدقيقة
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS minute_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    identifier TEXT NOT NULL,
                    endpoint TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_address TEXT,
                    user_agent TEXT
                )
            ''')
            
            # جدول طلبات الساعة
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS hour_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    identifier TEXT NOT NULL,
                    endpoint TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_address TEXT,
                    user_agent TEXT
                )
            ''')
            
            # جدول الحظر المؤقت
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS temporary_bans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    identifier TEXT UNIQUE NOT NULL,
                    banned_until TIMESTAMP NOT NULL,
                    reason TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # إنشاء فهارس للأداء
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_minute_identifier_timestamp ON minute_requests(identifier, timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_hour_identifier_timestamp ON hour_requests(identifier, timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_bans_identifier ON temporary_bans(identifier)')
            
            conn.commit()
            conn.close()
            logger.info("تم إعداد قاعدة بيانات Rate Limiting")
            
        except Exception as e:
            logger.error(f"خطأ في إعداد قاعدة بيانات Rate Limiting: {e}")
    
    def get_identifier(self, request) -> str:
        """الحصول على معرف المستخدم/IP"""
        # إذا كان مسجل دخول، استخدم user_id
        if hasattr(request, 'current_user') and request.current_user:
            return f"user_{request.current_user.get('user_id')}"
        
        # وإلا استخدم IP address
        ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'unknown'))
        return f"ip_{ip}"
    
    def is_banned(self, identifier: str) -> tuple:
        """فحص إذا كان المستخدم محظور مؤقتاً"""
        try:
            conn = sqlite3.connect('rate_limits.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT banned_until, reason 
                FROM temporary_bans 
                WHERE identifier = ? AND banned_until > CURRENT_TIMESTAMP
            ''', (identifier,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                banned_until, reason = result
                return True, banned_until, reason
            
            return False, None, None
            
        except Exception as e:
            logger.error(f"خطأ في فحص الحظر: {e}")
            return False, None, None
    
    def check_rate_limit(self, identifier: str, endpoint: str, ip_address: str, user_agent: str) -> dict:
        """فحص حدود معدل الطلبات"""
        try:
            # فحص الحظر المؤقت
            is_banned, banned_until, reason = self.is_banned(identifier)
            if is_banned:
                return {
                    'allowed': False,
                    'error': f'محظور مؤقتاً حتى {banned_until}. السبب: {reason}',
                    'retry_after': banned_until
                }
            
            conn = sqlite3.connect('rate_limits.db')
            cursor = conn.cursor()
            
            current_time = datetime.now()
            minute_ago = current_time - timedelta(minutes=1)
            hour_ago = current_time - timedelta(hours=1)
            
            # فحص طلبات الدقيقة الماضية
            cursor.execute('''
                SELECT COUNT(*) FROM minute_requests 
                WHERE identifier = ? AND timestamp > ?
            ''', (identifier, minute_ago.isoformat()))
            
            minute_count = cursor.fetchone()[0]
            
            # فحص طلبات الساعة الماضية
            cursor.execute('''
                SELECT COUNT(*) FROM hour_requests 
                WHERE identifier = ? AND timestamp > ?
            ''', (identifier, hour_ago.isoformat()))
            
            hour_count = cursor.fetchone()[0]
            
            # فحص الحدود
            if minute_count >= self.per_minute_limit:
                # حظر مؤقت لمدة 5 دقائق
                self.add_temporary_ban(identifier, 5, "تجاوز حد الطلبات في الدقيقة")
                conn.close()
                return {
                    'allowed': False,
                    'error': f'تجاوزت حد الطلبات ({self.per_minute_limit} في الدقيقة)',
                    'retry_after': 60
                }
            
            if hour_count >= self.per_hour_limit:
                # حظر مؤقت لمدة ساعة
                self.add_temporary_ban(identifier, 60, "تجاوز حد الطلبات في الساعة")
                conn.close()
                return {
                    'allowed': False,
                    'error': f'تجاوزت حد الطلبات ({self.per_hour_limit} في الساعة)',
                    'retry_after': 3600
                }
            
            # تسجيل الطلب
            cursor.execute('''
                INSERT INTO minute_requests (identifier, endpoint, ip_address, user_agent)
                VALUES (?, ?, ?, ?)
            ''', (identifier, endpoint, ip_address, user_agent))
            
            cursor.execute('''
                INSERT INTO hour_requests (identifier, endpoint, ip_address, user_agent)
                VALUES (?, ?, ?, ?)
            ''', (identifier, endpoint, ip_address, user_agent))
            
            # تنظيف البيانات القديمة
            cursor.execute('DELETE FROM minute_requests WHERE timestamp < ?', (minute_ago.isoformat(),))
            cursor.execute('DELETE FROM hour_requests WHERE timestamp < ?', (hour_ago.isoformat(),))
            cursor.execute('DELETE FROM temporary_bans WHERE banned_until < CURRENT_TIMESTAMP')
            
            conn.commit()
            conn.close()
            
            return {
                'allowed': True,
                'remaining_minute': self.per_minute_limit - minute_count - 1,
                'remaining_hour': self.per_hour_limit - hour_count - 1
            }
            
        except Exception as e:
            logger.error(f"خطأ في فحص Rate Limiting: {e}")
            return {'allowed': True}  # السماح في حالة الخطأ
    
    def add_temporary_ban(self, identifier: str, duration_minutes: int, reason: str):
        """إضافة حظر مؤقت"""
        try:
            banned_until = datetime.now() + timedelta(minutes=duration_minutes)
            
            conn = sqlite3.connect('rate_limits.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO temporary_bans (identifier, banned_until, reason)
                VALUES (?, ?, ?)
            ''', (identifier, banned_until.isoformat(), reason))
            
            conn.commit()
            conn.close()
            
            logger.warning(f"تم حظر {identifier} مؤقتاً لمدة {duration_minutes} دقيقة. السبب: {reason}")
            
        except Exception as e:
            logger.error(f"خطأ في إضافة الحظر المؤقت: {e}")
    
    def get_stats(self) -> dict:
        """الحصول على إحصائيات Rate Limiting"""
        try:
            conn = sqlite3.connect('rate_limits.db')
            cursor = conn.cursor()
            
            # طلبات الدقيقة الماضية
            minute_ago = (datetime.now() - timedelta(minutes=1)).isoformat()
            cursor.execute('SELECT COUNT(*) FROM minute_requests WHERE timestamp > ?', (minute_ago,))
            minute_requests = cursor.fetchone()[0]
            
            # طلبات الساعة الماضية
            hour_ago = (datetime.now() - timedelta(hours=1)).isoformat()
            cursor.execute('SELECT COUNT(*) FROM hour_requests WHERE timestamp > ?', (hour_ago,))
            hour_requests = cursor.fetchone()[0]
            
            # المحظورين حالياً
            cursor.execute('SELECT COUNT(*) FROM temporary_bans WHERE banned_until > CURRENT_TIMESTAMP')
            active_bans = cursor.fetchone()[0]
            
            # أكثر المستخدمين نشاطاً
            cursor.execute('''
                SELECT identifier, COUNT(*) as count 
                FROM hour_requests 
                WHERE timestamp > ? 
                GROUP BY identifier 
                ORDER BY count DESC 
                LIMIT 5
            ''', (hour_ago,))
            
            top_users = [{'identifier': row[0], 'requests': row[1]} for row in cursor.fetchall()]
            
            conn.close()
            
            return {
                'minute_requests': minute_requests,
                'hour_requests': hour_requests,
                'active_bans': active_bans,
                'top_users': top_users,
                'limits': {
                    'per_minute': self.per_minute_limit,
                    'per_hour': self.per_hour_limit
                }
            }
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على إحصائيات Rate Limiting: {e}")
            return {}

# إنشاء مثيل عام
rate_limiter = RateLimiter()

def rate_limit(endpoint_name: str = None):
    """Decorator لتطبيق Rate Limiting"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            endpoint = endpoint_name or request.endpoint or f.__name__
            identifier = rate_limiter.get_identifier(request)
            ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'unknown'))
            user_agent = request.headers.get('User-Agent', 'unknown')
            
            # فحص Rate Limiting
            result = rate_limiter.check_rate_limit(identifier, endpoint, ip_address, user_agent)
            
            if not result.get('allowed', True):
                response = jsonify({
                    'error': result['error'],
                    'retry_after': result.get('retry_after', 60)
                })
                response.status_code = 429  # Too Many Requests
                response.headers['Retry-After'] = str(result.get('retry_after', 60))
                return response
            
            # إضافة headers للمعلومات
            response = f(*args, **kwargs)
            if hasattr(response, 'headers'):
                response.headers['X-RateLimit-Limit-Minute'] = str(rate_limiter.per_minute_limit)
                response.headers['X-RateLimit-Limit-Hour'] = str(rate_limiter.per_hour_limit)
                response.headers['X-RateLimit-Remaining-Minute'] = str(result.get('remaining_minute', 0))
                response.headers['X-RateLimit-Remaining-Hour'] = str(result.get('remaining_hour', 0))
            
            return response
        
        return decorated_function
    return decorator

if __name__ == "__main__":
    print("⚡ اختبار نظام Rate Limiting...")
    
    # محاكاة طلبات
    test_identifier = "test_user_123"
    test_endpoint = "test_endpoint"
    test_ip = "192.168.1.1"
    test_user_agent = "Test Agent"
    
    # اختبار طلبات عادية
    for i in range(5):
        result = rate_limiter.check_rate_limit(test_identifier, test_endpoint, test_ip, test_user_agent)
        print(f"طلب {i+1}: {'✅ مسموح' if result['allowed'] else '❌ مرفوض'}")
        if not result['allowed']:
            print(f"  السبب: {result['error']}")
    
    # عرض الإحصائيات
    stats = rate_limiter.get_stats()
    print(f"\n📊 الإحصائيات:")
    print(f"  طلبات الدقيقة: {stats.get('minute_requests', 0)}")
    print(f"  طلبات الساعة: {stats.get('hour_requests', 0)}")
    print(f"  محظورين حالياً: {stats.get('active_bans', 0)}")
    
    print("✅ انتهى اختبار Rate Limiting")
