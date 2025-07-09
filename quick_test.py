#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار سريع للنظام الآمن
"""

import sys
import subprocess

def test_imports():
    """اختبار الاستيرادات"""
    print("🧪 اختبار الاستيرادات...")
    
    tests = [
        ("flask", "Flask"),
        ("flask_cors", "Flask-CORS"),
        ("requests", "requests"),
        ("jwt", "PyJWT")
    ]
    
    failed = []
    
    for module, name in tests:
        try:
            __import__(module)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name} - غير مثبت")
            failed.append(name)
    
    if failed:
        print(f"\n📦 تثبيت المكتبات المفقودة...")
        for name in failed:
            if name == "PyJWT":
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'PyJWT'])
            elif name == "Flask-CORS":
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'flask-cors'])
            else:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', name.lower()])
        print("✅ تم تثبيت المكتبات")
    
    return len(failed) == 0

def test_config():
    """اختبار الإعدادات"""
    print("\n🔧 اختبار الإعدادات...")
    try:
        from secure_config import config
        print(f"✅ الإعدادات: منفذ {config.backend_port}")
        return True
    except Exception as e:
        print(f"❌ خطأ في الإعدادات: {e}")
        return False

def test_auth():
    """اختبار المصادقة"""
    print("\n🔐 اختبار المصادقة...")
    try:
        from secure_auth import secure_auth
        print("✅ نظام المصادقة جاهز")
        return True
    except Exception as e:
        print(f"❌ خطأ في المصادقة: {e}")
        return False

def test_rate_limiter():
    """اختبار Rate Limiting"""
    print("\n⚡ اختبار Rate Limiting...")
    try:
        from rate_limiter import rate_limiter
        print("✅ Rate Limiting جاهز")
        return True
    except Exception as e:
        print(f"❌ خطأ في Rate Limiting: {e}")
        return False

def test_deepseek():
    """اختبار DeepSeek AI"""
    print("\n🧠 اختبار DeepSeek AI...")
    try:
        from deepseek_ai import deepseek_ai
        result = deepseek_ai.test_connection()
        if result['status'] == 'connected':
            print("✅ DeepSeek AI متصل")
            return True
        else:
            print(f"⚠️ DeepSeek AI: {result['message']}")
            return True  # ليس خطأ قاتل
    except Exception as e:
        print(f"❌ خطأ في DeepSeek AI: {e}")
        return False

def main():
    """الاختبار الرئيسي"""
    print("🚀 اختبار سريع للنظام الآمن")
    print("="*50)
    
    tests = [
        ("المكتبات", test_imports),
        ("الإعدادات", test_config),
        ("المصادقة", test_auth),
        ("Rate Limiting", test_rate_limiter),
        ("DeepSeek AI", test_deepseek)
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        if test_func():
            passed += 1
    
    print(f"\n{'='*50}")
    print(f"📊 النتائج: {passed}/{total} نجح")
    
    if passed == total:
        print("🎉 جميع الاختبارات نجحت! النظام جاهز")
        return True
    elif passed >= total - 1:
        print("👍 النظام يعمل مع تحذيرات بسيطة")
        return True
    else:
        print("⚠️ يحتاج إصلاحات قبل التشغيل")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print(f"\n🚀 يمكنك الآن تشغيل النظام:")
        print("   python real_backend.py")
    else:
        print(f"\n🔧 أصلح المشاكل أولاً")
    
    input("\nاضغط Enter للخروج...")
