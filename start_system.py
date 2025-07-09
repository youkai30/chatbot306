#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تشغيل النظام المبسط والمضمون
"""

import sys
import time
import subprocess
import webbrowser
import threading
from pathlib import Path

def check_python():
    """فحص Python"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ مطلوب")
        return False
    print(f"✅ Python {sys.version.split()[0]}")
    return True

def check_files():
    """فحص الملفات المطلوبة"""
    required_files = [
        'simple_server.py',
        'ai-agent/simple_run.py',
        'web-integration/chatbot-widget.html',
        'dashboard/index.html'
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

def install_requirements():
    """تثبيت المتطلبات الأساسية"""
    try:
        import requests
        print("✅ المكتبات مثبتة")
        return True
    except ImportError:
        print("📦 تثبيت المكتبات...")
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', 'requests'
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("✅ تم تثبيت المكتبات")
            return True
        except:
            print("⚠️  لم يتم تثبيت requests، سيعمل النظام بدونها")
            return True

def start_ai_agent():
    """تشغيل AI Agent"""
    try:
        print("🤖 تشغيل AI Agent...")
        process = subprocess.Popen([
            sys.executable, 'ai-agent/simple_run.py',
            '--host', 'localhost', '--port', '5000'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        time.sleep(3)
        
        # فحص إذا كان يعمل
        if process.poll() is None:
            print("✅ AI Agent يعمل على http://localhost:5000")
            return process
        else:
            print("⚠️  AI Agent لم يبدأ، سيعمل النظام بدونه")
            return None
    except Exception as e:
        print(f"⚠️  خطأ في تشغيل AI Agent: {e}")
        return None

def start_main_server():
    """تشغيل الخادم الرئيسي"""
    try:
        print("🌐 تشغيل الخادم الرئيسي...")
        process = subprocess.Popen([
            sys.executable, 'simple_server.py', '--port', '8000'
        ])
        
        time.sleep(2)
        print("✅ الخادم يعمل على http://localhost:8000")
        return process
    except Exception as e:
        print(f"❌ خطأ في تشغيل الخادم: {e}")
        return None

def open_browser():
    """فتح المتصفح"""
    def open_delayed():
        time.sleep(3)
        try:
            webbrowser.open('http://localhost:8000')
            print("✅ تم فتح المتصفح")
        except:
            print("⚠️  لم يتم فتح المتصفح تلقائياً")
            print("   افتح يدوياً: http://localhost:8000")
    
    thread = threading.Thread(target=open_delayed)
    thread.daemon = True
    thread.start()

def main():
    """الدالة الرئيسية"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           🚀 تشغيل النظام المبسط والمضمون                   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

🔍 فحص النظام...
    """)
    
    # فحص المتطلبات
    if not check_python() or not check_files():
        print("\n❌ لا يمكن تشغيل النظام")
        input("اضغط Enter للخروج...")
        return
    
    install_requirements()
    
    print("\n🚀 تشغيل المكونات...")
    
    # تشغيل AI Agent (اختياري)
    ai_agent_process = start_ai_agent()
    
    # تشغيل الخادم الرئيسي
    main_process = start_main_server()
    
    if not main_process:
        print("\n❌ فشل في تشغيل الخادم الرئيسي")
        if ai_agent_process:
            ai_agent_process.terminate()
        input("اضغط Enter للخروج...")
        return
    
    # فتح المتصفح
    open_browser()
    
    print(f"""
{'='*60}
🎉 النظام يعمل بنجاح!

📋 الخدمات المتاحة:
   🏠 الصفحة الرئيسية: http://localhost:8000
   💬 الشات بوت: http://localhost:8000/web-integration/chatbot-widget.html
   📊 لوحة التحكم: http://localhost:8000/dashboard/index.html
   🤖 AI Agent: http://localhost:5000 {"(يعمل)" if ai_agent_process else "(غير متاح)"}

💡 نصائح:
   - جرب الشات بوت: "مرحبا"، "الوقت"، "مساعدة"
   - جرب AI Agent: "افتح المفكرة"، "التقط لقطة شاشة"
   - راقب الإحصائيات في لوحة التحكم

⌨️  اضغط Ctrl+C للإيقاف
{'='*60}
    """)
    
    try:
        # انتظار الإيقاف
        main_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 إيقاف النظام...")
        
        if main_process:
            main_process.terminate()
            print("✅ تم إيقاف الخادم الرئيسي")
        
        if ai_agent_process:
            ai_agent_process.terminate()
            print("✅ تم إيقاف AI Agent")
        
        print("👋 تم إيقاف جميع العمليات")

if __name__ == "__main__":
    main()
