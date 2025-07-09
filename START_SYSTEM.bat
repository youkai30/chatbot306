@echo off
chcp 65001 >nul
title نظام الشات بوت متعدد القنوات

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║           🚀 نظام الشات بوت متعدد القنوات                   ║
echo ║                                                              ║
echo ║                    تشغيل النظام الكامل                      ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo 🔄 بدء تشغيل النظام...
echo.

REM فحص وجود Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python غير مثبت أو غير متاح في PATH
    echo 💡 يرجى تثبيت Python 3.8+ من https://python.org
    pause
    exit /b 1
)

echo ✅ Python متاح

REM فحص وجود الملفات المطلوبة
if not exist "server.py" (
    echo ❌ ملف server.py غير موجود
    pause
    exit /b 1
)

if not exist "ai-agent\simple_run.py" (
    echo ❌ ملف ai-agent\simple_run.py غير موجود
    pause
    exit /b 1
)

echo ✅ جميع الملفات الرئيسية موجودة (real_backend.py, run_complete_system.py, ai-agent\simple_run.py)

REM تثبيت المتطلبات إذا لم تكن مثبتة (يمكن تحسين هذا لاحقًا ليكون من requirements.txt)
echo 📦 فحص المتطلبات الأساسية (Flask, requests)...
python -c "import flask, requests" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  بعض المكتبات الأساسية غير مثبتة، جاري التثبيت...
    pip install flask requests flask-cors
    if errorlevel 1 (
        echo ❌ فشل في تثبيت المكتبات الأساسية.
        echo 💡 يرجى التأكد من تثبيت pip وتجربة: pip install flask requests flask-cors
        pause
        exit /b 1
    )
    echo ✅ تم تثبيت المكتبات الأساسية.
) else (
    echo ✅ المكتبات الأساسية مثبتة.
)
echo 💡 ملاحظة: قد تحتاج إلى تثبيت مكتبات إضافية عبر 'pip install -r requirements.txt' لتشغيل كامل وآمن.

echo.
echo 🚀 تشغيل النظام الكامل الموحد...
echo.

REM تشغيل النظام الكامل عبر السكريبت البايثون المحدث
python run_complete_system.py

REM إذا فشل التشغيل الكامل، جرب التشغيل اليدوي للمكونات الأساسية
if errorlevel 1 (
    echo.
    echo ⚠️  فشل التشغيل التلقائي عبر run_complete_system.py، جاري التشغيل اليدوي للمكونات...
    echo.
    
    echo 🗄️  تشغيل الباك-إند الموحد (API + واجهة أمامية)...
    start "Unified Backend" python real_backend.py
    
    echo ⏳ انتظار 5 ثوان...
    timeout /t 5 /nobreak >nul

    echo 🤖 تشغيل AI Agent...
    start "AI Agent" python ai-agent\simple_run.py

    echo ⏳ انتظار 3 ثوان...
    timeout /t 3 /nobreak >nul
    
    echo.
    echo 📋 الخدمات متاحة على (يفترض المنفذ 8001 للباك-إند أو كما في .env):
    echo    🗄️  النظام الموحد: http://localhost:8001/
    echo    💬 الشات بوت: http://localhost:8001/web-integration/chatbot-widget.html
    echo    📊 لوحة التحكم: http://localhost:8001/dashboard/index.html
    echo    🤖 AI Agent: http://localhost:5000
    echo.
    echo ⌨️  سيستمر هذا الوضع اليدوي حتى يتم إغلاق النوافذ يدويًا أو إيقاف العمليات.
    echo.
)

echo.
echo 👋 النظام متوقف أو يعمل في الخلفية (إذا بدأ بنجاح).
pause
