from flask import Flask, jsonify, request, send_from_directory # تمت إضافة send_from_directory
from flask_cors import CORS
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from deepseek_ai import deepseek_ai
from secure_config import config
from secure_auth import secure_auth, require_auth, require_role # تأكد من صحة هذا الاستيراد
from rate_limiter import rate_limiter, rate_limit # تأكد من صحة هذا الاستيراد
import logging
import os # تمت إضافة os

logger = logging.getLogger(__name__)

app = Flask(__name__)

# إعداد CORS الآمن
CORS(app, origins=config.allowed_origins, supports_credentials=True)

# إعداد المفتاح السري
app.secret_key = config.secret_key

DB_PATH = config.get_database_path()

# فحص قاعدة البيانات عند البدء
if not Path(DB_PATH).exists():
    print("⚠️  قاعدة البيانات غير موجودة!")
    print("   شغّل: python setup_database.py")
    print("   أو ستُنشأ تلقائياً عند أول استخدام")

# اختبار DeepSeek AI عند البدء
print("🤖 اختبار اتصال DeepSeek AI...")
ai_test = deepseek_ai.test_connection()
if ai_test['status'] == 'connected':
    print("✅ DeepSeek AI متصل ويعمل بنجاح")
else:
    print(f"⚠️  DeepSeek AI: {ai_test['message']}")
    print("   سيتم استخدام الردود الاحتياطية")

# --- بداية تعديلات خدمة الملفات الثابتة ---
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

@app.route('/')
def serve_index():
    return send_from_directory(PROJECT_ROOT, 'index.html')

@app.route('/<path:filename>')
def serve_root_static_files(filename):
    allowed_root_files = ['favicon.ico', 'manifest.json', 'robots.txt', 'README.md', 'README_QUICK.md', 'PROJECT_SUMMARY.md', 'COMPLETE_SYSTEM_GUIDE.md', 'DEEPSEEK_AI_GUIDE.md', 'QUICK_START_GUIDE.md', 'REAL_BACKEND_GUIDE.md', 'REAL_SYSTEM_GUIDE.md', 'SECURE_SYSTEM_GUIDE.md']
    allowed_extensions = ['.png', '.jpg', '.jpeg', '.css', '.js', '.ico', '.txt', '.md'] # السماح بـ .md
    file_ext = os.path.splitext(filename)[1].lower()

    if filename in allowed_root_files or file_ext in allowed_extensions:
        # تحقق إضافي لمنع خدمة ملفات .py أو .env من الجذر
        if filename.endswith(('.py', '.env', '.bat', '.sh')) or '.git' in filename:
             return "Access denied", 403
        return send_from_directory(PROJECT_ROOT, filename)
    return "File not found or not permitted", 404


@app.route('/web-integration/<path:filename>')
def serve_web_integration_files(filename):
    web_integration_dir = os.path.join(PROJECT_ROOT, 'web-integration')
    return send_from_directory(web_integration_dir, filename)

@app.route('/dashboard/<path:filename>')
def serve_dashboard_files(filename):
    dashboard_dir = os.path.join(PROJECT_ROOT, 'dashboard')
    return send_from_directory(dashboard_dir, filename)

# --- نهاية تعديلات خدمة الملفات الثابتة ---

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/stats')
def stats():
    conn = get_db_connection()
    cur = conn.cursor()

    # إجمالي المحادثات
    cur.execute('SELECT COUNT(*) FROM conversations')
    total_conversations = cur.fetchone()[0]

    # المستخدمون النشطون اليوم
    cur.execute("SELECT COUNT(DISTINCT user_id) FROM conversations WHERE date(timestamp) = date('now')")
    active_users_today = cur.fetchone()[0]

    # إجمالي المستخدمين المميزين (من جدول users إذا كان يُملأ بشكل جيد، أو conversations كبديل)
    # سنستخدم conversations كبديل لضمان وجود بيانات
    cur.execute('SELECT COUNT(DISTINCT user_id) FROM conversations')
    total_distinct_users = cur.fetchone()[0]

    # متوسط وقت الاستجابة
    cur.execute('SELECT AVG(response_time) FROM conversations')
    response_time = round(cur.fetchone()[0] or 1.2, 1)

    # معدل الرضا
    cur.execute('SELECT AVG(satisfaction) FROM conversations WHERE satisfaction IS NOT NULL')
    satisfaction_rate = round((cur.fetchone()[0] or 4.5) * 20, 1) # تحويل من 5 إلى 100

    # إحصائيات القنوات لليوم الحالي
    cur.execute("SELECT channel, COUNT(*) FROM conversations WHERE date(timestamp) = date('now') GROUP BY channel")
    channels_data_today = {row[0]: row[1] for row in cur.fetchall()}

    # إحصائيات الساعات لليوم الحالي
    cur.execute("SELECT strftime('%H:00', timestamp) as hour, COUNT(*) as count FROM conversations WHERE date(timestamp) = date('now') GROUP BY hour ORDER BY hour")
    hourly_stats_today = [{'hour': row[0], 'messages': row[1]} for row in cur.fetchall()]

    # إجمالي الرسائل اليوم
    cur.execute("SELECT COUNT(*) FROM conversations WHERE date(timestamp) = date('now')")
    messages_today = cur.fetchone()[0]

    # المحادثات الحديثة
    cur.execute('SELECT user_id, user_message, channel, timestamp FROM conversations ORDER BY timestamp DESC LIMIT 10')
    recent_chats = []
    for row in cur.fetchall():
        time_diff = datetime.now() - datetime.strptime(row[3], '%Y-%m-%d %H:%M:%S')
        if time_diff.seconds < 3600:
            time_str = f"منذ {time_diff.seconds // 60} دقيقة"
        else:
            time_str = f"منذ {time_diff.seconds // 3600} ساعة"
        recent_chats.append({
            'time': time_str,
            'user': row[0],
            'channel': row[2],
            'message': row[1],
            'status': 'resolved'
        })
    conn.close()
    return jsonify({
        "total_conversations": total_conversations,
        "active_users_today": active_users_today,
        "total_distinct_users": total_distinct_users,
        "messages_today": messages_today,
        "response_time": response_time,
        "satisfaction_rate": satisfaction_rate,
        "channels_today": channels_data_today,
        "hourly_stats_today": hourly_stats_today,
        "recent_chats": recent_chats
    })

@app.route('/api/conversations')
def conversations():
    conn = get_db_connection()
    cur = conn.cursor()
    # جلب المزيد من التفاصيل وتوحيد الحقول مع ما كان في backend_server.py
    # وزيادة الحد إلى 50
    cur.execute('''
        SELECT id, user_id, session_id, user_message, bot_response, channel, timestamp, response_time, satisfaction
        FROM conversations
        ORDER BY timestamp DESC
        LIMIT 50
    ''')
    conversations_list = []
    for row in cur.fetchall():
        conversations_list.append({
            'id': row[0],
            'user_id': row[1],
            'session_id': row[2],
            'user_message': row[3],
            'bot_response': row[4],
            'channel': row[5],
            'timestamp': row[6],
            'response_time': row[7],
            'satisfaction': row[8],
            'status': 'resolved' if row[8] is not None else ('pending' if not row[4] else 'answered') # تحسين منطق الحالة
        })
    conn.close()
    return jsonify({'conversations': conversations_list})

@app.route('/api/channels')
def channels_api():
    conn = get_db_connection()
    cur = conn.cursor()
    # جلب إحصائيات أكثر تفصيلاً لكل قناة
    cur.execute('''
        SELECT
            channel,
            COUNT(*) as total_messages,
            COUNT(DISTINCT user_id) as distinct_users,
            AVG(response_time) as avg_response_time,
            SUM(CASE WHEN date(timestamp) = date('now') THEN 1 ELSE 0 END) as messages_today
        FROM conversations
        GROUP BY channel
    ''')
    channels_detailed_list = []
    for row in cur.fetchall():
        channels_detailed_list.append({
            'id': row[0].lower().replace(" ", "_"), # إنشاء id بسيط
            'name': row[0],
            'status': 'active', # افتراضيًا
            'total_messages': row[1],
            'distinct_users': row[2],
            'avg_response_time': round(row[3] or 0, 1),
            'messages_today': row[4]
        })
    conn.close()
    return jsonify({'channels': channels_detailed_list})

@app.route('/api/analytics')
def analytics():
    conn = get_db_connection()
    cur = conn.cursor()

    # Summary
    cur.execute('SELECT COUNT(*) FROM conversations')
    total_conversations = cur.fetchone()[0] if cur.fetchone() else 0
    cur.execute('SELECT COUNT(DISTINCT user_id) FROM conversations')
    total_users = cur.fetchone()[0] if cur.fetchone() else 0
    cur.execute('SELECT AVG(response_time) FROM conversations WHERE response_time IS NOT NULL')
    avg_response_time_row = cur.fetchone()
    avg_response_time = round(avg_response_time_row[0] if avg_response_time_row and avg_response_time_row[0] is not None else 1.2, 1)
    cur.execute('SELECT AVG(satisfaction) FROM conversations WHERE satisfaction IS NOT NULL')
    satisfaction_rate_row = cur.fetchone()
    satisfaction_rate = round((satisfaction_rate_row[0] if satisfaction_rate_row and satisfaction_rate_row[0] is not None else 4.5) * 20, 1)
    cur.execute('SELECT channel, COUNT(*) FROM conversations GROUP BY channel ORDER BY COUNT(*) DESC LIMIT 3')
    top_channels_query = cur.fetchall()
    top_channels = [row[0] for row in top_channels_query]

    # User Satisfaction
    user_satisfaction_distribution = {'excellent': 0, 'good': 0, 'average': 0, 'poor': 0, 'not_rated': 0}
    if total_conversations > 0:
        cur.execute('SELECT satisfaction, COUNT(*) FROM conversations GROUP BY satisfaction')
        satisfaction_counts = dict(cur.fetchall())

        # Примерное распределение на основе оценок от 1 до 5 (если satisfaction так хранится)
        # Это нужно адаптировать, если satisfaction хранится иначе
        user_satisfaction_distribution['excellent'] = satisfaction_counts.get(5, 0)
        user_satisfaction_distribution['good'] = satisfaction_counts.get(4, 0)
        user_satisfaction_distribution['average'] = satisfaction_counts.get(3, 0)
        user_satisfaction_distribution['poor'] = sum(satisfaction_counts.get(i, 0) for i in [1, 2])
        user_satisfaction_distribution['not_rated'] = total_conversations - sum(user_satisfaction_distribution.values())

    # Response Times
    cur.execute("SELECT response_time FROM conversations WHERE response_time IS NOT NULL")
    all_response_times = [row[0] for row in cur.fetchall()]
    response_times_distribution = {
        'under_1s': sum(1 for t in all_response_times if t < 1),
        '1_to_3s': sum(1 for t in all_response_times if 1 <= t <= 3),
        '3_to_5s': sum(1 for t in all_response_times if 3 < t <= 5),
        'over_5s': sum(1 for t in all_response_times if t > 5)
    }

    # Popular Topics (mocked for now)
    popular_topics_mock = [
        {'topic': 'استفسارات عامة', 'count': int(total_conversations * 0.4) if total_conversations else 0, 'percentage': 40.0},
        {'topic': 'مشاكل تقنية', 'count': int(total_conversations * 0.25) if total_conversations else 0, 'percentage': 25.0},
        {'topic': 'طلبات المنتج', 'count': int(total_conversations * 0.20) if total_conversations else 0, 'percentage': 20.0},
        {'topic': 'اقتراحات', 'count': int(total_conversations * 0.15) if total_conversations else 0, 'percentage': 15.0}
    ]

    conn.close()
    return jsonify({
        'summary': {
            'total_conversations': total_conversations,
            'total_users': total_users,
            'avg_response_time': avg_response_time,
            'satisfaction_rate': satisfaction_rate,
            'top_channels': top_channels
        },
        'user_satisfaction': user_satisfaction_distribution,
        'response_times': response_times_distribution,
        'popular_topics': popular_topics_mock
    })

@app.route('/api/flows')
@require_auth # افترض أن require_auth تم استيراده ويعمل بشكل صحيح
def flows_api():
    mock_flows = [
        {
            'id': 'welcome_flow',
            'name': 'سيناريو الترحيب',
            'status': 'active',
            'triggers': 150,
            'success_rate': 92.5,
            'last_updated': '2024-02-10T10:00:00Z'
        },
        {
            'id': 'support_flow',
            'name': 'سيناريو الدعم الفني',
            'status': 'active',
            'triggers': 85,
            'success_rate': 88.0,
            'last_updated': '2024-02-09T15:30:00Z'
        }
    ]
    return jsonify({'flows': mock_flows})

@app.route('/api/integrations')
@require_auth # افترض أن require_auth تم استيراده ويعمل بشكل صحيح
def integrations_api():
    ai_connection_status = deepseek_ai.test_connection()
    integrations_data = {
        'integrations': [
            {
                'id': 'deepseek',
                'name': 'DeepSeek AI',
                'type': 'ai_provider',
                'status': ai_connection_status.get('status', 'unknown'),
                'last_sync': datetime.now().isoformat(),
                'details': ai_connection_status.get('message', '')
            },
            {
                'id': 'google_sheets',
                'name': 'Google Sheets',
                'type': 'data_storage',
                'status': 'disconnected',
                'last_sync': None,
                'details': 'Not configured'
            }
        ]
    }
    return jsonify(integrations_data)

@app.route('/api/settings')
@require_auth # افترض أن require_auth تم استيراده ويعمل بشكل صحيح
def settings_api():
    settings_data = {
        'general': {
            'bot_name': config.get('BOT_NAME', 'المساعد الذكي'),
            'default_language': config.get('DEFAULT_LANGUAGE', 'ar'),
            'timezone': config.get('TIMEZONE', 'Asia/Riyadh'),
        },
        'ai_settings': {
            'provider': 'deepseek',
            'model': config.get('DEEPSEEK_MODEL', 'deepseek-chat'),
            'temperature': config.get('DEEPSEEK_TEMPERATURE', 0.7), # يجب أن يكون float
            'max_tokens': config.get_int('DEEPSEEK_MAX_TOKENS', 1000),
        },
        'rate_limiting': { # مثال لإعدادات الحد من الطلبات
            'chat_api_limit_requests': config.get_int('RATE_LIMIT_CHAT_API_REQUESTS', 100),
            'chat_api_limit_period_seconds': config.get_int('RATE_LIMIT_CHAT_API_PERIOD_SECONDS', 60)
        }
    }
    return jsonify(settings_data)

@app.route('/api/chat', methods=['POST'])
@rate_limit('chat_api')
def chat():
    """معالجة رسائل الشات"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        user_id = data.get('user_id', 'anonymous')
        session_id = data.get('session_id', 'default')

        # معالجة الرسالة باستخدام DeepSeek AI
        response = process_message(message, user_id)

        # حفظ في قاعدة البيانات
        save_conversation(user_id, session_id, message, response)

        return jsonify({
            'success': True,
            'response': response,
            'timestamp': time.time(),
            'user_id': user_id,
            'session_id': session_id
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/health')
def health():
    """فحص صحة النظام"""
    db_status = 'connected' if Path(DB_PATH).exists() else 'disconnected'

    # فحص DeepSeek AI
    ai_test_result = deepseek_ai.test_connection() # تم تغيير اسم المتغير
    ai_status = ai_test_result['status'] # تم استخدام الاسم الجديد

    return jsonify({
        'status': 'healthy',
        'database': db_status,
        'deepseek_ai': ai_status,
        'timestamp': time.time()
    })

@app.route('/api/ai/stats')
def ai_stats():
    """إحصائيات DeepSeek AI"""
    try:
        stats_data = deepseek_ai.get_usage_stats() # تم تغيير اسم المتغير
        return jsonify(stats_data) # تم استخدام الاسم الجديد
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/test', methods=['POST'])
def test_ai():
    """اختبار DeepSeek AI"""
    try:
        data = request.get_json()
        test_message = data.get('message', 'مرحبا، هذا اختبار')

        result = deepseek_ai.chat(test_message, 'test_user')
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def process_message(message, user_id='anonymous'):
    """معالجة رسالة المستخدم باستخدام DeepSeek AI"""
    try:
        # الحصول على سياق المحادثة
        context = deepseek_ai.get_conversation_context(user_id, limit=3)

        # إرسال للذكاء الاصطناعي
        ai_result = deepseek_ai.chat(message, user_id, context)

        if ai_result['success']:
            return ai_result['response']
        else:
            # في حالة فشل AI، استخدم الرد الاحتياطي
            print(f"DeepSeek AI Error: {ai_result['error']}")
            return ai_result.get('fallback_response', get_simple_response(message))

    except Exception as e:
        print(f"خطأ في معالجة الرسالة: {e}")
        return get_simple_response(message)

def get_simple_response(message):
    """ردود بسيطة احتياطية"""
    message_lower = message.lower()

    if any(word in message_lower for word in ['مرحبا', 'السلام', 'أهلا', 'hello', 'hi']):
        return 'مرحباً بك! 👋 أنا المساعد الذكي. كيف يمكنني مساعدتك اليوم؟'
    elif any(word in message_lower for word in ['وقت', 'ساعة', 'time']):
        return f'الوقت الحالي هو: {datetime.now().strftime("%H:%M:%S")} ⏰'
    elif any(word in message_lower for word in ['شكرا', 'شكراً', 'thanks']):
        return 'العفو! سعيد لمساعدتك 😊 هل تحتاج لأي شيء آخر؟'
    else:
        return f'شكراً لرسالتك: "{message}". فريق خدمة العملاء سيتواصل معك قريباً! 📞'

def save_conversation(user_id, session_id, user_message, bot_response):
    """حفظ المحادثة في قاعدة البيانات"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        response_time = round(0.5 + (len(bot_response) / 100), 1)

        cursor.execute('''
            INSERT INTO conversations
            (user_id, session_id, user_message, bot_response, channel, response_time)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, session_id, user_message, bot_response, 'website', response_time))

        # تحديث إحصائيات المستخدم
        cursor.execute('''
            INSERT OR REPLACE INTO users
            (user_id, channel, last_seen, total_messages)
            VALUES (?, ?, CURRENT_TIMESTAMP,
                    COALESCE((SELECT total_messages FROM users WHERE user_id = ?), 0) + 1)
        ''', (user_id, 'website', user_id))

        conn.commit()
        conn.close()

    except Exception as e:
        print(f"خطأ في حفظ المحادثة: {e}")
        # إنشاء الجداول إذا لم تكن موجودة
        try:
            from setup_database import create_database
            create_database()
            print("تم إنشاء قاعدة البيانات تلقائياً")
        except:
            pass

# تم نقل هذا الجزء إلى الأسفل ليكون بعد تعريف جميع المسارات
# if __name__ == '__main__':
#     print("""
# ╔══════════════════════════════════════════════════════════════╗
# ║                                                              ║
# ║                🗄️  الباك-إند الحقيقي                        ║
# ║                                                              ║
# ║                  مع قاعدة بيانات حقيقية                     ║
# ║                                                              ║
# ╚══════════════════════════════════════════════════════════════╝
# 🚀 تشغيل الباك-إند على المنفذ 8001...
# 📊 قاعدة البيانات: SQLite (chatbot_data.db)
# 📋 APIs المتاحة:
#    📈 الإحصائيات: http://localhost:8001/api/stats
#    💬 الشات: http://localhost:8001/api/chat
#    🔍 الصحة: http://localhost:8001/api/health
# ⌨️  اضغط Ctrl+C للإيقاف
#     """)

# APIs المصادقة
@app.route('/api/auth/login', methods=['POST'])
@rate_limit('auth_login')
def login():
    """تسجيل الدخول"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')

        if not username or not password:
            return jsonify({'success': False, 'error': 'اسم المستخدم وكلمة المرور مطلوبان'}), 400

        ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
        user_agent = request.headers.get('User-Agent')

        result = secure_auth.authenticate_user(username, password, ip_address, user_agent)

        if result['success']:
            logger.info(f"تسجيل دخول ناجح: {username}")
            return jsonify(result)
        else:
            logger.warning(f"محاولة دخول فاشلة: {username}")
            return jsonify(result), 401

    except Exception as e:
        logger.error(f"خطأ في تسجيل الدخول: {e}")
        return jsonify({'success': False, 'error': 'خطأ في النظام'}), 500

if __name__ == '__main__':
    print("🚀 تشغيل الباك-إند الآمن والموحد...") # تم تعديل الرسالة
    print(f"   الخادم: http://localhost:{config.backend_port}")
    print(f"   🏠 الصفحة الرئيسية: http://localhost:{config.backend_port}/")
    print(f"   💬 الشات بوت: http://localhost:{config.backend_port}/web-integration/chatbot-widget.html")
    print(f"   📊 لوحة التحكم: http://localhost:{config.backend_port}/dashboard/index.html")
    print(f"   الصحة API: http://localhost:{config.backend_port}/api/health")
    print(f"   تسجيل الدخول API: http://localhost:{config.backend_port}/api/auth/login")
    print(f"   وضع التطوير: {config.is_debug}")

    app.run(host='0.0.0.0', port=config.backend_port, debug=config.is_debug)
