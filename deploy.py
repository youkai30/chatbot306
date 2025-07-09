#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت النشر للإنتاج
يحضر النظام للنشر على خادم حقيقي
"""

import os
import sys
import shutil
import subprocess
import zipfile
from pathlib import Path
from datetime import datetime

class DeploymentManager:
    """مدير النشر"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.deploy_dir = self.project_root / 'deploy'
        self.backup_dir = self.project_root / 'backups'
        
    def print_header(self):
        """طباعة رأس النشر"""
        print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                🚀 إعداد النظام للنشر                        ║
║                                                              ║
║              تحضير النظام للخادم الحقيقي                    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

📦 بدء عملية التحضير للنشر...
        """)
    
    def create_deploy_structure(self):
        """إنشاء هيكل النشر"""
        print("📁 إنشاء هيكل المجلدات...")
        
        # إنشاء مجلد النشر
        if self.deploy_dir.exists():
            shutil.rmtree(self.deploy_dir)
        
        self.deploy_dir.mkdir()
        
        # المجلدات المطلوبة
        directories = [
            'backend',
            'frontend',
            'static',
            'templates',
            'config',
            'scripts',
            'docs'
        ]
        
        for directory in directories:
            (self.deploy_dir / directory).mkdir()
        
        print("✅ تم إنشاء هيكل المجلدات")
    
    def copy_backend_files(self):
        """نسخ ملفات الباك-إند"""
        print("🗄️  نسخ ملفات الباك-إند...")
        
        backend_files = [
            'backend_server.py',
            'auth_system.py',
            'config.py',
            'requirements.txt'
        ]
        
        for file_name in backend_files:
            src = self.project_root / file_name
            if src.exists():
                dst = self.deploy_dir / 'backend' / file_name
                shutil.copy2(src, dst)
                print(f"  ✅ {file_name}")
            else:
                print(f"  ⚠️  {file_name} غير موجود")
        
        print("✅ تم نسخ ملفات الباك-إند")
    
    def copy_frontend_files(self):
        """نسخ ملفات الفرونت-إند"""
        print("🌐 نسخ ملفات الفرونت-إند...")
        
        # نسخ مجلد لوحة التحكم
        dashboard_src = self.project_root / 'dashboard'
        dashboard_dst = self.deploy_dir / 'frontend' / 'dashboard'
        
        if dashboard_src.exists():
            shutil.copytree(dashboard_src, dashboard_dst)
            print("  ✅ لوحة التحكم")
        
        # نسخ مجلد الشات بوت
        chatbot_src = self.project_root / 'web-integration'
        chatbot_dst = self.deploy_dir / 'frontend' / 'web-integration'
        
        if chatbot_src.exists():
            shutil.copytree(chatbot_src, chatbot_dst)
            print("  ✅ الشات بوت")
        
        # نسخ الملفات الأساسية
        basic_files = [
            'index.html',
            'simple_server.py'
        ]
        
        for file_name in basic_files:
            src = self.project_root / file_name
            if src.exists():
                dst = self.deploy_dir / 'frontend' / file_name
                shutil.copy2(src, dst)
                print(f"  ✅ {file_name}")
        
        print("✅ تم نسخ ملفات الفرونت-إند")
    
    def create_production_config(self):
        """إنشاء ملف إعدادات الإنتاج"""
        print("⚙️  إنشاء إعدادات الإنتاج...")
        
        production_env = """# إعدادات الإنتاج
ENVIRONMENT=production
HOST=0.0.0.0
BACKEND_PORT=8001
FRONTEND_PORT=8000

# قاعدة البيانات
DATABASE_PATH=/var/lib/chatbot/chatbot_data.db
AUTH_DATABASE_PATH=/var/lib/chatbot/auth.db

# الأمان
SECRET_KEY=change-this-in-production-very-important
SESSION_TIMEOUT=3600

# AI
AI_PROVIDER=deepseek
AI_API_KEY=your-deepseek-api-key-here
AI_MODEL=deepseek-chat
AI_TEMPERATURE=0.7
AI_MAX_TOKENS=1000

# التسجيل
LOG_LEVEL=INFO
LOG_FILE=/var/log/chatbot/chatbot.log

# CORS
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# النسخ الاحتياطي
BACKUP_ENABLED=true
BACKUP_INTERVAL=3600
BACKUP_DIRECTORY=/var/backups/chatbot

# الإشعارات
EMAIL_ENABLED=false
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password

# الويب هوك
WEBHOOK_ENABLED=false
WEBHOOK_URL=https://hooks.slack.com/your-webhook-url
"""
        
        env_file = self.deploy_dir / 'config' / '.env.production'
        env_file.write_text(production_env, encoding='utf-8')
        
        print("✅ تم إنشاء ملف إعدادات الإنتاج")
    
    def create_deployment_scripts(self):
        """إنشاء سكريبتات النشر"""
        print("📜 إنشاء سكريبتات النشر...")
        
        # سكريبت تثبيت النظام
        install_script = """#!/bin/bash
# سكريبت تثبيت النظام على Ubuntu/Debian

echo "🚀 تثبيت نظام الشات بوت..."

# تحديث النظام
sudo apt update
sudo apt upgrade -y

# تثبيت Python
sudo apt install python3 python3-pip python3-venv -y

# إنشاء مستخدم النظام
sudo useradd -r -s /bin/false chatbot
sudo mkdir -p /var/lib/chatbot
sudo mkdir -p /var/log/chatbot
sudo mkdir -p /var/backups/chatbot
sudo chown chatbot:chatbot /var/lib/chatbot
sudo chown chatbot:chatbot /var/log/chatbot
sudo chown chatbot:chatbot /var/backups/chatbot

# إنشاء البيئة الافتراضية
sudo -u chatbot python3 -m venv /var/lib/chatbot/venv
sudo -u chatbot /var/lib/chatbot/venv/bin/pip install -r requirements.txt

# نسخ الملفات
sudo cp -r backend/* /var/lib/chatbot/
sudo cp -r frontend/* /var/lib/chatbot/frontend/
sudo cp config/.env.production /var/lib/chatbot/.env
sudo chown -R chatbot:chatbot /var/lib/chatbot

# إنشاء خدمات systemd
sudo cp scripts/chatbot-backend.service /etc/systemd/system/
sudo cp scripts/chatbot-frontend.service /etc/systemd/system/

# تفعيل الخدمات
sudo systemctl daemon-reload
sudo systemctl enable chatbot-backend
sudo systemctl enable chatbot-frontend

echo "✅ تم تثبيت النظام بنجاح!"
echo "لبدء النظام: sudo systemctl start chatbot-backend chatbot-frontend"
"""
        
        install_file = self.deploy_dir / 'scripts' / 'install.sh'
        install_file.write_text(install_script)
        install_file.chmod(0o755)
        
        # خدمة الباك-إند
        backend_service = """[Unit]
Description=Chatbot Backend Server
After=network.target

[Service]
Type=simple
User=chatbot
WorkingDirectory=/var/lib/chatbot
Environment=PATH=/var/lib/chatbot/venv/bin
EnvironmentFile=/var/lib/chatbot/.env
ExecStart=/var/lib/chatbot/venv/bin/python backend_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        
        backend_service_file = self.deploy_dir / 'scripts' / 'chatbot-backend.service'
        backend_service_file.write_text(backend_service)
        
        # خدمة الفرونت-إند
        frontend_service = """[Unit]
Description=Chatbot Frontend Server
After=network.target

[Service]
Type=simple
User=chatbot
WorkingDirectory=/var/lib/chatbot/frontend
Environment=PATH=/var/lib/chatbot/venv/bin
EnvironmentFile=/var/lib/chatbot/.env
ExecStart=/var/lib/chatbot/venv/bin/python simple_server.py --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        
        frontend_service_file = self.deploy_dir / 'scripts' / 'chatbot-frontend.service'
        frontend_service_file.write_text(frontend_service)
        
        print("✅ تم إنشاء سكريبتات النشر")
    
    def create_documentation(self):
        """إنشاء الوثائق"""
        print("📚 إنشاء الوثائق...")
        
        deployment_guide = """# دليل النشر

## متطلبات النظام

- Ubuntu 20.04+ أو Debian 11+
- Python 3.8+
- 1GB RAM على الأقل
- 5GB مساحة تخزين

## خطوات النشر

### 1. تحضير الخادم

```bash
# تحديث النظام
sudo apt update && sudo apt upgrade -y

# تثبيت المتطلبات
sudo apt install python3 python3-pip python3-venv nginx -y
```

### 2. تثبيت النظام

```bash
# نسخ ملفات النشر إلى الخادم
scp -r deploy/ user@server:/tmp/chatbot-deploy/

# تشغيل سكريبت التثبيت
cd /tmp/chatbot-deploy
sudo bash scripts/install.sh
```

### 3. إعداد Nginx (اختياري)

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/ {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 4. بدء النظام

```bash
sudo systemctl start chatbot-backend
sudo systemctl start chatbot-frontend
sudo systemctl status chatbot-backend chatbot-frontend
```

## المراقبة

```bash
# مراقبة السجلات
sudo journalctl -u chatbot-backend -f
sudo journalctl -u chatbot-frontend -f

# فحص حالة النظام
curl http://localhost:8001/api/health
curl http://localhost:8000
```

## النسخ الاحتياطي

```bash
# نسخ احتياطي يدوي
sudo -u chatbot cp /var/lib/chatbot/*.db /var/backups/chatbot/

# النسخ الاحتياطي التلقائي مفعل في الإعدادات
```

## الأمان

- غير كلمة مرور المستخدم الإداري
- غير SECRET_KEY في ملف .env
- استخدم HTTPS في الإنتاج
- قم بتحديث النظام بانتظام
"""
        
        docs_file = self.deploy_dir / 'docs' / 'DEPLOYMENT.md'
        docs_file.write_text(deployment_guide)
        
        print("✅ تم إنشاء الوثائق")
    
    def create_backup(self):
        """إنشاء نسخة احتياطية"""
        print("💾 إنشاء نسخة احتياطية...")
        
        if not self.backup_dir.exists():
            self.backup_dir.mkdir()
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"chatbot_backup_{timestamp}.zip"
        backup_path = self.backup_dir / backup_name
        
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in self.project_root.rglob('*'):
                if file_path.is_file() and not any(part.startswith('.') for part in file_path.parts):
                    if 'deploy' not in str(file_path) and 'backups' not in str(file_path):
                        arcname = file_path.relative_to(self.project_root)
                        zipf.write(file_path, arcname)
        
        print(f"✅ تم إنشاء النسخة الاحتياطية: {backup_name}")
    
    def create_deployment_package(self):
        """إنشاء حزمة النشر"""
        print("📦 إنشاء حزمة النشر...")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        package_name = f"chatbot_deploy_{timestamp}.zip"
        package_path = self.project_root / package_name
        
        with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in self.deploy_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(self.deploy_dir)
                    zipf.write(file_path, arcname)
        
        print(f"✅ تم إنشاء حزمة النشر: {package_name}")
        return package_path
    
    def deploy(self):
        """تنفيذ عملية النشر الكاملة"""
        self.print_header()
        
        try:
            self.create_backup()
            self.create_deploy_structure()
            self.copy_backend_files()
            self.copy_frontend_files()
            self.create_production_config()
            self.create_deployment_scripts()
            self.create_documentation()
            
            package_path = self.create_deployment_package()
            
            print(f"""
{'='*60}
🎉 تم تحضير النظام للنشر بنجاح!

📦 حزمة النشر: {package_path.name}
📁 مجلد النشر: {self.deploy_dir}

📋 الخطوات التالية:
1. ارفع حزمة النشر إلى الخادم
2. فك الضغط واتبع دليل النشر
3. قم بتشغيل سكريبت install.sh
4. اضبط الإعدادات في .env.production

📚 راجع ملف docs/DEPLOYMENT.md للتفاصيل

⚠️  تذكر:
- غير كلمة مرور المستخدم الإداري
- اضبط مفتاح DeepSeek API
- غير SECRET_KEY
- استخدم HTTPS في الإنتاج

🚀 النظام جاهز للنشر!
{'='*60}
            """)
            
        except Exception as e:
            print(f"❌ خطأ في عملية النشر: {e}")
            return False
        
        return True

if __name__ == "__main__":
    deployer = DeploymentManager()
    deployer.deploy()
