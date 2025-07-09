#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام DeepSeek AI الحقيقي
تكامل مع DeepSeek API للذكاء الاصطناعي
"""

import requests
import time
import sqlite3
from datetime import datetime
from typing import Dict, List
from secure_config import config
import logging

logger = logging.getLogger(__name__)

class DeepSeekAI:
    """فئة التكامل مع DeepSeek AI"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or config.deepseek_api_key
        self.base_url = "https://api.deepseek.com/v1"
        self.model = config.get('DEEPSEEK_MODEL', 'deepseek-chat')
        self.max_tokens = config.get_int('DEEPSEEK_MAX_TOKENS', 1000)
        self.temperature = float(config.get('DEEPSEEK_TEMPERATURE', '0.7'))

        if not self.api_key or self.api_key == 'your-deepseek-api-key-here':
            logger.error("مفتاح DeepSeek API غير صحيح!")
            raise ValueError("يرجى تحديث مفتاح DeepSeek API في ملف .env")
        
        # إعدادات الشخصية
        self.system_prompt = """أنت مساعد ذكي ومفيد باللغة العربية. 
خصائصك:
- تجيب بطريقة ودودة ومهذبة
- تقدم معلومات دقيقة ومفيدة
- تساعد في خدمة العملاء والدعم الفني
- تتحدث العربية بطلاقة
- تستخدم الرموز التعبيرية بشكل مناسب
- تحافظ على الطابع المهني والودود

إذا لم تعرف إجابة سؤال، قل ذلك بصراحة واقترح طرق للحصول على المساعدة."""
        
        # ذاكرة المحادثات
        self.conversation_memory = {}
        
    def chat(self, message: str, user_id: str = "default", context: List[Dict] = None) -> Dict:
        """إرسال رسالة إلى DeepSeek AI"""
        try:
            # بناء المحادثة مع السياق
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # إضافة السياق إذا كان متوفراً
            if context:
                messages.extend(context)
            
            # إضافة الرسالة الحالية
            messages.append({"role": "user", "content": message})
            
            # إعداد الطلب
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "stream": False
            }
            
            # إرسال الطلب
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            response_time = round(time.time() - start_time, 2)
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data['choices'][0]['message']['content']
                
                # حفظ في الذاكرة
                self.save_to_memory(user_id, message, ai_response)
                
                return {
                    'success': True,
                    'response': ai_response,
                    'response_time': response_time,
                    'tokens_used': data.get('usage', {}).get('total_tokens', 0),
                    'model': self.model
                }
            else:
                error_msg = f"خطأ من DeepSeek API: {response.status_code}"
                if response.text:
                    try:
                        error_data = response.json()
                        error_msg = error_data.get('error', {}).get('message', error_msg)
                    except:
                        pass
                
                return {
                    'success': False,
                    'error': error_msg,
                    'fallback_response': self.get_fallback_response(message)
                }
                
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'انتهت مهلة الاتصال مع DeepSeek',
                'fallback_response': self.get_fallback_response(message)
            }
        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'error': 'لا يمكن الاتصال بخدمة DeepSeek',
                'fallback_response': self.get_fallback_response(message)
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'خطأ غير متوقع: {str(e)}',
                'fallback_response': self.get_fallback_response(message)
            }
    
    def get_conversation_context(self, user_id: str, limit: int = 5) -> List[Dict]:
        """الحصول على سياق المحادثة من قاعدة البيانات"""
        try:
            # فحص وجود قاعدة البيانات
            from pathlib import Path
            if not Path('chatbot_data.db').exists():
                return []

            conn = sqlite3.connect('chatbot_data.db')
            cursor = conn.cursor()

            # فحص وجود الجدول
            cursor.execute('''
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='conversations'
            ''')
            if not cursor.fetchone():
                conn.close()
                return []

            cursor.execute('''
                SELECT user_message, bot_response
                FROM conversations
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (user_id, limit))

            rows = cursor.fetchall()
            conn.close()

            # تحويل إلى تنسيق المحادثة (الأحدث أولاً، لذا نعكس)
            context = []
            for row in reversed(rows):
                if row[0] and row[1]:  # التأكد من وجود البيانات
                    context.append({"role": "user", "content": row[0]})
                    context.append({"role": "assistant", "content": row[1]})

            return context

        except Exception as e:
            print(f"خطأ في الحصول على السياق: {e}")
            return []
    
    def save_to_memory(self, user_id: str, user_message: str, ai_response: str):
        """حفظ المحادثة في الذاكرة المؤقتة"""
        if user_id not in self.conversation_memory:
            self.conversation_memory[user_id] = []
        
        self.conversation_memory[user_id].append({
            'user': user_message,
            'assistant': ai_response,
            'timestamp': datetime.now().isoformat()
        })
        
        # الاحتفاظ بآخر 10 رسائل فقط
        if len(self.conversation_memory[user_id]) > 10:
            self.conversation_memory[user_id] = self.conversation_memory[user_id][-10:]
    
    def get_fallback_response(self, message: str) -> str:
        """ردود احتياطية عند فشل DeepSeek"""
        message_lower = message.lower()
        
        fallback_responses = {
            'greeting': [
                'مرحباً بك! 👋 أعتذر، خدمة الذكاء الاصطناعي غير متاحة حالياً، لكنني هنا لمساعدتك.',
                'أهلاً وسهلاً! 🌟 نواجه مشكلة تقنية مؤقتة، لكن يمكنني مساعدتك بالطرق التقليدية.'
            ],
            'help': [
                'يمكنني مساعدتك في:\n• الأسئلة العامة\n• معلومات الخدمات\n• التوجيه للقسم المناسب\n\nما الذي تحتاج مساعدة فيه؟',
                'أنا هنا لمساعدتك! اسألني عن خدماتنا أو أي استفسار لديك.'
            ],
            'thanks': [
                'العفو! 😊 سعيد لمساعدتك رغم المشكلة التقنية المؤقتة.',
                'لا شكر على واجب! أتمنى أن تتحسن الخدمة قريباً.'
            ],
            'default': [
                f'شكراً لرسالتك: "{message}". نواجه مشكلة تقنية مؤقتة مع خدمة الذكاء الاصطناعي. فريق الدعم سيتواصل معك قريباً.',
                'أعتذر، خدمة الذكاء الاصطناعي غير متاحة حالياً. يمكنك المحاولة لاحقاً أو التواصل مع فريق الدعم مباشرة.'
            ]
        }
        
        # تحديد نوع الرسالة
        if any(word in message_lower for word in ['مرحبا', 'السلام', 'أهلا', 'hello', 'hi']):
            responses = fallback_responses['greeting']
        elif any(word in message_lower for word in ['مساعدة', 'help', 'دعم']):
            responses = fallback_responses['help']
        elif any(word in message_lower for word in ['شكرا', 'شكراً', 'thanks']):
            responses = fallback_responses['thanks']
        else:
            responses = fallback_responses['default']
        
        # اختيار رد عشوائي
        import random
        return random.choice(responses)
    
    def test_connection(self) -> Dict:
        """اختبار الاتصال مع DeepSeek API"""
        try:
            test_result = self.chat("مرحبا، هذا اختبار للاتصال", "test_user")
            
            if test_result['success']:
                return {
                    'status': 'connected',
                    'message': 'الاتصال مع DeepSeek AI يعمل بنجاح',
                    'response_time': test_result['response_time'],
                    'model': self.model
                }
            else:
                return {
                    'status': 'error',
                    'message': f"فشل الاتصال: {test_result['error']}",
                    'fallback_available': True
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'خطأ في اختبار الاتصال: {str(e)}',
                'fallback_available': True
            }
    
    def get_usage_stats(self) -> Dict:
        """إحصائيات الاستخدام"""
        try:
            conn = sqlite3.connect('chatbot_data.db')
            cursor = conn.cursor()
            
            # إحصائيات اليوم
            cursor.execute('''
                SELECT COUNT(*), AVG(response_time)
                FROM conversations 
                WHERE date(timestamp) = date('now')
                AND bot_response NOT LIKE '%خدمة الذكاء الاصطناعي غير متاحة%'
            ''')
            
            today_stats = cursor.fetchone()
            ai_requests_today = today_stats[0] or 0
            avg_response_time = round(today_stats[1] or 0, 2)
            
            # إحصائيات الأسبوع
            cursor.execute('''
                SELECT COUNT(*)
                FROM conversations 
                WHERE date(timestamp) >= date('now', '-7 days')
                AND bot_response NOT LIKE '%خدمة الذكاء الاصطناعي غير متاحة%'
            ''')
            
            ai_requests_week = cursor.fetchone()[0] or 0
            
            conn.close()
            
            return {
                'ai_requests_today': ai_requests_today,
                'ai_requests_week': ai_requests_week,
                'avg_response_time': avg_response_time,
                'model': self.model,
                'api_status': 'active'
            }
            
        except Exception as e:
            return {
                'error': f'خطأ في الحصول على الإحصائيات: {str(e)}',
                'ai_requests_today': 0,
                'ai_requests_week': 0,
                'avg_response_time': 0,
                'model': self.model,
                'api_status': 'unknown'
            }

# إنشاء مثيل عام (يستخدم الإعدادات من .env)
try:
    deepseek_ai = DeepSeekAI()
    logger.info("تم تهيئة DeepSeek AI بنجاح")
except Exception as e:
    logger.error(f"فشل في تهيئة DeepSeek AI: {e}")
    # إنشاء مثيل وهمي للاختبار
    class DummyDeepSeekAI:
        def chat(self, *args, **kwargs):
            return {'success': False, 'error': 'DeepSeek AI غير متاح', 'fallback_response': 'عذراً، الخدمة غير متاحة حالياً'}
        def test_connection(self):
            return {'status': 'error', 'message': 'مفتاح API غير صحيح'}
        def get_usage_stats(self):
            return {'error': 'DeepSeek AI غير متاح'}

    deepseek_ai = DummyDeepSeekAI()

if __name__ == "__main__":
    # اختبار النظام
    print("🤖 اختبار DeepSeek AI...")
    
    # اختبار الاتصال
    connection_test = deepseek_ai.test_connection()
    print(f"حالة الاتصال: {connection_test}")
    
    # اختبار محادثة
    if connection_test['status'] == 'connected':
        print("\n💬 اختبار المحادثة:")
        
        test_messages = [
            "مرحبا، كيف حالك؟",
            "ما هي خدماتكم؟",
            "شكراً لك"
        ]
        
        for msg in test_messages:
            print(f"\nالمستخدم: {msg}")
            result = deepseek_ai.chat(msg, "test_user")
            
            if result['success']:
                print(f"DeepSeek: {result['response']}")
                print(f"وقت الاستجابة: {result['response_time']}s")
            else:
                print(f"خطأ: {result['error']}")
                print(f"رد احتياطي: {result['fallback_response']}")
    
    # عرض الإحصائيات
    stats = deepseek_ai.get_usage_stats()
    print(f"\n📊 الإحصائيات: {stats}")
    
    print("\n✅ انتهى الاختبار")
