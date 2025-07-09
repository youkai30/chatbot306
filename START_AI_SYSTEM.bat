@echo off
chcp 65001 >nul
title نظام الشات بوت الذكي مع DeepSeek AI

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║           🧠 نظام الشات بوت الذكي مع DeepSeek AI             ║
echo ║                                                              ║
echo ║                    ذكاء اصطناعي حقيقي                      ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo 🔄 بدء تشغيل النظام الذكي...
echo.

REM فحص Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python غير مثبت
    pause
    exit /b 1
)

echo ✅ Python متاح

REM فحص وتثبيت المكتبات المطلوبة
echo 📦 فحص المكتبات المطلوبة...

python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo 📦 تثبيت Flask...
    pip install flask flask-cors
)

python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo 📦 تثبيت requests...
    pip install requests
)

echo ✅ جميع المكتبات متاحة

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

REM اختبار DeepSeek AI
echo 🧠 اختبار DeepSeek AI...
python deepseek_ai.py
if errorlevel 1 (
    echo ⚠️  مشكلة في DeepSeek AI، سيعمل النظام بالردود الاحتياطية
) else (
    echo ✅ DeepSeek AI يعمل بنجاح
)

echo.
echo 🚀 تشغيل النظام الذكي...
echo.

REM تشغيل الباك-إند مع DeepSeek AI
echo 🧠 تشغيل الباك-إند الذكي...
start "AI Backend" python real_backend.py

echo ⏳ انتظار 5 ثوان...
timeout /t 5 /nobreak >nul

REM تشغيل الفرونت-إند
echo 🌐 تشغيل الفرونت-إند...
start "Frontend Server" python simple_server.py --port 8000

echo ⏳ انتظار 3 ثوان...
timeout /t 3 /nobreak >nul

echo.
echo 📋 النظام الذكي يعمل على:
echo    🧠 الباك-إند الذكي: http://localhost:8001
echo    🏠 الصفحة الرئيسية: http://localhost:8000
echo    💬 الشات بوت الذكي: http://localhost:8000/web-integration/chatbot-widget.html
echo    📊 لوحة التحكم: http://localhost:8000/dashboard/index.html
echo.

echo 🧪 اختبار الاتصال...
curl -s http://localhost:8001/api/health >nul 2>&1
if errorlevel 1 (
    echo ⚠️  الباك-إند قد يحتاج وقت إضافي للبدء
) else (
    echo ✅ الباك-إند الذكي يعمل بنجاح
)

echo.
echo 🌐 فتح الشات بوت الذكي...
start http://localhost:8000/web-integration/chatbot-widget.html

echo.
echo 🧠 المميزات الذكية الجديدة:
echo    ✅ DeepSeek AI للذكاء الاصطناعي الحقيقي
echo    ✅ فهم السياق والمتابعة
echo    ✅ ردود ذكية ومتنوعة
echo    ✅ معالجة طبيعية للغة العربية
echo    ✅ تعلم من المحادثات السابقة
echo.
echo 💡 جرب هذه الأسئلة:
echo    - "مرحبا، كيف يمكنك مساعدتي؟"
echo    - "اشرح لي عن خدماتكم"
echo    - "ما رأيك في الذكاء الاصطناعي؟"
echo    - "كيف يمكنني تحسين موقعي الإلكتروني؟"
echo.
echo ⌨️  اضغط أي مفتاح للإغلاق
pause >nul

echo.
echo 👋 تم إيقاف النظام الذكي
