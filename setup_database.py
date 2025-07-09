#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت تهيئة قاعدة البيانات
ينشئ قاعدة البيانات مع بيانات تجريبية واقعية
"""

import sqlite3
from datetime import datetime, timedelta
import random

def create_database():
    """إنشاء قاعدة البيانات والجداول"""
    """إنشاء قاعدة البيانات والجداول"""
    print("🗄️  إنشاء قاعدة البيانات...")
    
    conn = sqlite3.connect('chatbot_data.db')
    cursor = conn.cursor()
    
    # جدول المحادثات
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            session_id TEXT NOT NULL,
            user_message TEXT NOT NULL,
            bot_response TEXT NOT NULL,
            channel TEXT DEFAULT 'website',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            response_time REAL DEFAULT 1.0,
            satisfaction INTEGER DEFAULT NULL
        )
    ''')
    
    # جدول المستخدمين
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            email TEXT,
            phone TEXT,
            channel TEXT,
            first_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
            total_messages INTEGER DEFAULT 0,
            avg_satisfaction REAL DEFAULT NULL
        )
    ''')
    
    # جدول الإحصائيات اليومية
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_stats (
            date DATE PRIMARY KEY,
            total_conversations INTEGER DEFAULT 0,
            unique_users INTEGER DEFAULT 0,
            avg_response_time REAL DEFAULT 0,
            satisfaction_rate REAL DEFAULT 0,
            channel_website INTEGER DEFAULT 0,
            channel_whatsapp INTEGER DEFAULT 0,
            channel_telegram INTEGER DEFAULT 0,
            channel_messenger INTEGER DEFAULT 0,
            channel_instagram INTEGER DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ تم إنشاء قاعدة البيانات والجداول")

def add_sample_data():
    """إضافة بيانات تجريبية واقعية"""
    print("📊 إضافة بيانات تجريبية...")
    
    conn = sqlite3.connect('chatbot_data.db')
    cursor = conn.cursor()
    
    # فحص إذا كانت هناك بيانات موجودة
    cursor.execute("SELECT COUNT(*) FROM conversations")
    if cursor.fetchone()[0] > 0:
        print("⚠️  البيانات موجودة مسبقاً، تخطي إضافة البيانات التجريبية")
        conn.close()
        return
    
    # بيانات مستخدمين تجريبية
    sample_users = [
        ('user_001', 'أحمد', 'محمد', 'ahmed@example.com', '+966501234567', 'website'),
        ('user_002', 'فاطمة', 'علي', 'fatima@example.com', '+966507654321', 'whatsapp'),
        ('user_003', 'محمد', 'سالم', 'mohammed@example.com', '+966509876543', 'telegram'),
        ('user_004', 'نورا', 'أحمد', 'nora@example.com', '+966502468135', 'messenger'),
        ('user_005', 'خالد', 'عبدالله', 'khalid@example.com', '+966508642097', 'instagram'),
        ('user_006', 'سارة', 'حسن', 'sara@example.com', '+966503691472', 'website'),
        ('user_007', 'عمر', 'يوسف', 'omar@example.com', '+966504826159', 'whatsapp'),
        ('user_008', 'ليلى', 'إبراهيم', 'layla@example.com', '+966505937284', 'telegram'),
    ]
    
    for user in sample_users:
        cursor.execute('''
            INSERT OR IGNORE INTO users 
            (user_id, first_name, last_name, email, phone, channel, total_messages, avg_satisfaction)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (*user, random.randint(5, 25), round(random.uniform(3.5, 5.0), 1)))
    
    # رسائل تجريبية متنوعة
    sample_messages = [
        # رسائل ترحيب
        ('مرحبا', 'مرحباً بك! 👋 أنا المساعد الذكي. كيف يمكنني مساعدتك اليوم؟'),
        ('السلام عليكم', 'وعليكم السلام ورحمة الله وبركاته! أهلاً وسهلاً بك 🌟'),
        ('أهلا', 'أهلاً وسهلاً! سعيد بلقائك. ما الذي يمكنني مساعدتك فيه؟'),
        
        # استفسارات عن المنتجات
        ('أريد معلومات عن المنتج', 'بالطبع! يمكنني تقديم معلومات مفصلة عن منتجاتنا. ما المنتج الذي تهتم به؟'),
        ('ما هي الأسعار؟', 'أسعارنا تنافسية ومناسبة للجميع. يمكنك مراجعة قائمة الأسعار على موقعنا أو سأرسل لك التفاصيل.'),
        ('هل يوجد خصومات؟', 'نعم! لدينا عروض وخصومات مستمرة. حالياً خصم 20% على جميع المنتجات للعملاء الجدد! 🎉'),
        
        # استفسارات عن الخدمات
        ('كيف يمكنني الطلب؟', 'يمكنك الطلب بسهولة من خلال موقعنا أو تطبيق الجوال. هل تحتاج مساعدة في التنقل؟'),
        ('ما هي أوقات العمل؟', 'نعمل من الأحد إلى الخميس من 9 صباحاً حتى 6 مساءً، والجمعة من 2 ظهراً حتى 6 مساءً.'),
        ('هل يوجد توصيل مجاني؟', 'نعم! نوفر توصيل مجاني للطلبات أكثر من 200 ريال داخل المدينة. 🚚'),
        
        # خدمة العملاء
        ('أريد إرجاع منتج', 'يمكنك إرجاع المنتج خلال 14 يوم من تاريخ الشراء. هل تحتاج تفاصيل أكثر عن سياسة الإرجاع؟'),
        ('لدي شكوى', 'أعتذر عن أي إزعاج. يرجى توضيح المشكلة وسأقوم بتوجيهك للقسم المختص فوراً.'),
        ('أريد التحدث مع مندوب', 'بالطبع! سأقوم بتحويلك لأحد مندوبي خدمة العملاء. يرجى الانتظار قليلاً...'),
        
        # استفسارات عامة
        ('ما الوقت الآن؟', f'الوقت الحالي هو: {datetime.now().strftime("%H:%M:%S")} ⏰'),
        ('شكرا لك', 'العفو! سعيد لمساعدتك 😊 هل تحتاج لأي شيء آخر؟'),
        ('وداعا', 'وداعاً! كان من دواعي سروري مساعدتك. نتطلع لخدمتك مرة أخرى! 👋'),
    ]
    
    # إضافة محادثات موزعة على الأيام والساعات
    channels = ['website', 'whatsapp', 'telegram', 'messenger', 'instagram']
    
    # إضافة محادثات لآخر 7 أيام
    for day_offset in range(7):
        date = datetime.now() - timedelta(days=day_offset)
        
        # عدد المحادثات يقل في الأيام الأقدم
        conversations_count = random.randint(15, 30) if day_offset < 2 else random.randint(5, 15)
        
        for i in range(conversations_count):
            # اختيار رسالة عشوائية
            user_msg, bot_msg = random.choice(sample_messages)
            
            # اختيار مستخدم وقناة عشوائية
            user_id = random.choice([u[0] for u in sample_users])
            channel = random.choice(channels)
            
            # وقت عشوائي في اليوم (ساعات العمل أكثر)
            if 9 <= date.hour <= 18:
                hour = random.randint(9, 18)
            else:
                hour = random.randint(0, 23)
            
            minute = random.randint(0, 59)
            timestamp = date.replace(hour=hour, minute=minute, second=random.randint(0, 59))
            
            # وقت استجابة واقعي
            response_time = round(random.uniform(0.5, 3.0), 1)
            
            # تقييم عشوائي (أغلبه إيجابي)
            satisfaction = random.choices([3, 4, 5, None], weights=[10, 30, 50, 10])[0]
            
            cursor.execute('''
                INSERT INTO conversations 
                (user_id, session_id, user_message, bot_response, channel, timestamp, response_time, satisfaction)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, 
                f"sess_{user_id}_{i}", 
                user_msg, 
                bot_msg, 
                channel, 
                timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                response_time,
                satisfaction
            ))
    
    # تحديث إحصائيات المستخدمين
    for user in sample_users:
        user_id = user[0]
        cursor.execute('''
            UPDATE users SET 
                total_messages = (SELECT COUNT(*) FROM conversations WHERE user_id = ?),
                last_seen = (SELECT MAX(timestamp) FROM conversations WHERE user_id = ?),
                avg_satisfaction = (SELECT AVG(satisfaction) FROM conversations WHERE user_id = ? AND satisfaction IS NOT NULL)
            WHERE user_id = ?
        ''', (user_id, user_id, user_id, user_id))
    
    conn.commit()
    conn.close()
    print("✅ تم إضافة البيانات التجريبية")

def create_auth_database():
    """إنشاء قاعدة بيانات المصادقة"""
    print("🔐 إنشاء قاعدة بيانات المصادقة...")
    
    conn = sqlite3.connect('auth.db')
    cursor = conn.cursor()
    
    # جدول المستخدمين
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            role TEXT DEFAULT 'user',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_login DATETIME,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    # جدول الجلسات
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            user_id INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            expires_at DATETIME,
            ip_address TEXT,
            user_agent TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # جدول الصلاحيات
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            resource TEXT NOT NULL,
            action TEXT NOT NULL,
            allowed BOOLEAN DEFAULT 1
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ تم إنشاء قاعدة بيانات المصادقة")

def show_database_info():
    """عرض معلومات قاعدة البيانات"""
    print("\n📊 معلومات قاعدة البيانات:")
    
    try:
        conn = sqlite3.connect('chatbot_data.db')
        cursor = conn.cursor()
        
        # عدد المحادثات
        cursor.execute("SELECT COUNT(*) FROM conversations")
        conversations_count = cursor.fetchone()[0]
        
        # عدد المستخدمين
        cursor.execute("SELECT COUNT(*) FROM users")
        users_count = cursor.fetchone()[0]
        
        # آخر محادثة
        cursor.execute("SELECT MAX(timestamp) FROM conversations")
        last_conversation = cursor.fetchone()[0]
        
        # توزيع القنوات
        cursor.execute("SELECT channel, COUNT(*) FROM conversations GROUP BY channel")
        channels_stats = cursor.fetchall()
        
        print(f"  📝 إجمالي المحادثات: {conversations_count}")
        print(f"  👥 إجمالي المستخدمين: {users_count}")
        print(f"  🕐 آخر محادثة: {last_conversation}")
        print(f"  📺 توزيع القنوات:")
        for channel, count in channels_stats:
            print(f"    - {channel}: {count} محادثة")
        
        conn.close()
        
    except Exception as e:
        print(f"  ❌ خطأ في قراءة قاعدة البيانات: {e}")

def main():
    """الدالة الرئيسية"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                🗄️  تهيئة قاعدة البيانات                     ║
║                                                              ║
║              إنشاء قواعد البيانات مع بيانات تجريبية          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    try:
        # إنشاء قاعدة البيانات الرئيسية
        create_database()
        
        # إضافة البيانات التجريبية
        add_sample_data()
        
        # إنشاء قاعدة بيانات المصادقة
        create_auth_database()
        
        # عرض معلومات قاعدة البيانات
        show_database_info()
        
        print(f"""
{'='*60}
🎉 تم تهيئة قاعدة البيانات بنجاح!

📁 الملفات المنشأة:
  🗄️  chatbot_data.db - قاعدة البيانات الرئيسية
  🔐 auth.db - قاعدة بيانات المصادقة

🚀 الخطوات التالية:
  1. شغّل الباك-إند: python backend_server.py
  2. شغّل الفرونت-إند: python simple_server.py --port 8000
  3. افتح لوحة التحكم: http://localhost:8000/dashboard/

🔐 بيانات الدخول:
  اسم المستخدم: admin
  كلمة المرور: admin123

✅ النظام جاهز للاستخدام!
{'='*60}
        """)
        
    except Exception as e:
        print(f"❌ خطأ في تهيئة قاعدة البيانات: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
