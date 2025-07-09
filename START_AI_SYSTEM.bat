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
echo 🚀 تشغيل النظام الذكي الموحد...
echo.

REM تشغيل الباك-إند الموحد (API + واجهة أمامية) مع DeepSeek AI
echo 🧠 تشغيل الباك-إند الذكي الموحد...
start "Unified AI Backend" python real_backend.py

echo ⏳ انتظار 5 ثوان...
timeout /t 5 /nobreak >nul

REM تشغيل AI Agent
echo 🤖 تشغيل AI Agent...
start "AI Agent" python ai-agent\simple_run.py

echo ⏳ انتظار 3 ثوان...
timeout /t 3 /nobreak >nul

echo.
echo 📋 النظام الذكي الموحد يعمل على (يفترض المنفذ 8001 أو كما في .env):
echo    🧠 الباك-إند و الواجهة: http://localhost:8001
echo    🏠 الصفحة الرئيسية: http://localhost:8001/
echo    💬 الشات بوت الذكي: http://localhost:8001/web-integration/chatbot-widget.html
echo    📊 لوحة التحكم: http://localhost:8001/dashboard/index.html
echo    🤖 AI Agent: http://localhost:5000
echo.

echo 🧪 اختبار الاتصال...
curl -s http://localhost:8001/api/health >nul 2>&1
if errorlevel 1 (
    echo ⚠️  الباك-إند الموحد قد يحتاج وقت إضافي للبدء أو تأكد من تشغيله على المنفذ الصحيح.
) else (
    echo ✅ الباك-إند الذكي الموحد يستجيب بنجاح.
)

echo.
echo 🌐 فتح الشات بوت الذكي...
start http://localhost:8001/web-integration/chatbot-widget.html

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
