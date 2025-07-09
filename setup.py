#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت إعداد البيئة البرمجية الشامل
تثبيت وإعداد جميع المتطلبات للنظام
"""

import os
import sys
import subprocess
import json
from pathlib import Path

class SystemSetup:
    """فئة إعداد النظام"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.errors = []
        self.warnings = []
        
    def print_header(self):
        """طباعة رأس الإعداد"""
        print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                ⚙️  إعداد البيئة البرمجية                    ║
║                                                              ║
║              نظام الشات بوت متعدد القنوات                   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """)
        
    def check_python_version(self):
        """فحص إصدار Python"""
        print("🐍 فحص إصدار Python...")
        
        if sys.version_info < (3, 8):
            self.errors.append(f"Python 3.8+ مطلوب، الإصدار الحالي: {sys.version}")
            print(f"❌ Python 3.8+ مطلوب، الإصدار الحالي: {sys.version}")
            return False
        else:
            print(f"✅ Python {sys.version.split()[0]} - ممتاز!")
            return True
            
    def create_directories(self):
        """إنشاء المجلدات المطلوبة"""
        print("📁 إنشاء المجلدات المطلوبة...")
        
        directories = [
            'logs',
            'temp', 
            'data',
            'uploads',
            'backups',
            'ai-agent/logs',
            'ai-agent/temp',
            'ai-agent/data'
        ]
        
        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ {directory}")
            
        return True
        
    def install_python_packages(self):
        """تثبيت حزم Python"""
        print("📦 تثبيت حزم Python...")
        
        # الحزم الأساسية
        basic_packages = [
            'flask>=2.3.0',
            'requests>=2.31.0',
            'flask-cors>=4.0.0'
        ]
        
        # الحزم الاختيارية
        optional_packages = [
            'pyautogui>=0.9.54',
            'pillow>=10.0.0',
            'opencv-python>=4.8.0',
            'numpy>=1.24.0'
        ]
        
        # تثبيت الحزم الأساسية
        for package in basic_packages:
            try:
                print(f"📦 تثبيت {package}...")
                subprocess.check_call([
                    sys.executable, '-m', 'pip', 'install', package
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"✅ {package}")
            except subprocess.CalledProcessError:
                self.errors.append(f"فشل تثبيت {package}")
                print(f"❌ فشل تثبيت {package}")
                
        # تثبيت الحزم الاختيارية
        for package in optional_packages:
            try:
                print(f"📦 تثبيت {package} (اختياري)...")
                subprocess.check_call([
                    sys.executable, '-m', 'pip', 'install', package
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"✅ {package}")
            except subprocess.CalledProcessError:
                self.warnings.append(f"لم يتم تثبيت {package} (اختياري)")
                print(f"⚠️  لم يتم تثبيت {package} (اختياري)")
                
        return len(self.errors) == 0
        
    def setup_config_files(self):
        """إعداد ملفات التكوين"""
        print("⚙️  إعداد ملفات التكوين...")
        
        # التحقق من وجود ملفات الإعداد
        config_files = [
            'config/deepseek-config.json',
            'config/project-config.json',
            'config/server-config.json',
            'config/security-config.json'
        ]
        
        missing_configs = []
        for config_file in config_files:
            if not (self.project_root / config_file).exists():
                missing_configs.append(config_file)
                
        if missing_configs:
            self.warnings.append(f"ملفات إعداد مفقودة: {missing_configs}")
            print(f"⚠️  ملفات إعداد مفقودة: {len(missing_configs)}")
            for config in missing_configs:
                print(f"   - {config}")
        else:
            print("✅ جميع ملفات الإعداد موجودة")
            
        return True
        
    def test_imports(self):
        """اختبار استيراد المكتبات"""
        print("🧪 اختبار استيراد المكتبات...")
        
        # المكتبات الأساسية
        basic_imports = [
            ('flask', 'Flask'),
            ('requests', 'requests'),
            ('json', 'json'),
            ('pathlib', 'Path')
        ]
        
        # المكتبات الاختيارية
        optional_imports = [
            ('pyautogui', 'pyautogui'),
            ('PIL', 'Pillow'),
            ('cv2', 'OpenCV'),
            ('numpy', 'numpy')
        ]
        
        # اختبار المكتبات الأساسية
        for module, name in basic_imports:
            try:
                __import__(module)
                print(f"✅ {name}")
            except ImportError:
                self.errors.append(f"لا يمكن استيراد {name}")
                print(f"❌ لا يمكن استيراد {name}")
                
        # اختبار المكتبات الاختيارية
        for module, name in optional_imports:
            try:
                __import__(module)
                print(f"✅ {name}")
            except ImportError:
                self.warnings.append(f"لا يمكن استيراد {name} (اختياري)")
                print(f"⚠️  لا يمكن استيراد {name} (اختياري)")
                
        return len(self.errors) == 0
        
    def create_startup_scripts(self):
        """إنشاء سكريبتات التشغيل"""
        print("🚀 إنشاء سكريبتات التشغيل...")
        
        # سكريبت تشغيل Windows
        windows_script = """@echo off
echo Starting Smart Chatbot System...
echo.

echo Starting AI Agent...
start "AI Agent" python ai-agent/simple_run.py

echo Waiting for AI Agent to start...
timeout /t 3 /nobreak > nul

echo Starting Main Server...
python server.py

pause
"""
        
        # سكريبت تشغيل Linux/Mac
        unix_script = """#!/bin/bash
echo "Starting Smart Chatbot System..."
echo

echo "Starting AI Agent..."
python3 ai-agent/simple_run.py &
AI_AGENT_PID=$!

echo "Waiting for AI Agent to start..."
sleep 3

echo "Starting Main Server..."
python3 server.py

# Cleanup on exit
trap "kill $AI_AGENT_PID 2>/dev/null" EXIT
"""
        
        # كتابة السكريبتات
        try:
            with open('start.bat', 'w', encoding='utf-8') as f:
                f.write(windows_script)
            print("✅ start.bat (Windows)")
            
            with open('start.sh', 'w', encoding='utf-8') as f:
                f.write(unix_script)
            
            # جعل السكريبت قابل للتنفيذ على Unix
            if os.name != 'nt':
                os.chmod('start.sh', 0o755)
            print("✅ start.sh (Linux/Mac)")
            
        except Exception as e:
            self.warnings.append(f"لم يتم إنشاء سكريبتات التشغيل: {e}")
            print(f"⚠️  لم يتم إنشاء سكريبتات التشغيل: {e}")
            
        return True
        
    def run_setup(self):
        """تشغيل الإعداد الكامل"""
        self.print_header()
        
        steps = [
            ("فحص إصدار Python", self.check_python_version),
            ("إنشاء المجلدات", self.create_directories),
            ("تثبيت حزم Python", self.install_python_packages),
            ("إعداد ملفات التكوين", self.setup_config_files),
            ("اختبار المكتبات", self.test_imports),
            ("إنشاء سكريبتات التشغيل", self.create_startup_scripts)
        ]
        
        print("🔄 بدء عملية الإعداد...\n")
        
        for step_name, step_func in steps:
            print(f"{'='*60}")
            print(f"📋 {step_name}")
            print('='*60)
            
            try:
                if not step_func():
                    print(f"❌ فشل في: {step_name}")
                else:
                    print(f"✅ نجح: {step_name}")
            except Exception as e:
                self.errors.append(f"خطأ في {step_name}: {e}")
                print(f"❌ خطأ في {step_name}: {e}")
                
            print()
            
        self.print_summary()
        
    def print_summary(self):
        """طباعة ملخص الإعداد"""
        print(f"{'='*60}")
        print("📊 ملخص الإعداد")
        print('='*60)
        
        if not self.errors:
            print("🎉 تم الإعداد بنجاح!")
            print("\n🚀 خطوات التشغيل:")
            print("   1. تشغيل الخادم: python server.py")
            print("   2. أو استخدام: start.bat (Windows) / ./start.sh (Linux/Mac)")
            print("   3. فتح المتصفح: http://localhost:8000")
            
        else:
            print("🚨 هناك أخطاء تحتاج لإصلاح:")
            for error in self.errors:
                print(f"   ❌ {error}")
                
        if self.warnings:
            print(f"\n⚠️  تحذيرات ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   ⚠️  {warning}")
                
        print(f"\n{'='*60}")

if __name__ == "__main__":
    setup = SystemSetup()
    setup.run_setup()
