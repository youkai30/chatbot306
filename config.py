#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ملف الإعدادات للنظام
يحتوي على جميع الإعدادات القابلة للتخصيص
"""

import os
from pathlib import Path

class Config:
    """إعدادات النظام"""
    
    # إعدادات الخادم
    HOST = os.getenv('HOST', 'localhost')
    BACKEND_PORT = int(os.getenv('BACKEND_PORT', 8001))
    FRONTEND_PORT = int(os.getenv('FRONTEND_PORT', 8000))
    AI_AGENT_PORT = int(os.getenv('AI_AGENT_PORT', 5000))
    
    # إعدادات قاعدة البيانات
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'chatbot_data.db')
    AUTH_DATABASE_PATH = os.getenv('AUTH_DATABASE_PATH', 'auth.db')
    
    # إعدادات الأمان
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', 86400))  # 24 ساعة
    
    # إعدادات AI
    AI_PROVIDER = os.getenv('AI_PROVIDER', 'deepseek')
    AI_API_KEY = os.getenv('AI_API_KEY', '')
    AI_MODEL = os.getenv('AI_MODEL', 'deepseek-chat')
    AI_TEMPERATURE = float(os.getenv('AI_TEMPERATURE', 0.7))
    AI_MAX_TOKENS = int(os.getenv('AI_MAX_TOKENS', 1000))
    
    # إعدادات التطبيق
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')  # development, production
    
    # إعدادات التسجيل
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'chatbot.log')
    
    # إعدادات CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # إعدادات النسخ الاحتياطي
    BACKUP_ENABLED = os.getenv('BACKUP_ENABLED', 'True').lower() == 'true'
    BACKUP_INTERVAL = int(os.getenv('BACKUP_INTERVAL', 3600))  # كل ساعة
    BACKUP_DIRECTORY = os.getenv('BACKUP_DIRECTORY', 'backups')
    
    # إعدادات الإشعارات
    EMAIL_ENABLED = os.getenv('EMAIL_ENABLED', 'False').lower() == 'true'
    EMAIL_HOST = os.getenv('EMAIL_HOST', '')
    EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
    EMAIL_USER = os.getenv('EMAIL_USER', '')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
    
    # إعدادات الويب هوك
    WEBHOOK_ENABLED = os.getenv('WEBHOOK_ENABLED', 'False').lower() == 'true'
    WEBHOOK_URL = os.getenv('WEBHOOK_URL', '')
    
    @classmethod
    def get_database_url(cls):
        """الحصول على رابط قاعدة البيانات"""
        return f"sqlite:///{cls.DATABASE_PATH}"
    
    @classmethod
    def get_auth_database_url(cls):
        """الحصول على رابط قاعدة بيانات المصادقة"""
        return f"sqlite:///{cls.AUTH_DATABASE_PATH}"
    
    @classmethod
    def create_directories(cls):
        """إنشاء المجلدات المطلوبة"""
        directories = [
            cls.BACKUP_DIRECTORY,
            'logs',
            'uploads',
            'exports'
        ]
        
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
    
    @classmethod
    def validate_config(cls):
        """التحقق من صحة الإعدادات"""
        errors = []
        
        # فحص المنافذ
        if not (1024 <= cls.BACKEND_PORT <= 65535):
            errors.append(f"منفذ الباك-إند غير صحيح: {cls.BACKEND_PORT}")
        
        if not (1024 <= cls.FRONTEND_PORT <= 65535):
            errors.append(f"منفذ الفرونت-إند غير صحيح: {cls.FRONTEND_PORT}")
        
        # فحص إعدادات AI
        if cls.AI_PROVIDER == 'deepseek' and not cls.AI_API_KEY:
            errors.append("مفتاح API للـ DeepSeek مطلوب")
        
        # فحص إعدادات الإيميل
        if cls.EMAIL_ENABLED and not all([cls.EMAIL_HOST, cls.EMAIL_USER, cls.EMAIL_PASSWORD]):
            errors.append("إعدادات الإيميل غير مكتملة")
        
        return errors

class DevelopmentConfig(Config):
    """إعدادات التطوير"""
    DEBUG = True
    HOST = 'localhost'

class ProductionConfig(Config):
    """إعدادات الإنتاج"""
    DEBUG = False
    HOST = '0.0.0.0'
    
    # إعدادات أمان إضافية للإنتاج
    SESSION_TIMEOUT = 3600  # ساعة واحدة
    CORS_ORIGINS = ['https://yourdomain.com']

# اختيار الإعدادات حسب البيئة
def get_config():
    """الحصول على الإعدادات المناسبة للبيئة"""
    env = os.getenv('ENVIRONMENT', 'development')
    
    if env == 'production':
        return ProductionConfig
    else:
        return DevelopmentConfig

# الإعدادات الحالية
current_config = get_config()

if __name__ == "__main__":
    # اختبار الإعدادات
    print("🔧 فحص الإعدادات...")
    
    config = get_config()
    errors = config.validate_config()
    
    if errors:
        print("❌ أخطاء في الإعدادات:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✅ جميع الإعدادات صحيحة")
    
    print(f"\n📋 الإعدادات الحالية:")
    print(f"  البيئة: {config.ENVIRONMENT}")
    print(f"  المضيف: {config.HOST}")
    print(f"  منفذ الباك-إند: {config.BACKEND_PORT}")
    print(f"  منفذ الفرونت-إند: {config.FRONTEND_PORT}")
    print(f"  وضع التطوير: {config.DEBUG}")
    print(f"  مزود AI: {config.AI_PROVIDER}")
    
    # إنشاء المجلدات
    config.create_directories()
    print("✅ تم إنشاء المجلدات المطلوبة")
