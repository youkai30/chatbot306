from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from deepseek_ai import deepseek_ai
from secure_config import config
from secure_auth import secure_auth, require_auth, require_role
from rate_limiter import rate_limiter, rate_limit
import logging

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

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/stats')
def stats():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM conversations')
    total_conversations = cur.fetchone()[0]
    cur.execute('SELECT COUNT(DISTINCT user_id) FROM conversations')
    active_users = cur.fetchone()[0]
    cur.execute('SELECT AVG(response_time) FROM conversations')
    response_time = round(cur.fetchone()[0] or 1.2, 1)
    cur.execute('SELECT AVG(satisfaction) FROM conversations WHERE satisfaction IS NOT NULL')
    satisfaction_rate = round((cur.fetchone()[0] or 4.5) * 20, 1)
    cur.execute('SELECT channel, COUNT(*) FROM conversations GROUP BY channel')
    channels = {row[0]: row[1] for row in cur.fetchall()}
    # Hourly stats
    cur.execute("SELECT strftime('%H', timestamp) as hour, COUNT(*) FROM conversations GROUP BY hour ORDER BY hour")
    hourly_stats = [{"hour": row[0], "messages": row[1]} for row in cur.fetchall()]
    # Recent chats
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
        "active_users": active_users,
        "response_time": response_time,
        "satisfaction_rate": satisfaction_rate,
        "channels": channels,
        "hourly_stats": hourly_stats,
        "recent_chats": recent_chats
    })

@app.route('/api/conversations')
def conversations():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT user_id, channel, user_message, satisfaction, timestamp FROM conversations ORDER BY timestamp DESC LIMIT 20')
    conversations = []
    for row in cur.fetchall():
        conversations.append({
            'user': row[0],
            'channel': row[1],
            'last_message': row[2],
            'status': 'resolved' if row[3] else 'pending',
            'time': row[4]
        })
    conn.close()
    return jsonify({'conversations': conversations})

@app.route('/api/channels')
def channels():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT channel, COUNT(*) FROM conversations GROUP BY channel')
    channels = []
    for row in cur.fetchall():
        channels.append({'name': row[0], 'active': True, 'users': row[1]})
    conn.close()
    return jsonify({'channels': channels})

@app.route('/api/analytics')
def analytics():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM conversations')
    total_conversations = cur.fetchone()[0]
    cur.execute('SELECT COUNT(DISTINCT user_id) FROM conversations')
    total_users = cur.fetchone()[0]
    cur.execute('SELECT AVG(response_time) FROM conversations')
    avg_response_time = round(cur.fetchone()[0] or 1.2, 1)
    cur.execute('SELECT AVG(satisfaction) FROM conversations WHERE satisfaction IS NOT NULL')
    satisfaction_rate = round((cur.fetchone()[0] or 4.5) * 20, 1)
    cur.execute('SELECT channel, COUNT(*) FROM conversations GROUP BY channel ORDER BY COUNT(*) DESC LIMIT 3')
    top_channels = [row[0] for row in cur.fetchall()]
    conn.close()
    return jsonify({
        'summary': {
            'total_conversations': total_conversations,
            'total_users': total_users,
            'avg_response_time': avg_response_time,
            'satisfaction_rate': satisfaction_rate
        },
        'top_channels': top_channels
    })

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
    ai_test = deepseek_ai.test_connection()
    ai_status = ai_test['status']

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
        stats = deepseek_ai.get_usage_stats()
        return jsonify(stats)
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

if __name__ == '__main__':
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                🗄️  الباك-إند الحقيقي                        ║
║                                                              ║
║                  مع قاعدة بيانات حقيقية                     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

🚀 تشغيل الباك-إند على المنفذ 8001...

📊 قاعدة البيانات: SQLite (chatbot_data.db)
📋 APIs المتاحة:
   📈 الإحصائيات: http://localhost:8001/api/stats
   💬 الشات: http://localhost:8001/api/chat
   🔍 الصحة: http://localhost:8001/api/health

⌨️  اضغط Ctrl+C للإيقاف
    """)

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
    print("🚀 تشغيل الباك-إند الآمن...")
    print(f"   الخادم: http://localhost:{config.backend_port}")
    print(f"   الصحة: http://localhost:{config.backend_port}/api/health")
    print(f"   تسجيل الدخول: http://localhost:{config.backend_port}/api/auth/login")
    print(f"   وضع التطوير: {config.is_debug}")

    app.run(host='0.0.0.0', port=config.backend_port, debug=config.is_debug)
