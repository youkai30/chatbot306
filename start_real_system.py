#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تشغيل النظام الحقيقي مع قاعدة البيانات
"""

import sys
import time
import subprocess
import webbrowser
import threading
from pathlib import Path

def print_banner():
    """طباعة شعار النظام"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           🗄️  نظام الشات بوت الحقيقي                        ║
║                                                              ║
║                    مع قاعدة بيانات حقيقية                   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

🔄 بدء تشغيل النظام الحقيقي...
    """)

def check_requirements():
    """فحص المتطلبات"""
    print("🔍 فحص المتطلبات...")
    
    # فحص Python
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ مطلوب")
        return False
    
    print("✅ Python متاح")
    
    # فحص Flask
    try:
        import flask
        import flask_cors
        print("✅ Flask متاح")
    except ImportError:
        print("📦 تثبيت Flask...")
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', 'flask', 'flask-cors'
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("✅ تم تثبيت Flask")
        except:
            print("❌ فشل في تثبيت Flask")
            return False
    
    # فحص الملفات
    required_files = [
        'real_backend.py',
        'setup_database.py',
        'simple_server.py',
        'dashboard/index.html',
        'web-integration/chatbot-widget.html'
    ]
    
    missing = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing.append(file_path)
    
    if missing:
        print(f"❌ ملفات مفقودة: {missing}")
        return False
    
    print("✅ جميع الملفات موجودة")
    return True

def setup_database():
    """إعداد قاعدة البيانات"""
    if not Path('chatbot_data.db').exists():
        print("🗄️  إنشاء قاعدة البيانات...")
        try:
            result = subprocess.run([
                sys.executable, 'setup_database.py'
            ], capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode == 0:
                print("✅ تم إنشاء قاعدة البيانات")
                return True
            else:
                print(f"❌ فشل في إنشاء قاعدة البيانات: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ خطأ في إنشاء قاعدة البيانات: {e}")
            return False
    else:
        print("✅ قاعدة البيانات موجودة")
        return True

def start_real_backend():
    """تشغيل الباك-إند الحقيقي"""
    print("🗄️  تشغيل الباك-إند الحقيقي...")
    
    try:
        process = subprocess.Popen([
            sys.executable, 'real_backend.py'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        time.sleep(5)
        
        # فحص إذا كان يعمل
        if process.poll() is None:
            print("✅ الباك-إند الحقيقي يعمل على http://localhost:8001")
            return process
        else:
            print("❌ فشل في تشغيل الباك-إند الحقيقي")
            return None
    except Exception as e:
        print(f"❌ خطأ في تشغيل الباك-إند: {e}")
        return None

def start_frontend():
    """تشغيل الفرونت-إند"""
    print("🌐 تشغيل الفرونت-إند...")
    
    try:
        process = subprocess.Popen([
            sys.executable, 'simple_server.py', '--port', '8000'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        time.sleep(3)
        
        if process.poll() is None:
            print("✅ الفرونت-إند يعمل على http://localhost:8000")
            return process
        else:
            print("❌ فشل في تشغيل الفرونت-إند")
            return None
    except Exception as e:
        print(f"❌ خطأ في تشغيل الفرونت-إند: {e}")
        return None

def test_system():
    """اختبار النظام"""
    print("\n🧪 اختبار الاتصال...")
    
    try:
        import requests
        
        # اختبار الباك-إند
        try:
            response = requests.get('http://localhost:8001/api/health', timeout=5)
            if response.ok:
                print("✅ الباك-إند الحقيقي يستجيب")
            else:
                print("⚠️  الباك-إند لا يستجيب بشكل صحيح")
        except:
            print("⚠️  الباك-إند قد يحتاج وقت إضافي للبدء")
        
        # اختبار الفرونت-إند
        try:
            response = requests.get('http://localhost:8000', timeout=5)
            if response.ok:
                print("✅ الفرونت-إند يستجيب")
            else:
                print("⚠️  الفرونت-إند لا يستجيب بشكل صحيح")
        except:
            print("⚠️  الفرونت-إند غير متاح")
            
    except ImportError:
        print("⚠️  مكتبة requests غير مثبتة، تخطي الاختبار")

def open_browser():
    """فتح المتصفح"""
    def open_delayed():
        time.sleep(3)
        try:
            webbrowser.open('http://localhost:8000/dashboard/index.html')
            print("✅ تم فتح لوحة التحكم في المتصفح")
        except:
            print("⚠️  لم يتم فتح المتصفح تلقائياً")
    
    thread = threading.Thread(target=open_delayed)
    thread.daemon = True
    thread.start()

def main():
    """الدالة الرئيسية"""
    print_banner()
    
    # فحص المتطلبات
    if not check_requirements():
        input("اضغط Enter للخروج...")
        return
    
    # إعداد قاعدة البيانات
    if not setup_database():
        input("اضغط Enter للخروج...")
        return
    
    print("\n🚀 تشغيل المكونات...")
    
    # تشغيل الباك-إند الحقيقي
    backend_process = start_real_backend()
    
    # تشغيل الفرونت-إند
    frontend_process = start_frontend()
    
    if not backend_process or not frontend_process:
        print("\n❌ فشل في تشغيل المكونات الأساسية")
        
        # إيقاف العمليات المتبقية
        if backend_process:
            backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()
        
        input("اضغط Enter للخروج...")
        return
    
    # اختبار النظام
    test_system()
    
    # فتح المتصفح
    print("\n🌐 فتح المتصفح...")
    open_browser()
    
    print(f"""
{'='*60}
🎉 النظام الحقيقي يعمل بنجاح!

🗄️  الباك-إند الحقيقي:
   📊 الإحصائيات: http://localhost:8001/api/stats
   💬 الشات API: http://localhost:8001/api/chat
   🔍 فحص الصحة: http://localhost:8001/api/health

🌐 الفرونت-إند:
   🏠 الصفحة الرئيسية: http://localhost:8000
   💬 الشات بوت: http://localhost:8000/web-integration/chatbot-widget.html
   📊 لوحة التحكم: http://localhost:8000/dashboard/index.html

💡 المميزات الحقيقية:
   ✅ قاعدة بيانات SQLite حقيقية
   ✅ بيانات تُحفظ مع كل رسالة
   ✅ إحصائيات مباشرة ومحدثة
   ✅ محادثات مؤرخة ومنظمة

🔐 بيانات الدخول:
   اسم المستخدم: admin
   كلمة المرور: admin123

⌨️  اضغط Ctrl+C للإيقاف
{'='*60}
    """)
    
    try:
        # انتظار الإيقاف
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 إيقاف النظام...")
        
        if backend_process:
            backend_process.terminate()
            print("✅ تم إيقاف الباك-إند الحقيقي")
        
        if frontend_process:
            frontend_process.terminate()
            print("✅ تم إيقاف الفرونت-إند")
        
        print("👋 تم إيقاف جميع العمليات")

if __name__ == "__main__":
    main()
