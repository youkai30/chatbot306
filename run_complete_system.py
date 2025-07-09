#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تشغيل النظام الكامل
تشغيل جميع مكونات النظام: الخادم الرئيسي، AI Agent، لوحة التحكم
"""

import os
import sys
import time
import subprocess
import webbrowser
import threading
from pathlib import Path

class CompleteSystemRunner:
    """مشغل النظام الكامل"""
    
    def __init__(self):
        self.processes = []
        self.project_root = Path.cwd()
        
    def print_banner(self):
        """طباعة شعار النظام"""
        print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           🚀 نظام الشات بوت متعدد القنوات                   ║
║                                                              ║
║                    تشغيل النظام الكامل                      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

🔄 بدء تشغيل جميع المكونات...
        """)
        
    def check_requirements(self):
        """فحص المتطلبات"""
        print("🔍 فحص المتطلبات...")
        
        # فحص Python
        if sys.version_info < (3, 8):
            print("❌ Python 3.8+ مطلوب")
            return False
            
        # فحص الملفات المطلوبة
        required_files = [
            'server.py',
            'ai-agent/simple_run.py',
            'web-integration/chatbot-widget.html',
            'dashboard/index.html'
        ]
        
        missing_files = []
        for file_path in required_files:
            if not (self.project_root / file_path).exists():
                missing_files.append(file_path)
                
        if missing_files:
            print(f"❌ ملفات مفقودة: {missing_files}")
            return False
            
        # فحص المكتبات
        try:
            import flask
            import requests
            print("✅ جميع المتطلبات متوفرة")
            return True
        except ImportError as e:
            print(f"❌ مكتبة مفقودة: {e}")
            print("💡 قم بتشغيل: python setup.py")
            return False
            
    def start_ai_agent(self):
        """تشغيل AI Agent"""
        print("🤖 تشغيل AI Agent...")
        
        try:
            ai_agent_path = self.project_root / 'ai-agent' / 'simple_run.py'
            process = subprocess.Popen([
                sys.executable, str(ai_agent_path),
                '--host', 'localhost',
                '--port', '5000'
            ], cwd=self.project_root)
            
            self.processes.append(('AI Agent', process))
            
            # انتظار للتشغيل
            time.sleep(3)
            
            # فحص إذا كان يعمل
            try:
                import requests
                response = requests.get('http://localhost:5000/api/health', timeout=5)
                if response.status_code == 200:
                    print("✅ AI Agent يعمل على http://localhost:5000")
                    return True
                else:
                    print("⚠️  AI Agent يعمل لكن هناك مشكلة في الاستجابة")
                    return True
            except:
                print("⚠️  AI Agent قيد التشغيل...")
                return True
                
        except Exception as e:
            print(f"❌ خطأ في تشغيل AI Agent: {e}")
            return False
            
    def start_main_server(self):
        """تشغيل الخادم الرئيسي"""
        print("🌐 تشغيل الخادم الرئيسي...")
        
        try:
            server_path = self.project_root / 'server.py'
            process = subprocess.Popen([
                sys.executable, str(server_path),
                '--port', '8000'
            ], cwd=self.project_root)
            
            self.processes.append(('Main Server', process))
            
            # انتظار للتشغيل
            time.sleep(3)
            
            print("✅ الخادم الرئيسي يعمل على http://localhost:8000")
            return True
            
        except Exception as e:
            print(f"❌ خطأ في تشغيل الخادم الرئيسي: {e}")
            return False
            
    def open_browser_tabs(self):
        """فتح علامات تبويب المتصفح"""
        print("🌐 فتح المتصفح...")
        
        urls = [
            ('الصفحة الرئيسية', 'http://localhost:8000'),
            ('الشات بوت', 'http://localhost:8000/web-integration/chatbot-widget.html'),
            ('لوحة التحكم', 'http://localhost:8000/dashboard/index.html'),
            ('AI Agent', 'http://localhost:5000')
        ]
        
        def open_url_delayed(name, url, delay):
            time.sleep(delay)
            try:
                webbrowser.open(url)
                print(f"✅ تم فتح {name}: {url}")
            except Exception as e:
                print(f"⚠️  لم يتم فتح {name}: {e}")
                print(f"   يمكنك فتحه يدوياً: {url}")
        
        # فتح الروابط بتأخير
        for i, (name, url) in enumerate(urls):
            thread = threading.Thread(
                target=open_url_delayed, 
                args=(name, url, i * 2)
            )
            thread.daemon = True
            thread.start()
            
    def print_status(self):
        """طباعة حالة النظام"""
        print(f"""
{'='*60}
🎉 النظام يعمل بنجاح!

📋 الخدمات المتاحة:
   🏠 الصفحة الرئيسية: http://localhost:8000
   💬 الشات بوت: http://localhost:8000/web-integration/chatbot-widget.html
   📊 لوحة التحكم: http://localhost:8000/dashboard/index.html
   🤖 AI Agent: http://localhost:5000
   🔍 فحص الصحة: http://localhost:8000/api/health
   📈 الإحصائيات: http://localhost:8000/api/stats

💡 نصائح الاستخدام:
   - جرب الشات بوت بكتابة "مرحبا" أو "الوقت"
   - استخدم AI Agent لأوامر النظام مثل "افتح المفكرة"
   - راقب الإحصائيات في لوحة التحكم
   - جميع البيانات تجريبية ولا تحتاج إعداد APIs

🔧 العمليات الجارية:
        """)
        
        for name, process in self.processes:
            status = "🟢 يعمل" if process.poll() is None else "🔴 متوقف"
            print(f"   {name}: {status}")
            
        print(f"""
⌨️  اضغط Ctrl+C للإيقاف
{'='*60}
        """)
        
    def wait_for_exit(self):
        """انتظار إشارة الإيقاف"""
        try:
            while True:
                time.sleep(1)
                # فحص العمليات
                for name, process in self.processes:
                    if process.poll() is not None:
                        print(f"⚠️  {name} توقف بشكل غير متوقع")
        except KeyboardInterrupt:
            print("\n🛑 إيقاف النظام...")
            self.stop_all_processes()
            
    def stop_all_processes(self):
        """إيقاف جميع العمليات"""
        print("🔄 إيقاف جميع العمليات...")
        
        for name, process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ تم إيقاف {name}")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"🔴 تم إنهاء {name} بالقوة")
            except Exception as e:
                print(f"⚠️  خطأ في إيقاف {name}: {e}")
                
        print("👋 تم إيقاف جميع العمليات")
        
    def run(self):
        """تشغيل النظام الكامل"""
        self.print_banner()
        
        # فحص المتطلبات
        if not self.check_requirements():
            print("\n❌ لا يمكن تشغيل النظام بسبب متطلبات مفقودة")
            print("💡 قم بتشغيل: python setup.py")
            return
            
        # تشغيل المكونات
        success = True
        
        if not self.start_ai_agent():
            success = False
            
        if not self.start_main_server():
            success = False
            
        if not success:
            print("\n❌ فشل في تشغيل بعض المكونات")
            self.stop_all_processes()
            return
            
        # فتح المتصفح
        self.open_browser_tabs()
        
        # طباعة الحالة
        self.print_status()
        
        # انتظار الإيقاف
        self.wait_for_exit()

def main():
    """الدالة الرئيسية"""
    runner = CompleteSystemRunner()
    runner.run()

if __name__ == "__main__":
    main()
