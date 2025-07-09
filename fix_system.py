#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت فحص وإصلاح النظام
يكتشف ويصلح المشاكل الشائعة تلقائياً
"""

import os
import sys
import sqlite3
import subprocess
from pathlib import Path

def print_header():
    """طباعة رأس الفحص"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                🔧 فحص وإصلاح النظام                         ║
║                                                              ║
║              اكتشاف وإصلاح المشاكل تلقائياً                ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

🔍 بدء فحص النظام...
    """)

def check_python():
    """فحص Python"""
    print("🐍 فحص Python...")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ مطلوب")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} متاح")
    return True

def check_and_install_packages():
    """فحص وتثبيت المكتبات المطلوبة"""
    print("📦 فحص المكتبات المطلوبة...")
    
    required_packages = {
        'flask': 'Flask',
        'flask_cors': 'Flask-CORS',
        'requests': 'requests'
    }
    
    missing_packages = []
    
    for package, pip_name in required_packages.items():
        try:
            __import__(package)
            print(f"✅ {pip_name} متاح")
        except ImportError:
            missing_packages.append(pip_name)
            print(f"❌ {pip_name} غير متاح")
    
    if missing_packages:
        print(f"📦 تثبيت المكتبات المفقودة: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install'
            ] + missing_packages, stdout=subprocess.DEVNULL)
            print("✅ تم تثبيت جميع المكتبات")
            return True
        except subprocess.CalledProcessError:
            print("❌ فشل في تثبيت المكتبات")
            return False
    
    return True

def check_files():
    """فحص الملفات المطلوبة"""
    print("📁 فحص الملفات المطلوبة...")
    
    required_files = [
        'real_backend.py',
        'deepseek_ai.py',
        'setup_database.py',
        'simple_server.py',
        'web-integration/chatbot-widget.html',
        'web-integration/chatbot-widget.js',
        'dashboard/index.html'
    ]
    
    missing_files = []
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"❌ {file_path} غير موجود")
    
    if missing_files:
        print(f"⚠️  ملفات مفقودة: {len(missing_files)}")
        return False
    
    print("✅ جميع الملفات موجودة")
    return True

def check_database():
    """فحص قاعدة البيانات"""
    print("🗄️  فحص قاعدة البيانات...")
    
    db_path = Path('chatbot_data.db')
    
    if not db_path.exists():
        print("❌ قاعدة البيانات غير موجودة")
        return create_database()
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # فحص الجداول المطلوبة
        required_tables = ['conversations', 'users', 'daily_stats']
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        missing_tables = [t for t in required_tables if t not in existing_tables]
        
        if missing_tables:
            print(f"❌ جداول مفقودة: {missing_tables}")
            conn.close()
            return create_database()
        
        # فحص البيانات
        cursor.execute("SELECT COUNT(*) FROM conversations")
        conv_count = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"✅ قاعدة البيانات سليمة ({conv_count} محادثة)")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في قاعدة البيانات: {e}")
        return create_database()

def create_database():
    """إنشاء قاعدة البيانات"""
    print("🔧 إنشاء قاعدة البيانات...")
    
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

def test_deepseek_ai():
    """اختبار DeepSeek AI"""
    print("🧠 اختبار DeepSeek AI...")
    
    try:
        from deepseek_ai import deepseek_ai
        
        # اختبار الاتصال
        test_result = deepseek_ai.test_connection()
        
        if test_result['status'] == 'connected':
            print("✅ DeepSeek AI يعمل بنجاح")
            return True
        else:
            print(f"⚠️  DeepSeek AI: {test_result['message']}")
            print("   سيعمل النظام بالردود الاحتياطية")
            return True  # ليس خطأ قاتل
            
    except Exception as e:
        print(f"❌ خطأ في DeepSeek AI: {e}")
        print("   سيعمل النظام بالردود الاحتياطية")
        return True  # ليس خطأ قاتل

def test_backend():
    """اختبار الباك-إند"""
    print("🌐 اختبار الباك-إند...")
    
    try:
        # محاولة استيراد الباك-إند
        import real_backend
        print("✅ الباك-إند يمكن تحميله")
        return True
    except Exception as e:
        print(f"❌ خطأ في الباك-إند: {e}")
        return False

def fix_permissions():
    """إصلاح صلاحيات الملفات"""
    print("🔐 فحص الصلاحيات...")
    
    try:
        # فحص إمكانية الكتابة في المجلد الحالي
        test_file = Path('test_write.tmp')
        test_file.write_text('test')
        test_file.unlink()
        
        print("✅ صلاحيات الكتابة متاحة")
        return True
    except Exception as e:
        print(f"❌ مشكلة في الصلاحيات: {e}")
        return False

def generate_report(results):
    """إنشاء تقرير الفحص"""
    print(f"\n{'='*60}")
    print("📊 تقرير فحص النظام")
    print('='*60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    success_rate = (passed / total) * 100
    
    print(f"📝 إجمالي الفحوصات: {total}")
    print(f"✅ نجح: {passed}")
    print(f"❌ فشل: {total - passed}")
    print(f"📈 معدل النجاح: {success_rate:.1f}%")
    
    print(f"\n📋 تفاصيل الفحص:")
    for check_name, result in results.items():
        status = "✅" if result else "❌"
        print(f"  {status} {check_name}")
    
    if success_rate >= 90:
        print("\n🎉 ممتاز! النظام جاهز للعمل")
        recommendation = "يمكنك تشغيل النظام الآن"
    elif success_rate >= 70:
        print("\n👍 جيد! النظام يعمل مع بعض التحذيرات")
        recommendation = "النظام سيعمل، لكن راجع التحذيرات"
    else:
        print("\n⚠️  يحتاج إصلاح! مشاكل جوهرية")
        recommendation = "أصلح المشاكل قبل التشغيل"
    
    print(f"💡 التوصية: {recommendation}")
    
    return success_rate >= 70

def main():
    """الدالة الرئيسية"""
    print_header()
    
    # تشغيل الفحوصات
    results = {}
    
    results['Python'] = check_python()
    results['المكتبات'] = check_and_install_packages()
    results['الملفات'] = check_files()
    results['قاعدة البيانات'] = check_database()
    results['DeepSeek AI'] = test_deepseek_ai()
    results['الباك-إند'] = test_backend()
    results['الصلاحيات'] = fix_permissions()
    
    # إنشاء التقرير
    system_ready = generate_report(results)
    
    if system_ready:
        print(f"\n🚀 النظام جاهز! يمكنك تشغيله بـ:")
        print("   START_AI_SYSTEM.bat")
        print("   أو: python real_backend.py")
    else:
        print(f"\n🔧 أصلح المشاكل أولاً ثم أعد تشغيل الفحص")
    
    print(f"\n{'='*60}")
    
    return system_ready

if __name__ == "__main__":
    main()
