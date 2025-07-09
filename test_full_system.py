#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار شامل للنظام الكامل
فحص جميع المكونات والـ APIs
"""

import requests
import json
import time
import sys
from datetime import datetime

class SystemTester:
    """فئة اختبار النظام"""
    
    def __init__(self):
        self.backend_url = "http://localhost:8001"
        self.frontend_url = "http://localhost:8000"
        self.ai_agent_url = "http://localhost:5000"
        self.results = {
            'passed': 0,
            'failed': 0,
            'warnings': 0,
            'tests': []
        }
    
    def print_header(self):
        """طباعة رأس الاختبار"""
        print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                🧪 اختبار النظام الشامل                      ║
║                                                              ║
║              فحص جميع المكونات والـ APIs                     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

🔍 بدء الاختبار الشامل...
        """)
    
    def test_backend_health(self):
        """اختبار صحة الباك-إند"""
        print("🗄️  اختبار الباك-إند...")
        
        try:
            response = requests.get(f"{self.backend_url}/api/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'healthy':
                    self.log_test("Backend Health", True, "الباك-إند يعمل بشكل صحيح")
                    return True
                else:
                    self.log_test("Backend Health", False, f"حالة غير صحيحة: {data}")
                    return False
            else:
                self.log_test("Backend Health", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Backend Health", False, f"خطأ في الاتصال: {e}")
            return False
    
    def test_backend_stats(self):
        """اختبار API الإحصائيات"""
        print("📊 اختبار API الإحصائيات...")
        
        try:
            response = requests.get(f"{self.backend_url}/api/stats", timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                # فحص البيانات المطلوبة
                required_fields = [
                    'total_conversations', 'active_users', 'response_time',
                    'satisfaction_rate', 'channels', 'hourly_stats', 'recent_chats'
                ]
                
                missing_fields = []
                for field in required_fields:
                    if field not in data:
                        missing_fields.append(field)
                
                if not missing_fields:
                    self.log_test("Backend Stats API", True, f"جميع البيانات متوفرة: {len(data)} حقل")
                    
                    # اختبار جودة البيانات
                    if data['total_conversations'] > 0:
                        self.log_test("Stats Data Quality", True, f"المحادثات: {data['total_conversations']}")
                    else:
                        self.log_test("Stats Data Quality", False, "لا توجد محادثات")
                    
                    return True
                else:
                    self.log_test("Backend Stats API", False, f"حقول مفقودة: {missing_fields}")
                    return False
            else:
                self.log_test("Backend Stats API", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Backend Stats API", False, f"خطأ: {e}")
            return False
    
    def test_backend_chat(self):
        """اختبار API الشات"""
        print("💬 اختبار API الشات...")
        
        test_message = {
            "message": "اختبار النظام",
            "user_id": "test_user_" + str(int(time.time())),
            "session_id": "test_session_" + str(int(time.time()))
        }
        
        try:
            response = requests.post(
                f"{self.backend_url}/api/chat",
                json=test_message,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('response'):
                    self.log_test("Backend Chat API", True, f"رد: {data['response'][:50]}...")
                    return True
                else:
                    self.log_test("Backend Chat API", False, f"استجابة غير صحيحة: {data}")
                    return False
            else:
                self.log_test("Backend Chat API", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Backend Chat API", False, f"خطأ: {e}")
            return False
    
    def test_frontend_access(self):
        """اختبار الوصول للفرونت-إند"""
        print("🌐 اختبار الفرونت-إند...")
        
        pages = [
            ("الصفحة الرئيسية", "/"),
            ("الشات بوت", "/web-integration/chatbot-widget.html"),
            ("لوحة التحكم", "/dashboard/index.html")
        ]
        
        all_passed = True
        for name, path in pages:
            try:
                response = requests.get(f"{self.frontend_url}{path}", timeout=5)
                if response.status_code == 200:
                    self.log_test(f"Frontend - {name}", True, "متاح")
                else:
                    self.log_test(f"Frontend - {name}", False, f"HTTP {response.status_code}")
                    all_passed = False
            except Exception as e:
                self.log_test(f"Frontend - {name}", False, f"خطأ: {e}")
                all_passed = False
        
        return all_passed
    
    def test_ai_agent(self):
        """اختبار AI Agent"""
        print("🤖 اختبار AI Agent...")
        
        try:
            response = requests.get(f"{self.ai_agent_url}/api/health", timeout=5)
            if response.status_code == 200:
                self.log_test("AI Agent Health", True, "متاح")
                
                # اختبار تنفيذ أمر
                try:
                    command_response = requests.post(
                        f"{self.ai_agent_url}/api/execute",
                        json={"command": "مرحبا"},
                        timeout=10
                    )
                    if command_response.status_code == 200:
                        self.log_test("AI Agent Execute", True, "يستجيب للأوامر")
                    else:
                        self.log_test("AI Agent Execute", False, f"HTTP {command_response.status_code}")
                except Exception as e:
                    self.log_test("AI Agent Execute", False, f"خطأ: {e}")
                
                return True
            else:
                self.log_test("AI Agent Health", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("AI Agent Health", False, f"غير متاح: {e}")
            return False
    
    def test_integration(self):
        """اختبار التكامل بين المكونات"""
        print("🔄 اختبار التكامل...")
        
        # اختبار تدفق كامل: رسالة → باك-إند → حفظ → إحصائيات
        try:
            # 1. الحصول على الإحصائيات قبل الرسالة
            stats_before = requests.get(f"{self.backend_url}/api/stats", timeout=5).json()
            conversations_before = stats_before.get('total_conversations', 0)
            
            # 2. إرسال رسالة جديدة
            test_message = {
                "message": f"اختبار التكامل {int(time.time())}",
                "user_id": f"integration_test_{int(time.time())}",
                "session_id": f"integration_session_{int(time.time())}"
            }
            
            chat_response = requests.post(
                f"{self.backend_url}/api/chat",
                json=test_message,
                timeout=10
            )
            
            if chat_response.status_code == 200:
                # 3. انتظار قصير ثم فحص الإحصائيات
                time.sleep(1)
                stats_after = requests.get(f"{self.backend_url}/api/stats", timeout=5).json()
                conversations_after = stats_after.get('total_conversations', 0)
                
                if conversations_after > conversations_before:
                    self.log_test("Integration Test", True, f"المحادثات: {conversations_before} → {conversations_after}")
                    return True
                else:
                    self.log_test("Integration Test", False, "الإحصائيات لم تتحدث")
                    return False
            else:
                self.log_test("Integration Test", False, "فشل في إرسال الرسالة")
                return False
                
        except Exception as e:
            self.log_test("Integration Test", False, f"خطأ: {e}")
            return False
    
    def test_database_persistence(self):
        """اختبار استمرارية قاعدة البيانات"""
        print("💾 اختبار قاعدة البيانات...")
        
        try:
            import sqlite3
            from pathlib import Path
            
            db_path = Path("chatbot_data.db")
            if db_path.exists():
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                
                # فحص الجداول
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                expected_tables = ['conversations', 'users', 'daily_stats']
                missing_tables = [t for t in expected_tables if t not in tables]
                
                if not missing_tables:
                    # فحص البيانات
                    cursor.execute("SELECT COUNT(*) FROM conversations")
                    conv_count = cursor.fetchone()[0]
                    
                    cursor.execute("SELECT COUNT(*) FROM users")
                    user_count = cursor.fetchone()[0]
                    
                    self.log_test("Database Structure", True, f"الجداول: {len(tables)}")
                    self.log_test("Database Data", True, f"المحادثات: {conv_count}, المستخدمين: {user_count}")
                    
                    conn.close()
                    return True
                else:
                    self.log_test("Database Structure", False, f"جداول مفقودة: {missing_tables}")
                    conn.close()
                    return False
            else:
                self.log_test("Database File", False, "ملف قاعدة البيانات غير موجود")
                return False
                
        except Exception as e:
            self.log_test("Database Test", False, f"خطأ: {e}")
            return False
    
    def log_test(self, test_name, passed, details):
        """تسجيل نتيجة الاختبار"""
        status = "✅" if passed else "❌"
        print(f"  {status} {test_name}: {details}")
        
        self.results['tests'].append({
            'name': test_name,
            'passed': passed,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        
        if passed:
            self.results['passed'] += 1
        else:
            self.results['failed'] += 1
    
    def run_all_tests(self):
        """تشغيل جميع الاختبارات"""
        self.print_header()
        
        tests = [
            ("فحص الباك-إند", self.test_backend_health),
            ("API الإحصائيات", self.test_backend_stats),
            ("API الشات", self.test_backend_chat),
            ("الفرونت-إند", self.test_frontend_access),
            ("AI Agent", self.test_ai_agent),
            ("التكامل", self.test_integration),
            ("قاعدة البيانات", self.test_database_persistence)
        ]
        
        for test_name, test_func in tests:
            print(f"\n{'='*60}")
            print(f"🧪 {test_name}")
            print('='*60)
            
            try:
                test_func()
            except Exception as e:
                self.log_test(test_name, False, f"خطأ غير متوقع: {e}")
        
        self.print_summary()
    
    def print_summary(self):
        """طباعة ملخص النتائج"""
        total_tests = self.results['passed'] + self.results['failed']
        success_rate = (self.results['passed'] / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n{'='*60}")
        print("📊 ملخص نتائج الاختبار")
        print('='*60)
        print(f"📝 إجمالي الاختبارات: {total_tests}")
        print(f"✅ نجح: {self.results['passed']}")
        print(f"❌ فشل: {self.results['failed']}")
        print(f"📈 معدل النجاح: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("\n🎉 ممتاز! النظام يعمل بشكل مثالي")
        elif success_rate >= 70:
            print("\n👍 جيد! النظام يعمل مع بعض التحسينات المطلوبة")
        elif success_rate >= 50:
            print("\n⚠️  متوسط! النظام يحتاج لإصلاحات")
        else:
            print("\n🚨 ضعيف! النظام يحتاج لإصلاحات جوهرية")
        
        # حفظ النتائج
        try:
            with open('test_results.json', 'w', encoding='utf-8') as f:
                json.dump(self.results, f, ensure_ascii=False, indent=2)
            print(f"\n💾 تم حفظ النتائج في: test_results.json")
        except Exception as e:
            print(f"\n⚠️  لم يتم حفظ النتائج: {e}")
        
        print(f"\n{'='*60}")

if __name__ == "__main__":
    tester = SystemTester()
    tester.run_all_tests()
