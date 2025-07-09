#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام إدارة الإعدادات الآمن
يقرأ الإعدادات من ملف .env بشكل آمن
"""

import os
import logging
from pathlib import Path
from typing import Optional

class SecureConfig:
    """فئة إدارة الإعدادات الآمنة"""
    
    def __init__(self):
        self.load_env_file()
        self.setup_logging()
        self.validate_config()
    
    def load_env_file(self):
        """تحميل ملف .env"""
        env_path = Path('.env')
        
        if not env_path.exists():
            self.create_default_env()
        
        # قراءة ملف .env
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
        except Exception as e:
            print(f"خطأ في قراءة ملف .env: {e}")
    
    def create_default_env(self):
        """إنشاء ملف .env افتراضي"""
        default_env = """# إعدادات النظام الآمنة
DEEPSEEK_API_KEY=your-deepseek-api-key-here
SECRET_KEY=change-this-secret-key
DEBUG=true
HOST=localhost
BACKEND_PORT=8001
FRONTEND_PORT=8000
"""
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(default_env)
        
        print("⚠️  تم إنشاء ملف .env افتراضي. يرجى تحديث الإعدادات!")
    
    def setup_logging(self):
        """إعداد نظام التسجيل"""
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        log_level = getattr(logging, self.get('LOG_LEVEL', 'INFO'))
        log_file = self.get('LOG_FILE', 'logs/chatbot.log')
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("تم تهيئة نظام التسجيل")
    
    def get(self, key: str, default: Optional[str] = None) -> str:
        """الحصول على قيمة إعداد"""
        value = os.getenv(key, default)
        if value is None:
            self.logger.warning(f"الإعداد {key} غير موجود")
        return value
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """الحصول على قيمة boolean"""
        value = self.get(key, str(default))
        return value.lower() in ('true', '1', 'yes', 'on')
    
    def get_int(self, key: str, default: int = 0) -> int:
        """الحصول على قيمة integer"""
        try:
            return int(self.get(key, str(default)))
        except ValueError:
            self.logger.warning(f"قيمة غير صحيحة للإعداد {key}")
            return default
    
    def get_list(self, key: str, default: list = None) -> list:
        """الحصول على قائمة من النص"""
        if default is None:
            default = []
        
        value = self.get(key, '')
        if not value:
            return default
        
        return [item.strip() for item in value.split(',') if item.strip()]
    
    def validate_config(self):
        """التحقق من صحة الإعدادات"""
        errors = []
        
        # فحص المفاتيح المطلوبة
        required_keys = [
            'DEEPSEEK_API_KEY',
            'SECRET_KEY',
            'BACKEND_PORT',
            'FRONTEND_PORT'
        ]
        
        for key in required_keys:
            if not self.get(key):
                errors.append(f"الإعداد المطلوب {key} غير موجود")
        
        # فحص مفتاح DeepSeek
        api_key = self.get('DEEPSEEK_API_KEY', '')
        if api_key in ['your-deepseek-api-key-here', '']:
            errors.append("يرجى تحديث مفتاح DeepSeek API")
        
        # فحص المفتاح السري
        secret_key = self.get('SECRET_KEY', '')
        if secret_key in ['change-this-secret-key', ''] or len(secret_key) < 16:
            errors.append("يرجى تحديث المفتاح السري (16 حرف على الأقل)")
        
        # فحص المنافذ
        backend_port = self.get_int('BACKEND_PORT')
        frontend_port = self.get_int('FRONTEND_PORT')
        
        if not (1024 <= backend_port <= 65535):
            errors.append(f"منفذ الباك-إند غير صحيح: {backend_port}")
        
        if not (1024 <= frontend_port <= 65535):
            errors.append(f"منفذ الفرونت-إند غير صحيح: {frontend_port}")
        
        if backend_port == frontend_port:
            errors.append("منفذ الباك-إند والفرونت-إند لا يمكن أن يكونا نفس الرقم")
        
        if errors:
            self.logger.error("أخطاء في الإعدادات:")
            for error in errors:
                self.logger.error(f"  - {error}")
            
            if not self.get_bool('DEBUG'):
                raise ValueError("إعدادات غير صحيحة. راجع ملف .env")
        else:
            self.logger.info("جميع الإعدادات صحيحة")
    
    @property
    def deepseek_api_key(self) -> str:
        """مفتاح DeepSeek API"""
        return self.get('DEEPSEEK_API_KEY')
    
    @property
    def secret_key(self) -> str:
        """المفتاح السري"""
        return self.get('SECRET_KEY')
    
    @property
    def database_url(self) -> str:
        """رابط قاعدة البيانات"""
        return self.get('DATABASE_URL', 'sqlite:///chatbot_data.db')
    
    @property
    def backend_port(self) -> int:
        """منفذ الباك-إند"""
        return self.get_int('BACKEND_PORT', 8001)
    
    @property
    def frontend_port(self) -> int:
        """منفذ الفرونت-إند"""
        return self.get_int('FRONTEND_PORT', 8000)
    
    @property
    def allowed_origins(self) -> list:
        """المواقع المسموح لها بالوصول"""
        return self.get_list('ALLOWED_ORIGINS', ['http://localhost:8000'])
    
    @property
    def rate_limit_per_minute(self) -> int:
        """حد الطلبات في الدقيقة"""
        return self.get_int('RATE_LIMIT_PER_MINUTE', 30)
    
    @property
    def rate_limit_per_hour(self) -> int:
        """حد الطلبات في الساعة"""
        return self.get_int('RATE_LIMIT_PER_HOUR', 500)
    
    @property
    def is_debug(self) -> bool:
        """وضع التطوير"""
        return self.get_bool('DEBUG', False)
    
    def get_database_path(self) -> str:
        """مسار قاعدة البيانات"""
        url = self.database_url
        if url.startswith('sqlite:///'):
            return url[10:]  # إزالة sqlite:///
        return 'chatbot_data.db'

# إنشاء مثيل عام
config = SecureConfig()

if __name__ == "__main__":
    print("🔧 فحص الإعدادات...")
    
    print(f"مفتاح DeepSeek: {'✅ موجود' if config.deepseek_api_key else '❌ غير موجود'}")
    print(f"المفتاح السري: {'✅ موجود' if config.secret_key else '❌ غير موجود'}")
    print(f"منفذ الباك-إند: {config.backend_port}")
    print(f"منفذ الفرونت-إند: {config.frontend_port}")
    print(f"وضع التطوير: {config.is_debug}")
    print(f"المواقع المسموحة: {config.allowed_origins}")
    
    print("✅ تم فحص الإعدادات بنجاح")
