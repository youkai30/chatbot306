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
        # 'simple_server.py', # تم الإزالة
        'dashboard/index.html', # للتأكد من وجود الواجهات
        'web-integration/chatbot-widget.html' # للتأكد من وجود الواجهات
    ]
    
    missing = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing.append(file_path)
    
    if missing:
        print(f"❌ ملفات مفقودة: {missing}")
        return False
    
    print("✅ جميع الملفات الأساسية موجودة")
    return True

def setup_database():
    """إعداد قاعدة البيانات"""
    if not Path('chatbot_data.db').exists():
        print("🗄️  إنشاء قاعدة البيانات...")
        try:
            result = subprocess.run([
                sys.executable, 'setup_database.py'
            ], capture_output=True, text=True, encoding='utf-8') # Python 3.7+
            
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

def start_unified_backend(): # تم تغيير الاسم
    """تشغيل الباك-إند الموحد (API + واجهة أمامية)"""
    print("🗄️  تشغيل الباك-إند الموحد (real_backend.py)...")
    backend_port = "8001" # قيمة افتراضية
    try:
        from secure_config import config
        backend_port = str(config.backend_port)
    except Exception:
        print(f"⚠️ لم يتمكن من قراءة المنفذ من secure_config، سيستخدم المنفذ الافتراضي: {backend_port}")

    try:
        process = subprocess.Popen([
            sys.executable, 'real_backend.py'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        time.sleep(5)
        
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
#     return True


def test_system():
    """اختبار النظام"""
    print("\n🧪 اختبار الاتصال...")
    backend_port = "8001" # قيمة افتراضية
    try:
        from secure_config import config
        backend_port = str(config.backend_port)
    except Exception:
        pass
    
    try:
        import requests
        
        # اختبار الباك-إند الموحد
        try:
            response = requests.get(f'http://localhost:{backend_port}/api/health', timeout=5)
            if response.ok:
                print(f"✅ الباك-إند الموحد يستجيب على http://localhost:{backend_port}")
            else:
                print(f"⚠️  الباك-إند الموحد لا يستجيب بشكل صحيح على http://localhost:{backend_port}")
        except:
            print(f"⚠️  الباك-إند الموحد قد يحتاج وقت إضافي للبدء على http://localhost:{backend_port}")
            
    except ImportError:
        print("⚠️  مكتبة requests غير مثبتة، تخطي الاختبار")

def open_browser():
    """فتح المتصفح"""
    backend_port = "8001" # قيمة افتراضية
    try:
        from secure_config import config
        backend_port = str(config.backend_port)
    except Exception:
        pass

    def open_delayed():
        time.sleep(3)
        try:
            webbrowser.open(f'http://localhost:{backend_port}/dashboard/index.html')
            print(f"✅ تم فتح لوحة التحكم في المتصفح على http://localhost:{backend_port}/dashboard/index.html")
        except:
            print(f"⚠️  لم يتم فتح المتصفح تلقائياً. قم بزيارة http://localhost:{backend_port}/dashboard/index.html")
    
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
    
    # تشغيل الباك-إند الموحد
    unified_backend_process = start_unified_backend() # تم التغيير
        
    if not unified_backend_process: # تم التغيير
        print("\n❌ فشل في تشغيل الباك-إند الموحد (المكون الأساسي)")
        input("اضغط Enter للخروج...")
        return
    
    # اختبار النظام
    test_system()
    
    # فتح المتصفح
    print("\n🌐 فتح المتصفح...")
    open_browser()

    backend_port = "8001" # قيمة افتراضية
    try:
        from secure_config import config
        backend_port = str(config.backend_port)
    except Exception:
        pass
    
    print(f"""
{'='*60}
🎉 النظام الحقيقي الموحد يعمل بنجاح!

🗄️  الباك-إند الموحد (API + واجهة أمامية):
   🏠 الصفحة الرئيسية: http://localhost:{backend_port}/
   💬 الشات بوت: http://localhost:{backend_port}/web-integration/chatbot-widget.html
   📊 لوحة التحكم: http://localhost:{backend_port}/dashboard/index.html
   📈 الإحصائيات API: http://localhost:{backend_port}/api/stats
   💬 الشات API: http://localhost:{backend_port}/api/chat
   🔍 فحص الصحة API: http://localhost:{backend_port}/api/health

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
            # يمكن إضافة فحص لحالة العملية هنا إذا أردنا إيقاف السكريبت إذا توقفت العملية
            if unified_backend_process.poll() is not None:
                print("⚠️  الباك-إند الموحد توقف بشكل غير متوقع.")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 إيقاف النظام...")
        
        if unified_backend_process and unified_backend_process.poll() is None: # التأكد أن العملية لا تزال تعمل قبل محاولة الإيقاف
            unified_backend_process.terminate()
            try:
                unified_backend_process.wait(timeout=5) # انتظار الإيقاف
                print("✅ تم إيقاف الباك-إند الموحد")
            except subprocess.TimeoutExpired:
                unified_backend_process.kill() # إجبار على الإيقاف إذا لم يستجب
                print("🔴 تم إنهاء الباك-إند الموحد بالقوة")
        else:
            print("ℹ️ الباك-إند الموحد لم يكن يعمل أو توقف بالفعل.")

        print("👋 تم إيقاف جميع العمليات")

if __name__ == "__main__":
    main()
