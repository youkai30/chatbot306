#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
خادم مبسط وفعال للنظام
يعمل بشكل مضمون ومستقر
"""

import json
import time
import threading
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socketserver

# بيانات النظام المباشرة
SYSTEM_DATA = {
    'conversations': [],
    'users': {},
    'stats': {
        'total_conversations': 0,
        'active_users': 0,
        'messages_today': 0,
        'response_time': 1.2,
        'satisfaction_rate': 94.5,
        'start_time': time.time()
    },
    'channels': {
        'website': 0,
        'whatsapp': 0,
        'telegram': 0,
        'messenger': 0,
        'instagram': 0
    }
}

class SmartChatbotHandler(SimpleHTTPRequestHandler):
    """معالج طلبات الشات بوت المحسن"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(Path.cwd()), **kwargs)
    
    def do_POST(self):
        """معالجة طلبات POST"""
        if self.path == '/api/chat':
            self.handle_chat()
        elif self.path == '/api/agent':
            self.handle_agent_command()
        else:
            self.send_error(404)
    
    def do_GET(self):
        """معالجة طلبات GET"""
        if self.path == '/':
            self.path = '/index.html'
        elif self.path == '/api/health':
            self.handle_health()
        elif self.path == '/api/stats':
            self.handle_stats()
        elif self.path.startswith('/api/'):
            self.send_error(404)
        else:
            super().do_GET()
    
    def handle_chat(self):
        """معالجة رسائل الشات"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            message = data.get('message', '').strip()
            user_id = data.get('user_id', 'anonymous')
            session_id = data.get('session_id', 'default')
            
            # معالجة الرسالة
            response = self.process_message(message)
            
            # تسجيل المحادثة
            self.log_conversation(user_id, session_id, message, response)
            
            # إرسال الرد
            self.send_json({
                'success': True,
                'response': response,
                'timestamp': time.time(),
                'user_id': user_id,
                'session_id': session_id
            })
            
        except Exception as e:
            self.send_json({'success': False, 'error': str(e)}, 500)
    
    def handle_agent_command(self):
        """معالجة أوامر AI Agent"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            command = data.get('command', '').strip()
            
            # محاولة إرسال للـ AI Agent
            try:
                import requests
                response = requests.post('http://localhost:5000/api/execute', 
                                       json={'command': command}, 
                                       timeout=10)
                if response.ok:
                    agent_result = response.json()
                    self.send_json({
                        'success': True,
                        'response': agent_result.get('result', 'تم تنفيذ الأمر'),
                        'source': 'ai_agent'
                    })
                    return
            except:
                pass
            
            # إذا فشل AI Agent، استخدم معالجة محلية
            result = self.process_system_command(command)
            self.send_json({
                'success': True,
                'response': result,
                'source': 'local'
            })
            
        except Exception as e:
            self.send_json({'success': False, 'error': str(e)}, 500)
    
    def handle_health(self):
        """فحص صحة النظام"""
        uptime = time.time() - SYSTEM_DATA['stats']['start_time']
        
        # فحص AI Agent
        ai_agent_status = 'offline'
        try:
            import requests
            response = requests.get('http://localhost:5000/api/health', timeout=3)
            if response.ok:
                ai_agent_status = 'online'
        except:
            pass
        
        self.send_json({
            'status': 'healthy',
            'uptime': uptime,
            'ai_agent': ai_agent_status,
            'total_conversations': SYSTEM_DATA['stats']['total_conversations'],
            'active_users': len(SYSTEM_DATA['users']),
            'timestamp': time.time()
        })
    
    def handle_stats(self):
        """إرسال الإحصائيات"""
        # تحديث الإحصائيات
        SYSTEM_DATA['stats']['active_users'] = len(SYSTEM_DATA['users'])
        SYSTEM_DATA['stats']['messages_today'] = len(SYSTEM_DATA['conversations'])
        
        # إضافة بيانات الساعات
        current_hour = time.strftime('%H:00')
        hourly_stats = []
        for i in range(12):
            hour = f"{i:02d}:00"
            messages = len([c for c in SYSTEM_DATA['conversations'] 
                          if c.get('hour', '') == hour])
            hourly_stats.append({'hour': hour, 'messages': messages})
        
        self.send_json({
            **SYSTEM_DATA['stats'],
            'channels': SYSTEM_DATA['channels'],
            'hourly_stats': hourly_stats,
            'recent_chats': self.get_recent_chats()
        })
    
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
            return 'الطقس اليوم مشمس وجميل! 🌞 درجة الحرارة 25°م'
        
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
            # إرسال للـ AI Agent
            try:
                import requests
                response = requests.post('http://localhost:5000/api/execute', 
                                       json={'command': message}, 
                                       timeout=10)
                if response.ok:
                    result = response.json()
                    return f"🤖 AI Agent: {result.get('result', 'تم تنفيذ الأمر')}"
            except:
                pass
            
            return 'هذا أمر نظام! سيتم تمريره للوكيل الذكي (AI Agent) للتنفيذ... 🤖'
        
        else:
            return f'شكراً لرسالتك: "{message}". أنا هنا لمساعدتك! جرب أن تسألني عن الوقت أو الطقس أو اطلب المساعدة. 💬'
    
    def process_system_command(self, command):
        """معالجة أوامر النظام محلياً"""
        command_lower = command.lower()
        
        if 'مرحبا' in command_lower:
            return 'مرحباً! أنا الوكيل الذكي المحلي.'
        elif 'وقت' in command_lower:
            return f'الوقت الحالي: {time.strftime("%Y-%m-%d %H:%M:%S")}'
        else:
            return f'تم استلام الأمر: "{command}". AI Agent غير متاح، تم المعالجة محلياً.'
    
    def log_conversation(self, user_id, session_id, message, response):
        """تسجيل المحادثة"""
        conversation = {
            'user_id': user_id,
            'session_id': session_id,
            'user_message': message,
            'bot_response': response,
            'timestamp': time.time(),
            'hour': time.strftime('%H:00'),
            'channel': 'website'
        }
        
        SYSTEM_DATA['conversations'].append(conversation)
        SYSTEM_DATA['stats']['total_conversations'] += 1
        SYSTEM_DATA['channels']['website'] += 1
        
        # تسجيل المستخدم
        if user_id not in SYSTEM_DATA['users']:
            SYSTEM_DATA['users'][user_id] = {
                'first_seen': time.time(),
                'message_count': 0,
                'last_seen': time.time()
            }
        
        SYSTEM_DATA['users'][user_id]['message_count'] += 1
        SYSTEM_DATA['users'][user_id]['last_seen'] = time.time()
    
    def get_recent_chats(self):
        """الحصول على المحادثات الحديثة"""
        recent = SYSTEM_DATA['conversations'][-5:] if SYSTEM_DATA['conversations'] else []
        
        formatted_chats = []
        for chat in recent:
            time_diff = time.time() - chat['timestamp']
            if time_diff < 60:
                time_str = f"منذ {int(time_diff)} ثانية"
            elif time_diff < 3600:
                time_str = f"منذ {int(time_diff/60)} دقيقة"
            else:
                time_str = f"منذ {int(time_diff/3600)} ساعة"
            
            formatted_chats.append({
                'time': time_str,
                'user': chat['user_id'],
                'channel': chat['channel'],
                'message': chat['user_message'][:50] + '...' if len(chat['user_message']) > 50 else chat['user_message'],
                'status': 'resolved'
            })
        
        return formatted_chats
    
    def send_json(self, data, status=200):
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

def run_server(port=8000):
    """تشغيل الخادم"""
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                🌐 خادم النظام المبسط                        ║
║                                                              ║
║                    يعمل بشكل مضمون                          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

🚀 تشغيل الخادم على المنفذ {port}...

📋 الخدمات المتاحة:
   🏠 الصفحة الرئيسية: http://localhost:{port}
   💬 الشات بوت: http://localhost:{port}/web-integration/chatbot-widget.html
   📊 لوحة التحكم: http://localhost:{port}/dashboard/index.html
   🔍 فحص الصحة: http://localhost:{port}/api/health
   📈 الإحصائيات: http://localhost:{port}/api/stats

⌨️  اضغط Ctrl+C للإيقاف
{'='*60}
    """)
    
    try:
        with socketserver.TCPServer(("", port), SmartChatbotHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 تم إيقاف الخادم")
    except Exception as e:
        print(f"❌ خطأ في الخادم: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="خادم النظام المبسط")
    parser.add_argument('--port', type=int, default=8000, help='منفذ الخادم')
    
    args = parser.parse_args()
    run_server(args.port)
