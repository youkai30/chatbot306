#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار شامل للنظام
فحص جميع مكونات الشات بوت والوكيل الذكي
"""

import os
import sys
import json
import time
import requests
import subprocess
from pathlib import Path
from typing import Dict, List, Any

class SystemTester:
    """فئة اختبار النظام"""
    
    def __init__(self):
        self.results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'errors': [],
            'warnings': [],
            'start_time': time.time()
        }
        
    def print_header(self):
        """طباعة رأس الاختبار"""
        print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                🧪 اختبار النظام الشامل                      ║
║                                                              ║
║              فحص الشات بوت والوكيل الذكي                    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """)
        
    def test_file_structure(self):
        """اختبار هيكل الملفات"""
        print("🔍 فحص هيكل الملفات...")
        
        required_files = [
            'README.md',
            'index.html',
            'web-integration/chatbot-widget.html',
            'web-integration/chatbot-widget.css',
            'web-integration/chatbot-widget.js',
            'ai-agent/simple_run.py',
            'ai-agent/requirements.txt',
            'config/deepseek-config.json',
            'config/project-config.json',
            'n8n-workflows/chatbot-deepseek.json'
        ]
        
        missing_files = []
        for file_path in required_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)
                
        if missing_files:
            self.results['errors'].append(f"ملفات مفقودة: {missing_files}")
            print(f"❌ ملفات مفقودة: {len(missing_files)}")
            for file in missing_files:
                print(f"   - {file}")
            return False
        else:
            print("✅ جميع الملفات المطلوبة موجودة")
            return True
            
    def test_config_files(self):
        """اختبار ملفات الإعداد"""
        print("⚙️  فحص ملفات الإعداد...")
        
        config_files = [
            'config/deepseek-config.json',
            'config/project-config.json',
            'config/test-config.json',
            'config/security-config.json'
        ]
        
        valid_configs = 0
        for config_file in config_files:
            try:
                if Path(config_file).exists():
                    with open(config_file, 'r', encoding='utf-8') as f:
                        json.load(f)
                    print(f"✅ {config_file}")
                    valid_configs += 1
                else:
                    print(f"⚠️  {config_file} غير موجود")
                    self.results['warnings'].append(f"ملف الإعداد غير موجود: {config_file}")
            except json.JSONDecodeError as e:
                print(f"❌ {config_file} - خطأ في JSON: {e}")
                self.results['errors'].append(f"خطأ في {config_file}: {e}")
                
        return valid_configs > 0
        
    def test_chatbot_files(self):
        """اختبار ملفات الشات بوت"""
        print("💬 فحص ملفات الشات بوت...")
        
        # فحص HTML
        html_file = Path('web-integration/chatbot-widget.html')
        if html_file.exists():
            content = html_file.read_text(encoding='utf-8')
            if 'chatbot-widget.css' in content and 'chatbot-widget.js' in content:
                print("✅ ملف HTML صحيح")
            else:
                print("❌ ملف HTML لا يحتوي على الروابط المطلوبة")
                return False
        else:
            print("❌ ملف HTML غير موجود")
            return False
            
        # فحص CSS
        css_file = Path('web-integration/chatbot-widget.css')
        if css_file.exists():
            content = css_file.read_text(encoding='utf-8')
            if '.chatbot-container' in content and '.chatbot-toggle' in content:
                print("✅ ملف CSS صحيح")
            else:
                print("❌ ملف CSS لا يحتوي على الفئات المطلوبة")
                return False
        else:
            print("❌ ملف CSS غير موجود")
            return False
            
        # فحص JavaScript
        js_file = Path('web-integration/chatbot-widget.js')
        if js_file.exists():
            content = js_file.read_text(encoding='utf-8')
            if 'SmartChatbot' in content and 'sendMessage' in content:
                print("✅ ملف JavaScript صحيح")
            else:
                print("❌ ملف JavaScript لا يحتوي على الفئات المطلوبة")
                return False
        else:
            print("❌ ملف JavaScript غير موجود")
            return False
            
        return True
        
    def test_ai_agent_setup(self):
        """اختبار إعداد الوكيل الذكي"""
        print("🤖 فحص إعداد الوكيل الذكي...")
        
        # فحص ملف التشغيل المبسط
        simple_run = Path('ai-agent/simple_run.py')
        if simple_run.exists():
            print("✅ ملف التشغيل المبسط موجود")
        else:
            print("❌ ملف التشغيل المبسط غير موجود")
            return False
            
        # فحص requirements.txt
        requirements = Path('ai-agent/requirements.txt')
        if requirements.exists():
            content = requirements.read_text(encoding='utf-8')
            if 'Flask' in content and 'pyautogui' in content:
                print("✅ ملف المتطلبات صحيح")
            else:
                print("❌ ملف المتطلبات ناقص")
                return False
        else:
            print("❌ ملف المتطلبات غير موجود")
            return False
            
        return True
        
    def test_python_dependencies(self):
        """اختبار المكتبات المطلوبة"""
        print("📦 فحص المكتبات المطلوبة...")
        
        required_packages = ['flask', 'requests']
        optional_packages = ['pyautogui', 'pillow']
        
        missing_required = []
        missing_optional = []
        
        for package in required_packages:
            try:
                __import__(package)
                print(f"✅ {package}")
            except ImportError:
                missing_required.append(package)
                print(f"❌ {package} غير مثبت")
                
        for package in optional_packages:
            try:
                __import__(package)
                print(f"✅ {package}")
            except ImportError:
                missing_optional.append(package)
                print(f"⚠️  {package} غير مثبت (اختياري)")
                
        if missing_required:
            self.results['errors'].append(f"مكتبات مطلوبة غير مثبتة: {missing_required}")
            return False
            
        if missing_optional:
            self.results['warnings'].append(f"مكتبات اختيارية غير مثبتة: {missing_optional}")
            
        return True
        
    def test_ai_agent_startup(self):
        """اختبار تشغيل الوكيل الذكي"""
        print("🚀 اختبار تشغيل الوكيل الذكي...")
        
        try:
            # محاولة تشغيل الوكيل الذكي لفترة قصيرة
            process = subprocess.Popen(
                [sys.executable, 'ai-agent/simple_run.py', '--host', 'localhost', '--port', '5001'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=Path.cwd()
            )
            
            # انتظار قصير للتشغيل
            time.sleep(3)
            
            # فحص إذا كان يعمل
            try:
                response = requests.get('http://localhost:5001/api/health', timeout=5)
                if response.status_code == 200:
                    print("✅ الوكيل الذكي يعمل بنجاح")
                    result = True
                else:
                    print(f"❌ الوكيل الذكي يعمل لكن يرجع خطأ: {response.status_code}")
                    result = False
            except requests.exceptions.RequestException:
                print("❌ لا يمكن الاتصال بالوكيل الذكي")
                result = False
                
            # إيقاف العملية
            process.terminate()
            process.wait(timeout=5)
            
            return result
            
        except Exception as e:
            print(f"❌ خطأ في تشغيل الوكيل الذكي: {e}")
            self.results['errors'].append(f"خطأ في تشغيل الوكيل الذكي: {e}")
            return False
            
    def run_all_tests(self):
        """تشغيل جميع الاختبارات"""
        self.print_header()
        
        tests = [
            ("هيكل الملفات", self.test_file_structure),
            ("ملفات الإعداد", self.test_config_files),
            ("ملفات الشات بوت", self.test_chatbot_files),
            ("إعداد الوكيل الذكي", self.test_ai_agent_setup),
            ("المكتبات المطلوبة", self.test_python_dependencies),
            ("تشغيل الوكيل الذكي", self.test_ai_agent_startup)
        ]
        
        for test_name, test_func in tests:
            print(f"\n{'='*60}")
            print(f"🧪 اختبار: {test_name}")
            print('='*60)
            
            self.results['total_tests'] += 1
            
            try:
                if test_func():
                    self.results['passed_tests'] += 1
                    print(f"✅ نجح اختبار: {test_name}")
                else:
                    self.results['failed_tests'] += 1
                    print(f"❌ فشل اختبار: {test_name}")
            except Exception as e:
                self.results['failed_tests'] += 1
                self.results['errors'].append(f"خطأ في اختبار {test_name}: {e}")
                print(f"❌ خطأ في اختبار {test_name}: {e}")
                
        self.print_summary()
        
    def print_summary(self):
        """طباعة ملخص النتائج"""
        duration = time.time() - self.results['start_time']
        
        print(f"\n{'='*60}")
        print("📊 ملخص نتائج الاختبار")
        print('='*60)
        print(f"⏱️  مدة الاختبار: {duration:.2f} ثانية")
        print(f"📝 إجمالي الاختبارات: {self.results['total_tests']}")
        print(f"✅ الاختبارات الناجحة: {self.results['passed_tests']}")
        print(f"❌ الاختبارات الفاشلة: {self.results['failed_tests']}")
        print(f"⚠️  التحذيرات: {len(self.results['warnings'])}")
        print(f"🚨 الأخطاء: {len(self.results['errors'])}")
        
        if self.results['warnings']:
            print("\n⚠️  التحذيرات:")
            for warning in self.results['warnings']:
                print(f"   - {warning}")
                
        if self.results['errors']:
            print("\n🚨 الأخطاء:")
            for error in self.results['errors']:
                print(f"   - {error}")
                
        # تقييم عام
        success_rate = (self.results['passed_tests'] / self.results['total_tests']) * 100
        
        print(f"\n📈 معدل النجاح: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("🎉 ممتاز! النظام جاهز للاستخدام")
        elif success_rate >= 70:
            print("👍 جيد! النظام يعمل مع بعض التحسينات المطلوبة")
        elif success_rate >= 50:
            print("⚠️  متوسط! يحتاج النظام لإصلاحات")
        else:
            print("🚨 ضعيف! النظام يحتاج لإصلاحات جوهرية")
            
        print("\n" + "="*60)

if __name__ == "__main__":
    tester = SystemTester()
    tester.run_all_tests()
