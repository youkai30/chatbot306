#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تشغيل النظام الكامل مع الباك-إند الحقيقي
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
║           🚀 نظام الشات بوت الكامل مع باك-إند حقيقي         ║
║                                                              ║
║                    🗄️  قاعدة بيانات + APIs                  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

🔄 بدء تشغيل النظام الكامل...
    """)

def check_requirements():
    """فحص المتطلبات"""
    print("🔍 فحص المتطلبات...")
    
    # فحص Python
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ مطلوب")
        return False
    
    # فحص الملفات
    required_files = [
        'backend_server.py',
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
    
    print("✅ جميع المتطلبات متوفرة")
    return True

def start_backend():
    """تشغيل الباك-إند الحقيقي"""
    print("🗄️  تشغيل الباك-إند الحقيقي...")
    
    try:
        process = subprocess.Popen([
            sys.executable, 'backend_server.py'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        time.sleep(3)
        
        # فحص إذا كان يعمل
        if process.poll() is None:
            print("✅ الباك-إند يعمل على http://localhost:8001")
            return process
        else:
            print("❌ فشل في تشغيل الباك-إند")
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
        
        time.sleep(2)
        
        if process.poll() is None:
            print("✅ الفرونت-إند يعمل على http://localhost:8000")
            return process
        else:
            print("❌ فشل في تشغيل الفرونت-إند")
            return None
    except Exception as e:
        print(f"❌ خطأ في تشغيل الفرونت-إند: {e}")
        return None

def start_ai_agent():
    """تشغيل AI Agent"""
    print("🤖 تشغيل AI Agent...")
    
    try:
        process = subprocess.Popen([
            sys.executable, 'ai-agent/simple_run.py',
            '--host', 'localhost', '--port', '5000'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        time.sleep(3)
        
        if process.poll() is None:
            print("✅ AI Agent يعمل على http://localhost:5000")
            return process
        else:
            print("⚠️  AI Agent لم يبدأ، سيعمل النظام بدونه")
            return None
    except Exception as e:
        print(f"⚠️  خطأ في تشغيل AI Agent: {e}")
        return None

def open_browser_tabs():
    """فتح علامات تبويب المتصفح"""
    def open_delayed():
        time.sleep(5)
        
        urls = [
            ('الصفحة الرئيسية', 'http://localhost:8000'),
            ('الشات بوت', 'http://localhost:8000/web-integration/chatbot-widget.html'),
            ('لوحة التحكم', 'http://localhost:8000/dashboard/index.html'),
        ]
        
        for name, url in urls:
            try:
                webbrowser.open(url)
                print(f"✅ تم فتح {name}")
                time.sleep(1)
            except:
                print(f"⚠️  لم يتم فتح {name} تلقائياً: {url}")
    
    thread = threading.Thread(target=open_delayed)
    thread.daemon = True
    thread.start()

def test_system():
    """اختبار النظام"""
    print("\n🧪 اختبار النظام...")
    
    try:
        import requests
        
        # اختبار الباك-إند
        try:
            response = requests.get('http://localhost:8001/api/health', timeout=5)
            if response.ok:
                print("✅ الباك-إند يستجيب")
            else:
                print("⚠️  الباك-إند لا يستجيب بشكل صحيح")
        except:
            print("❌ الباك-إند غير متاح")
        
        # اختبار الفرونت-إند
        try:
            response = requests.get('http://localhost:8000', timeout=5)
            if response.ok:
                print("✅ الفرونت-إند يستجيب")
            else:
                print("⚠️  الفرونت-إند لا يستجيب بشكل صحيح")
        except:
            print("❌ الفرونت-إند غير متاح")
        
        # اختبار AI Agent
        try:
            response = requests.get('http://localhost:5000/api/health', timeout=5)
            if response.ok:
                print("✅ AI Agent يستجيب")
            else:
                print("⚠️  AI Agent لا يستجيب بشكل صحيح")
        except:
            print("⚠️  AI Agent غير متاح")
            
    except ImportError:
        print("⚠️  مكتبة requests غير مثبتة، تخطي الاختبار")

def print_system_status(processes):
    """طباعة حالة النظام"""
    print(f"""
{'='*60}
🎉 النظام يعمل بنجاح!

🗄️  الباك-إند الحقيقي:
   📊 الإحصائيات: http://localhost:8001/api/stats
   💬 الشات API: http://localhost:8001/api/chat
   🔍 فحص الصحة: http://localhost:8001/api/health

🌐 الفرونت-إند:
   🏠 الصفحة الرئيسية: http://localhost:8000
   💬 الشات بوت: http://localhost:8000/web-integration/chatbot-widget.html
   📊 لوحة التحكم: http://localhost:8000/dashboard/index.html

🤖 AI Agent:
   🔧 واجهة التحكم: http://localhost:5000

💡 المميزات الجديدة:
   ✅ قاعدة بيانات SQLite حقيقية
   ✅ بيانات واقعية ومباشرة
   ✅ إحصائيات تتحدث مع كل رسالة
   ✅ محادثات محفوظة ومؤرخة
   ✅ تكامل كامل بين جميع المكونات

🔧 العمليات الجارية:
    """)
    
    for name, process in processes.items():
        if process and process.poll() is None:
            print(f"   {name}: 🟢 يعمل")
        else:
            print(f"   {name}: 🔴 متوقف")
    
    print(f"""
⌨️  اضغط Ctrl+C للإيقاف
{'='*60}
    """)

def main():
    """الدالة الرئيسية"""
    print_banner()
    
    # فحص المتطلبات
    if not check_requirements():
        input("اضغط Enter للخروج...")
        return
    
    print("\n🚀 تشغيل المكونات...")
    
    # تشغيل المكونات
    processes = {}
    
    # تشغيل الباك-إند
    processes['الباك-إند'] = start_backend()
    
    # تشغيل الفرونت-إند
    processes['الفرونت-إند'] = start_frontend()
    
    # تشغيل AI Agent (اختياري)
    processes['AI Agent'] = start_ai_agent()
    
    # فحص إذا كان الباك-إند والفرونت-إند يعملان
    if not processes['الباك-إند'] or not processes['الفرونت-إند']:
        print("\n❌ فشل في تشغيل المكونات الأساسية")
        
        # إيقاف العمليات المتبقية
        for process in processes.values():
            if process:
                process.terminate()
        
        input("اضغط Enter للخروج...")
        return
    
    # اختبار النظام
    test_system()
    
    # فتح المتصفح
    print("\n🌐 فتح المتصفح...")
    open_browser_tabs()
    
    # طباعة حالة النظام
    print_system_status(processes)
    
    try:
        # انتظار الإيقاف
        while True:
            time.sleep(1)
            # فحص العمليات
            for name, process in processes.items():
                if process and process.poll() is not None:
                    print(f"⚠️  {name} توقف بشكل غير متوقع")
    except KeyboardInterrupt:
        print("\n🛑 إيقاف النظام...")
        
        # إيقاف جميع العمليات
        for name, process in processes.items():
            if process:
                try:
                    process.terminate()
                    process.wait(timeout=5)
                    print(f"✅ تم إيقاف {name}")
                except:
                    process.kill()
                    print(f"🔴 تم إنهاء {name} بالقوة")
        
        print("👋 تم إيقاف جميع العمليات")

if __name__ == "__main__":
    main()
