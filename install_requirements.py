#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تثبيت المكتبات المطلوبة للنظام الآمن
"""

import subprocess
import sys
import os

def install_package(package):
    """تثبيت مكتبة واحدة"""
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        print(f"✅ تم تثبيت {package}")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ فشل في تثبيت {package}")
        return False

def main():
    print("📦 تثبيت المكتبات المطلوبة للنظام الآمن...")
    
    # قائمة المكتبات المطلوبة
    required_packages = [
        'flask',
        'flask-cors', 
        'requests',
        'PyJWT',  # للـ JWT tokens
        'python-dotenv'  # لقراءة ملف .env (اختياري)
    ]
    
    failed_packages = []
    
    for package in required_packages:
        print(f"\n📦 تثبيت {package}...")
        if not install_package(package):
            failed_packages.append(package)
    
    print(f"\n{'='*50}")
    if failed_packages:
        print(f"❌ فشل في تثبيت: {', '.join(failed_packages)}")
        print("يرجى تثبيتها يدوياً:")
        for package in failed_packages:
            print(f"  pip install {package}")
        return False
    else:
        print("✅ تم تثبيت جميع المكتبات بنجاح!")
        return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 النظام جاهز للتشغيل!")
    else:
        print("\n⚠️  يرجى إصلاح مشاكل التثبيت أولاً")
    
    input("\nاضغط Enter للمتابعة...")
