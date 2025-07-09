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
        'real_backend.py', # تم التغيير
        # 'simple_server.py', # تم الإزالة
        'ai-agent/simple_run.py',
        'web-integration/chatbot-widget.html', # للتأكد من وجود الواجهات التي سيخدمها real_backend
        'dashboard/index.html' # للتأكد من وجود الواجهات التي سيخدمها real_backend
    ]
    
    missing = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing.append(file_path)
    
    if missing:
        print(f"❌ ملفات مفقودة: {missing}")
        return False
    
    print("✅ جميع المتطلبات الأساسية متوفرة")
    return True

def start_unified_backend(): # تم تغيير اسم الدالة والمحتوى
    """تشغيل الباك-إند الموحد (API + واجهة أمامية)"""
    print("🗄️  تشغيل الباك-إند الموحد (real_backend.py)...")
    
    try:
        # محاولة قراءة المنفذ من .env إذا أمكن، وإلا استخدام الافتراضي 8001
        backend_port = "8001" # قيمة افتراضية
        try:
            from secure_config import config
            backend_port = str(config.backend_port)
        except Exception:
            print(f"⚠️ لم يتمكن من قراءة المنفذ من secure_config، سيستخدم المنفذ الافتراضي: {backend_port}")

        process = subprocess.Popen([
            sys.executable, 'real_backend.py' # تم التغيير
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        time.sleep(5) # زيادة وقت الانتظار قليلاً لأن Flask قد يستغرق وقتًا أطول للبدء
        
        # فحص إذا كان يعمل
        if process.poll() is None:
            print(f"✅ الباك-إند الموحد يعمل (يفترض على http://localhost:{backend_port})")
            return process
        else:
            print("❌ فشل في تشغيل الباك-إند الموحد (real_backend.py)")
            return None
    except Exception as e:
        print(f"❌ خطأ في تشغيل الباك-إند الموحد: {e}")
        return None

# def start_frontend(): # تم تعطيل هذه الدالة
#     """تشغيل الفرونت-إند"""
#     print("🌐 (الفرونت-إند الآن يُخدم بواسطة الباك-إند الموحد)")
#     return True # إرجاع True للإشارة إلى أنه "بدأ" ضمنيًا


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
        backend_port = "8001" # قيمة افتراضية
        try:
            from secure_config import config
            backend_port = str(config.backend_port)
        except Exception:
            pass # استخدام الافتراضي

        urls = [
            ('الصفحة الرئيسية', f'http://localhost:{backend_port}/'),
            ('الشات بوت', f'http://localhost:{backend_port}/web-integration/chatbot-widget.html'),
            ('لوحة التحكم', f'http://localhost:{backend_port}/dashboard/index.html'),
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
        
        backend_port = "8001" # قيمة افتراضية
        try:
            from secure_config import config
            backend_port = str(config.backend_port)
        except Exception:
            pass

        # اختبار الباك-إند الموحد
        try:
            response = requests.get(f'http://localhost:{backend_port}/api/health', timeout=5)
            if response.ok:
                print(f"✅ الباك-إند الموحد يستجيب على http://localhost:{backend_port}")
            else:
                print(f"⚠️  الباك-إند الموحد لا يستجيب بشكل صحيح على http://localhost:{backend_port}")
        except:
            print(f"❌ الباك-إند الموحد غير متاح على http://localhost:{backend_port}")
        
        # اختبار AI Agent
        try:
            response = requests.get('http://localhost:5000/api/health', timeout=5) # افترض أن AI Agent لديه health endpoint
            if response.ok:
                print("✅ AI Agent يستجيب")
            else:
                print("⚠️  AI Agent لا يستجيب بشكل صحيح")
        except:
            print("⚠️  AI Agent غير متاح أو لا يوجد لديه /api/health")
            
    except ImportError:
        print("⚠️  مكتبة requests غير مثبتة، تخطي الاختبار")

def print_system_status(processes):
    """طباعة حالة النظام"""
    backend_port = "8001" # قيمة افتراضية
    try:
        from secure_config import config
        backend_port = str(config.backend_port)
    except Exception:
        pass

    print(f"""
{'='*60}
🎉 النظام الموحد يعمل بنجاح!

🗄️  الباك-إند الموحد (API + واجهة أمامية):
   🏠 الصفحة الرئيسية: http://localhost:{backend_port}/
   💬 الشات بوت: http://localhost:{backend_port}/web-integration/chatbot-widget.html
   📊 لوحة التحكم: http://localhost:{backend_port}/dashboard/index.html
   📈 الإحصائيات API: http://localhost:{backend_port}/api/stats
   💬 الشات API: http://localhost:{backend_port}/api/chat
   🔍 فحص الصحة API: http://localhost:{backend_port}/api/health

🤖 AI Agent:
   🔧 واجهة التحكم: http://localhost:5000 (إذا كان يعمل)

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
    
    # تشغيل الباك-إند الموحد
    processes['الباك-إند الموحد'] = start_unified_backend() # تم التغيير
    
    # الفرونت-إند لم يعد عملية منفصلة
    # processes['الفرونت-إند'] = start_frontend() # تم التعليق
    
    # تشغيل AI Agent (اختياري)
    processes['AI Agent'] = start_ai_agent()
    
    # فحص إذا كان الباك-إند الموحد يعمل
    if not processes['الباك-إند الموحد']: # تم التغيير
        print("\n❌ فشل في تشغيل الباك-إند الموحد (المكون الأساسي)")
        
        # إيقاف العمليات المتبقية
        if processes.get('AI Agent'):
            if processes['AI Agent']:
                processes['AI Agent'].terminate()
        
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
