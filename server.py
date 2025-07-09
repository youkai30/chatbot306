#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
خادم التطوير المحلي المبسط والفعال
يدير جميع مكونات النظام بشكل مستقر
"""

import os
import sys
import json
import time
import threading
import subprocess
import requests
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import socketserver

class ChatbotHandler(SimpleHTTPRequestHandler):
    """معالج طلبات الشات بوت"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(Path.cwd()), **kwargs)
    
    def do_POST(self):
        """معالجة طلبات POST"""
        if self.path.startswith('/api/'):
            self.handle_api_request()
        else:
            self.send_error(404)
    
    def do_GET(self):
        """معالجة طلبات GET"""
        # إعادة توجيه الصفحة الرئيسية
        if self.path == '/':
            self.path = '/index.html'
        elif self.path.startswith('/api/'):
            self.handle_api_request()
        else:
            super().do_GET()
    
    def handle_api_request(self):
        """معالجة طلبات API"""
        try:
            if self.path == '/api/health':
                self.send_json_response({
                    'status': 'healthy',
                    'timestamp': time.time(),
                    'services': {
                        'chatbot': 'running',
                        'ai_agent': 'running',
                        'dashboard': 'running'
                    }
                })
            elif self.path == '/api/chat':
                self.handle_chat_request()
            elif self.path == '/api/stats':
                self.handle_stats_request()
            else:
                self.send_error(404, "API endpoint not found")
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)
    
    def handle_chat_request(self):
        """معالجة طلبات الدردشة"""
        if self.command == 'POST':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                message = data.get('message', '')
                
                # معالجة الرسالة وإرجاع رد
                response = self.process_message(message)
                
                self.send_json_response({
                    'success': True,
                    'response': response,
                    'timestamp': time.time()
                })
            except json.JSONDecodeError:
                self.send_json_response({'error': 'Invalid JSON'}, 400)
        else:
            self.send_error(405, "Method not allowed")
    
    def handle_stats_request(self):
        """معالجة طلبات الإحصائيات"""
        stats = {
            'total_conversations': 156,
            'active_users': 23,
            'messages_today': 342,
            'response_time': 1.2,
            'satisfaction_rate': 94.5,
            'channels': {
                'website': 45,
                'whatsapp': 32,
                'telegram': 28,
                'messenger': 18
            },
            'hourly_stats': [
                {'hour': '00:00', 'messages': 12},
                {'hour': '01:00', 'messages': 8},
                {'hour': '02:00', 'messages': 5},
                {'hour': '03:00', 'messages': 3},
                {'hour': '04:00', 'messages': 7},
                {'hour': '05:00', 'messages': 15},
                {'hour': '06:00', 'messages': 28},
                {'hour': '07:00', 'messages': 45},
                {'hour': '08:00', 'messages': 67},
                {'hour': '09:00', 'messages': 89},
                {'hour': '10:00', 'messages': 76},
                {'hour': '11:00', 'messages': 54}
            ]
        }
        self.send_json_response(stats)
    
    def process_message(self, message):
        """معالجة رسالة المستخدم"""
        message_lower = message.lower()
        
        # ردود ذكية
        if any(word in message_lower for word in ['مرحبا', 'السلام', 'أهلا', 'hello', 'hi']):
            return 'مرحباً بك! 👋 أنا المساعد الذكي. كيف يمكنني مساعدتك اليوم؟'
        
        elif any(word in message_lower for word in ['وقت', 'ساعة', 'time']):
            current_time = time.strftime('%H:%M:%S')
            return f'الوقت الحالي هو: {current_time} ⏰'
        
        elif any(word in message_lower for word in ['طقس', 'جو', 'weather']):
            return 'الطقس اليوم مشمس وجميل! 🌞 درجة الحرارة 25°م (هذا مثال تجريبي)'
        
        elif any(word in message_lower for word in ['مساعدة', 'help']):
            return '''يمكنني مساعدتك في:
• الإجابة على الأسئلة العامة
• معرفة الوقت والطقس  
• تقديم المعلومات
• التحكم في النظام (عبر AI Agent)

ما الذي تريد معرفته؟ 🤔'''
        
        elif any(word in message_lower for word in ['شكرا', 'شكراً', 'thanks']):
            return 'العفو! سعيد لمساعدتك 😊 هل تحتاج لأي شيء آخر؟'
        
        elif any(word in message_lower for word in ['افتح', 'التقط', 'اغلق']):
            return 'هذا أمر نظام! سيتم تمريره للوكيل الذكي (AI Agent) للتنفيذ... 🤖'
        
        else:
            return f'شكراً لرسالتك: "{message}". أنا هنا لمساعدتك! جرب أن تسألني عن الوقت أو الطقس أو اطلب المساعدة. 💬'
    
    def send_json_response(self, data, status=200):
        """إرسال استجابة JSON"""
        response = json.dumps(data, ensure_ascii=False, indent=2)
        
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        self.wfile.write(response.encode('utf-8'))
    
    def do_OPTIONS(self):
        """معالجة طلبات OPTIONS للـ CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

class DevelopmentServer:
    """خادم التطوير الشامل"""
    
    def __init__(self, port=8000):
        self.port = port
        self.ai_agent_process = None
        
    def start_ai_agent(self):
        """تشغيل AI Agent في الخلفية"""
        try:
            ai_agent_path = Path('ai-agent/simple_run.py')
            if ai_agent_path.exists():
                print("🤖 تشغيل AI Agent...")
                self.ai_agent_process = subprocess.Popen([
                    sys.executable, str(ai_agent_path), 
                    '--host', 'localhost', 
                    '--port', '5000'
                ], cwd=Path.cwd())
                time.sleep(2)  # انتظار للتشغيل
                print("✅ AI Agent يعمل على http://localhost:5000")
            else:
                print("⚠️  AI Agent غير موجود")
        except Exception as e:
            print(f"❌ خطأ في تشغيل AI Agent: {e}")
    
    def stop_ai_agent(self):
        """إيقاف AI Agent"""
        if self.ai_agent_process:
            self.ai_agent_process.terminate()
            self.ai_agent_process.wait()
            print("🛑 تم إيقاف AI Agent")
    
    def start(self):
        """تشغيل الخادم"""
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                🌐 خادم التطوير المحلي                       ║
║                                                              ║
║              نظام الشات بوت متعدد القنوات                   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

🚀 بدء تشغيل الخدمات...
        """)
        
        # تشغيل AI Agent
        self.start_ai_agent()
        
        # تشغيل الخادم الرئيسي
        try:
            with socketserver.TCPServer(("", self.port), ChatbotHandler) as httpd:
                print(f"""
📋 الخدمات المتاحة:
   🏠 الصفحة الرئيسية: http://localhost:{self.port}
   💬 الشات بوت: http://localhost:{self.port}/web-integration/chatbot-widget.html
   📊 لوحة التحكم: http://localhost:{self.port}/dashboard/index.html
   🤖 AI Agent: http://localhost:5000
   🔍 فحص الصحة: http://localhost:{self.port}/api/health
   📈 الإحصائيات: http://localhost:{self.port}/api/stats

💡 نصائح:
   - جميع الملفات متاحة عبر الخادم
   - API endpoints تعمل مع بيانات تجريبية
   - AI Agent يعمل بشكل منفصل على المنفذ 5000
   - استخدم Ctrl+C للإيقاف

⌨️  اضغط Ctrl+C للإيقاف
{'='*60}
                """)
                
                httpd.serve_forever()
                
        except KeyboardInterrupt:
            print("\n🛑 إيقاف الخادم...")
            self.stop_ai_agent()
            print("👋 تم إيقاف جميع الخدمات")
        except Exception as e:
            print(f"❌ خطأ في الخادم: {e}")
            self.stop_ai_agent()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="خادم التطوير المحلي الشامل")
    parser.add_argument('--port', type=int, default=8000, help='منفذ الخادم (افتراضي: 8000)')
    
    args = parser.parse_args()
    
    # إنشاء المجلدات المطلوبة
    Path('logs').mkdir(exist_ok=True)
    Path('temp').mkdir(exist_ok=True)
    
    # تشغيل الخادم
    server = DevelopmentServer(port=args.port)
    server.start()
