#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام المصادقة الآمن
JWT tokens, password hashing, session management
"""

import hashlib
import secrets
import sqlite3
import time
try:
    import jwt
except ImportError:
    print("⚠️ PyJWT غير مثبت. تثبيت...")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'PyJWT'])
    import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from secure_config import config
import logging

logger = logging.getLogger(__name__)

class SecureAuth:
    """فئة المصادقة الآمنة"""
    
    def __init__(self):
        self.secret_key = config.secret_key
        self.jwt_secret = config.get('JWT_SECRET_KEY', self.secret_key)
        self.session_timeout = config.get_int('SESSION_TIMEOUT', 3600)
        self.setup_auth_database()
        self.create_default_admin()
    
    def setup_auth_database(self):
        """إعداد قاعدة بيانات المصادقة"""
        try:
            conn = sqlite3.connect('auth.db')
            cursor = conn.cursor()
            
            # جدول المستخدمين
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS auth_users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    role TEXT DEFAULT 'user',
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    failed_attempts INTEGER DEFAULT 0,
                    locked_until TIMESTAMP
                )
            ''')
            
            # جدول الجلسات
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS auth_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    token_hash TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES auth_users (id)
                )
            ''')
            
            # جدول محاولات تسجيل الدخول
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS auth_login_attempts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    ip_address TEXT,
                    success BOOLEAN,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_agent TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("تم إعداد قاعدة بيانات المصادقة")
            
        except Exception as e:
            logger.error(f"خطأ في إعداد قاعدة بيانات المصادقة: {e}")
    
    def hash_password(self, password: str) -> tuple:
        """تشفير كلمة المرور"""
        salt = secrets.token_hex(32)
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # 100,000 iterations
        ).hex()
        return password_hash, salt
    
    def verify_password(self, password: str, password_hash: str, salt: str) -> bool:
        """التحقق من كلمة المرور"""
        computed_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        ).hex()
        return secrets.compare_digest(computed_hash, password_hash)
    
    def create_user(self, username: str, password: str, email: str = None, role: str = 'user') -> bool:
        """إنشاء مستخدم جديد"""
        try:
            # التحقق من قوة كلمة المرور
            if not self.is_strong_password(password):
                logger.warning(f"كلمة مرور ضعيفة للمستخدم: {username}")
                return False
            
            password_hash, salt = self.hash_password(password)
            
            conn = sqlite3.connect('auth.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO auth_users (username, email, password_hash, salt, role)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, email, password_hash, salt, role))
            
            conn.commit()
            conn.close()
            
            logger.info(f"تم إنشاء المستخدم: {username}")
            return True
            
        except sqlite3.IntegrityError:
            logger.warning(f"المستخدم موجود مسبقاً: {username}")
            return False
        except Exception as e:
            logger.error(f"خطأ في إنشاء المستخدم: {e}")
            return False
    
    def authenticate_user(self, username: str, password: str, ip_address: str = None, user_agent: str = None) -> dict:
        """مصادقة المستخدم"""
        try:
            conn = sqlite3.connect('auth.db')
            cursor = conn.cursor()
            
            # فحص المستخدم
            cursor.execute('''
                SELECT id, username, password_hash, salt, role, is_active, 
                       failed_attempts, locked_until
                FROM auth_users 
                WHERE username = ?
            ''', (username,))
            
            user = cursor.fetchone()
            
            # تسجيل محاولة تسجيل الدخول
            success = False
            
            if user:
                user_id, username, password_hash, salt, role, is_active, failed_attempts, locked_until = user
                
                # فحص إذا كان الحساب مقفل
                if locked_until and datetime.fromisoformat(locked_until) > datetime.now():
                    logger.warning(f"محاولة دخول لحساب مقفل: {username}")
                    return {'success': False, 'error': 'الحساب مقفل مؤقتاً'}
                
                # فحص إذا كان الحساب نشط
                if not is_active:
                    logger.warning(f"محاولة دخول لحساب معطل: {username}")
                    return {'success': False, 'error': 'الحساب معطل'}
                
                # التحقق من كلمة المرور
                if self.verify_password(password, password_hash, salt):
                    success = True
                    
                    # إعادة تعيين محاولات فاشلة
                    cursor.execute('''
                        UPDATE auth_users 
                        SET failed_attempts = 0, locked_until = NULL, last_login = CURRENT_TIMESTAMP
                        WHERE id = ?
                    ''', (user_id,))
                    
                    # إنشاء token
                    token = self.create_jwt_token(user_id, username, role)
                    
                    # حفظ الجلسة
                    self.save_session(user_id, token, ip_address, user_agent)
                    
                    conn.commit()
                    conn.close()
                    
                    logger.info(f"تسجيل دخول ناجح: {username}")
                    return {
                        'success': True,
                        'token': token,
                        'user': {
                            'id': user_id,
                            'username': username,
                            'role': role
                        }
                    }
                else:
                    # زيادة محاولات فاشلة
                    failed_attempts += 1
                    locked_until = None
                    
                    # قفل الحساب بعد 5 محاولات فاشلة
                    if failed_attempts >= 5:
                        locked_until = (datetime.now() + timedelta(minutes=30)).isoformat()
                        logger.warning(f"تم قفل الحساب: {username}")
                    
                    cursor.execute('''
                        UPDATE auth_users 
                        SET failed_attempts = ?, locked_until = ?
                        WHERE id = ?
                    ''', (failed_attempts, locked_until, user_id))
            
            # تسجيل محاولة تسجيل الدخول
            cursor.execute('''
                INSERT INTO auth_login_attempts (username, ip_address, success, user_agent)
                VALUES (?, ?, ?, ?)
            ''', (username, ip_address, success, user_agent))
            
            conn.commit()
            conn.close()
            
            if not success:
                logger.warning(f"محاولة دخول فاشلة: {username}")
                return {'success': False, 'error': 'اسم المستخدم أو كلمة المرور غير صحيحة'}
            
        except Exception as e:
            logger.error(f"خطأ في المصادقة: {e}")
            return {'success': False, 'error': 'خطأ في النظام'}
    
    def create_jwt_token(self, user_id: int, username: str, role: str) -> str:
        """إنشاء JWT token"""
        payload = {
            'user_id': user_id,
            'username': username,
            'role': role,
            'iat': int(time.time()),
            'exp': int(time.time()) + self.session_timeout
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm='HS256')
    
    def verify_jwt_token(self, token: str) -> dict:
        """التحقق من JWT token"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            
            # فحص انتهاء الصلاحية
            if payload['exp'] < time.time():
                return {'valid': False, 'error': 'انتهت صلاحية الجلسة'}
            
            return {'valid': True, 'payload': payload}
            
        except jwt.ExpiredSignatureError:
            return {'valid': False, 'error': 'انتهت صلاحية الجلسة'}
        except jwt.InvalidTokenError:
            return {'valid': False, 'error': 'رمز غير صحيح'}
    
    def save_session(self, user_id: int, token: str, ip_address: str = None, user_agent: str = None):
        """حفظ الجلسة"""
        try:
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            expires_at = (datetime.now() + timedelta(seconds=self.session_timeout)).isoformat()
            
            conn = sqlite3.connect('auth.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO auth_sessions (user_id, token_hash, expires_at, ip_address, user_agent)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, token_hash, expires_at, ip_address, user_agent))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"خطأ في حفظ الجلسة: {e}")
    
    def is_strong_password(self, password: str) -> bool:
        """فحص قوة كلمة المرور"""
        if len(password) < 8:
            return False
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password)
        
        return has_upper and has_lower and has_digit and has_special
    
    def create_default_admin(self):
        """إنشاء مدير افتراضي"""
        admin_username = config.get('DEFAULT_ADMIN_USERNAME', 'admin')
        admin_password = config.get('DEFAULT_ADMIN_PASSWORD', 'SecureAdmin123!')
        admin_email = config.get('DEFAULT_ADMIN_EMAIL', 'admin@chatbot.local')
        
        try:
            conn = sqlite3.connect('auth.db')
            cursor = conn.cursor()
            
            cursor.execute('SELECT id FROM auth_users WHERE username = ?', (admin_username,))
            if not cursor.fetchone():
                conn.close()
                
                if self.create_user(admin_username, admin_password, admin_email, 'admin'):
                    logger.info(f"تم إنشاء المدير الافتراضي: {admin_username}")
                else:
                    logger.error("فشل في إنشاء المدير الافتراضي")
            else:
                conn.close()
                logger.info("المدير الافتراضي موجود مسبقاً")
                
        except Exception as e:
            logger.error(f"خطأ في إنشاء المدير الافتراضي: {e}")

# Decorators للمصادقة
def require_auth(f):
    """Decorator للتحقق من المصادقة"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'مطلوب تسجيل دخول'}), 401
        
        token = auth_header.split(' ')[1]
        auth_result = secure_auth.verify_jwt_token(token)
        
        if not auth_result['valid']:
            return jsonify({'error': auth_result['error']}), 401
        
        # إضافة معلومات المستخدم للطلب
        request.current_user = auth_result['payload']
        
        return f(*args, **kwargs)
    
    return decorated_function

def require_role(required_role):
    """Decorator للتحقق من الدور"""
    def decorator(f):
        @wraps(f)
        @require_auth
        def decorated_function(*args, **kwargs):
            user_role = request.current_user.get('role')
            
            if user_role != required_role and user_role != 'admin':
                return jsonify({'error': 'ليس لديك صلاحية للوصول'}), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

# إنشاء مثيل عام
secure_auth = SecureAuth()

if __name__ == "__main__":
    print("🔐 اختبار نظام المصادقة...")
    
    # اختبار إنشاء مستخدم
    test_user = "test_user"
    test_password = "TestPassword123!"
    
    if secure_auth.create_user(test_user, test_password):
        print(f"✅ تم إنشاء المستخدم: {test_user}")
        
        # اختبار المصادقة
        auth_result = secure_auth.authenticate_user(test_user, test_password)
        if auth_result['success']:
            print("✅ المصادقة نجحت")
            
            # اختبار التحقق من token
            token_result = secure_auth.verify_jwt_token(auth_result['token'])
            if token_result['valid']:
                print("✅ التحقق من token نجح")
            else:
                print("❌ فشل التحقق من token")
        else:
            print("❌ فشلت المصادقة")
    else:
        print("❌ فشل إنشاء المستخدم")
    
    print("✅ انتهى اختبار نظام المصادقة")
