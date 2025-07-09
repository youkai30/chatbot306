@echo off
chcp 65001 >nul
title النظام الآمن - شات بوت محمي ومحسن

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║           🔐 النظام الآمن - شات بوت محمي                    ║
echo ║                                                              ║
echo ║              أمان متقدم + Rate Limiting + JWT                ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo 🔧 فحص وإعداد النظام الآمن...
echo.

REM فحص Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python غير مثبت
    pause
    exit /b 1
)

echo ✅ Python متاح

REM تثبيت المكتبات المطلوبة
echo 📦 تثبيت المكتبات الآمنة...
python install_requirements.py

if errorlevel 1 (
    echo ❌ فشل في تثبيت المكتبات
    pause
    exit /b 1
)

echo ✅ جميع المكتبات متاحة

REM فحص ملف الإعدادات
if not exist ".env" (
    echo ⚠️  ملف .env غير موجود، سيتم إنشاؤه...
    python secure_config.py
)

echo ✅ ملف الإعدادات جاهز

REM فحص قاعدة البيانات
if not exist "chatbot_data.db" (
    echo 🗄️  إنشاء قاعدة البيانات...
    python setup_database.py
    if errorlevel 1 (
        echo ❌ فشل في إنشاء قاعدة البيانات
        pause
        exit /b 1
    )
) else (
    echo ✅ قاعدة البيانات موجودة
)

REM اختبار الأنظمة الآمنة
echo 🔐 اختبار الأنظمة الآمنة...

echo   🔧 اختبار الإعدادات...
python secure_config.py >nul 2>&1
if errorlevel 1 (
    echo ❌ مشكلة في الإعدادات
    echo يرجى مراجعة ملف .env
    pause
    exit /b 1
)

echo   🛡️  اختبار نظام المصادقة...
python secure_auth.py >nul 2>&1
if errorlevel 1 (
    echo ❌ مشكلة في نظام المصادقة
    pause
    exit /b 1
)

echo   ⚡ اختبار Rate Limiting...
python rate_limiter.py >nul 2>&1
if errorlevel 1 (
    echo ❌ مشكلة في Rate Limiting
    pause
    exit /b 1
)

echo   🧠 اختبار DeepSeek AI...
python deepseek_ai.py >nul 2>&1
if errorlevel 1 (
    echo ⚠️  مشكلة في DeepSeek AI، سيعمل النظام بالردود الاحتياطية
) else (
    echo ✅ DeepSeek AI يعمل بنجاح
)

echo ✅ جميع الأنظمة الآمنة جاهزة

echo.
echo 🚀 تشغيل النظام الآمن...
echo.

REM تشغيل الباك-إند الآمن
echo 🔐 تشغيل الباك-إند الآمن...
start "Secure Backend" python real_backend.py

echo ⏳ انتظار 5 ثوان...
timeout /t 5 /nobreak >nul

REM تشغيل الفرونت-إند
echo 🌐 تشغيل الفرونت-إند...
start "Frontend Server" python simple_server.py --port 8000

echo ⏳ انتظار 3 ثوان...
timeout /t 3 /nobreak >nul

echo.
echo 📋 النظام الآمن يعمل على:
echo    🔐 الباك-إند الآمن: http://localhost:8001
echo    🏠 الصفحة الرئيسية: http://localhost:8000
echo    💬 الشات بوت الآمن: http://localhost:8000/web-integration/chatbot-widget.html
echo    📊 لوحة التحكم: http://localhost:8000/dashboard/index.html
echo    🔧 لوحة AI: http://localhost:8000/dashboard/ai_dashboard.html
echo.

echo 🧪 اختبار الاتصال الآمن...
curl -s http://localhost:8001/api/health >nul 2>&1
if errorlevel 1 (
    echo ⚠️  الباك-إند قد يحتاج وقت إضافي للبدء
) else (
    echo ✅ الباك-إند الآمن يعمل بنجاح
)

echo.
echo 🌐 فتح النظام الآمن...
start http://localhost:8000/web-integration/chatbot-widget.html

echo.
echo 🔐 المميزات الأمنية الجديدة:
echo    ✅ مفتاح API محمي في ملف .env
echo    ✅ نظام مصادقة JWT متقدم
echo    ✅ Rate Limiting لمنع إساءة الاستخدام
echo    ✅ CORS آمن ومحدود
echo    ✅ تشفير كلمات المرور
echo    ✅ نظام logging متقدم
echo    ✅ معالجة أخطاء محسنة
echo    ✅ حماية من SQL injection
echo.
echo 🔑 بيانات الدخول الافتراضية:
echo    المستخدم: admin
echo    كلمة المرور: SecureAdmin123!
echo.
echo 💡 APIs الجديدة:
echo    🔐 تسجيل الدخول: POST /api/auth/login
echo    👤 الملف الشخصي: GET /api/auth/profile
echo    📊 إحصائيات المدير: GET /api/admin/stats
echo.
echo ⚠️  تذكير أمني:
echo    - غيّر كلمة مرور المدير الافتراضية
echo    - راجع إعدادات ملف .env
echo    - لا تشارك مفتاح DeepSeek API
echo.
echo ⌨️  اضغط أي مفتاح للإغلاق
pause >nul

echo.
echo 👋 تم إيقاف النظام الآمن
