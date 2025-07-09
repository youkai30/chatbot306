#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام المصادقة والأمان للشات بوت
"""

import hashlib
import secrets
import time
import json
import sqlite3
from pathlib import Path

class AuthSystem:
    """نظام المصادقة"""
    
    def __init__(self, db_path="auth.db"):
        self.db_path = db_path
        self.sessions = {}
        self.init_database()
        self.create_default_admin()
    
    def init_database(self):
        """إنشاء قاعدة بيانات المصادقة"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # جدول المستخدمين
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                role TEXT DEFAULT 'user',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_login DATETIME,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # جدول الجلسات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                token TEXT PRIMARY KEY,
                user_id INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                expires_at DATETIME,
                ip_address TEXT,
                user_agent TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # جدول الصلاحيات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS permissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                resource TEXT NOT NULL,
                action TEXT NOT NULL,
                allowed BOOLEAN DEFAULT 1
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_default_admin(self):
        """إنشاء مستخدم إداري افتراضي"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # فحص إذا كان هناك مستخدم إداري
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
        if cursor.fetchone()[0] == 0:
            # إنشاء مستخدم إداري افتراضي
            admin_password = "admin123"  # يجب تغييره في الإنتاج
            password_hash = self.hash_password(admin_password)
            
            cursor.execute('''
                INSERT INTO users (username, password_hash, email, role)
                VALUES (?, ?, ?, ?)
            ''', ('admin', password_hash, 'admin@chatbot.local', 'admin'))
            
            # إضافة صلاحيات الإداري
            admin_permissions = [
                ('admin', 'dashboard', 'view'),
                ('admin', 'dashboard', 'edit'),
                ('admin', 'conversations', 'view'),
                ('admin', 'conversations', 'delete'),
                ('admin', 'channels', 'manage'),
                ('admin', 'flows', 'manage'),
                ('admin', 'analytics', 'view'),
                ('admin', 'integrations', 'manage'),
                ('admin', 'settings', 'manage'),
                ('admin', 'users', 'manage')
            ]
            
            for role, resource, action in admin_permissions:
                cursor.execute('''
                    INSERT INTO permissions (role, resource, action)
                    VALUES (?, ?, ?)
                ''', (role, resource, action))
            
            print("✅ تم إنشاء المستخدم الإداري الافتراضي:")
            print("   اسم المستخدم: admin")
            print("   كلمة المرور: admin123")
            print("   ⚠️  يرجى تغيير كلمة المرور فور تسجيل الدخول")
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password):
        """تشفير كلمة المرور"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', 
                                          password.encode('utf-8'), 
                                          salt.encode('utf-8'), 
                                          100000)
        return salt + password_hash.hex()
    
    def verify_password(self, password, stored_hash):
        """التحقق من كلمة المرور"""
        salt = stored_hash[:32]
        stored_password_hash = stored_hash[32:]
        
        password_hash = hashlib.pbkdf2_hmac('sha256',
                                          password.encode('utf-8'),
                                          salt.encode('utf-8'),
                                          100000)
        
        return password_hash.hex() == stored_password_hash
    
    def login(self, username, password, ip_address=None, user_agent=None):
        """تسجيل الدخول"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # البحث عن المستخدم
        cursor.execute('''
            SELECT id, password_hash, role, is_active 
            FROM users 
            WHERE username = ?
        ''', (username,))
        
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return {'success': False, 'error': 'اسم المستخدم غير صحيح'}
        
        user_id, password_hash, role, is_active = user
        
        if not is_active:
            conn.close()
            return {'success': False, 'error': 'الحساب معطل'}
        
        if not self.verify_password(password, password_hash):
            conn.close()
            return {'success': False, 'error': 'كلمة المرور غير صحيحة'}
        
        # إنشاء جلسة جديدة
        token = secrets.token_urlsafe(32)
        expires_at = time.time() + (24 * 60 * 60)  # 24 ساعة
        
        cursor.execute('''
            INSERT INTO sessions (token, user_id, expires_at, ip_address, user_agent)
            VALUES (?, ?, datetime(?, 'unixepoch'), ?, ?)
        ''', (token, user_id, expires_at, ip_address, user_agent))
        
        # تحديث آخر تسجيل دخول
        cursor.execute('''
            UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
        ''', (user_id,))
        
        conn.commit()
        conn.close()
        
        # حفظ الجلسة في الذاكرة
        self.sessions[token] = {
            'user_id': user_id,
            'username': username,
            'role': role,
            'expires_at': expires_at
        }
        
        return {
            'success': True,
            'token': token,
            'user': {
                'id': user_id,
                'username': username,
                'role': role
            }
        }
    
    def logout(self, token):
        """تسجيل الخروج"""
        if token in self.sessions:
            del self.sessions[token]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM sessions WHERE token = ?', (token,))
        conn.commit()
        conn.close()
        
        return {'success': True}
    
    def verify_token(self, token):
        """التحقق من صحة الرمز المميز"""
        # فحص الجلسة في الذاكرة
        if token in self.sessions:
            session = self.sessions[token]
            if time.time() < session['expires_at']:
                return session
            else:
                # الجلسة منتهية الصلاحية
                del self.sessions[token]
        
        # فحص قاعدة البيانات
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT s.user_id, u.username, u.role, s.expires_at
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.token = ? AND s.expires_at > datetime('now')
        ''', (token,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            user_id, username, role, expires_at = result
            expires_timestamp = time.mktime(time.strptime(expires_at, '%Y-%m-%d %H:%M:%S'))
            
            session = {
                'user_id': user_id,
                'username': username,
                'role': role,
                'expires_at': expires_timestamp
            }
            
            # حفظ في الذاكرة
            self.sessions[token] = session
            return session
        
        return None
    
    def check_permission(self, role, resource, action):
        """فحص الصلاحيات"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT allowed FROM permissions 
            WHERE role = ? AND resource = ? AND action = ?
        ''', (role, resource, action))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return bool(result[0])
        
        # الصلاحيات الافتراضية
        if role == 'admin':
            return True
        elif role == 'user':
            return action == 'view'
        
        return False
    
    def require_auth(self, token, resource=None, action='view'):
        """مطلوب المصادقة"""
        session = self.verify_token(token)
        
        if not session:
            return {'success': False, 'error': 'غير مصرح', 'code': 401}
        
        if resource and not self.check_permission(session['role'], resource, action):
            return {'success': False, 'error': 'غير مسموح', 'code': 403}
        
        return {'success': True, 'user': session}
    
    def create_user(self, username, password, email=None, role='user'):
        """إنشاء مستخدم جديد"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # فحص إذا كان اسم المستخدم موجود
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        if cursor.fetchone():
            conn.close()
            return {'success': False, 'error': 'اسم المستخدم موجود مسبقاً'}
        
        # تشفير كلمة المرور
        password_hash = self.hash_password(password)
        
        # إنشاء المستخدم
        cursor.execute('''
            INSERT INTO users (username, password_hash, email, role)
            VALUES (?, ?, ?, ?)
        ''', (username, password_hash, email, role))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {'success': True, 'user_id': user_id}
    
    def get_users(self):
        """الحصول على قائمة المستخدمين"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, email, role, created_at, last_login, is_active
            FROM users
            ORDER BY created_at DESC
        ''')
        
        users = []
        for row in cursor.fetchall():
            users.append({
                'id': row[0],
                'username': row[1],
                'email': row[2],
                'role': row[3],
                'created_at': row[4],
                'last_login': row[5],
                'is_active': bool(row[6])
            })
        
        conn.close()
        return users

# إنشاء مثيل عام
auth_system = AuthSystem()

if __name__ == "__main__":
    # اختبار النظام
    print("🔐 اختبار نظام المصادقة...")
    
    # تسجيل دخول المستخدم الإداري
    result = auth_system.login('admin', 'admin123')
    if result['success']:
        print("✅ تم تسجيل الدخول بنجاح")
        token = result['token']
        
        # فحص الصلاحيات
        auth_check = auth_system.require_auth(token, 'dashboard', 'view')
        if auth_check['success']:
            print("✅ المستخدم لديه صلاحية عرض لوحة التحكم")
        
        # تسجيل الخروج
        auth_system.logout(token)
        print("✅ تم تسجيل الخروج")
    else:
        print(f"❌ فشل تسجيل الدخول: {result['error']}")
    
    print("🔐 نظام المصادقة جاهز للاستخدام")
