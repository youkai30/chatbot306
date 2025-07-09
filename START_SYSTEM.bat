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

echo ✅ جميع الملفات موجودة

REM تثبيت المتطلبات إذا لم تكن مثبتة
echo 📦 فحص المتطلبات...
python -c "import flask, requests" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  بعض المكتبات غير مثبتة، جاري التثبيت...
    pip install flask requests flask-cors >nul 2>&1
    if errorlevel 1 (
        echo ❌ فشل في تثبيت المكتبات
        echo 💡 قم بتشغيل: pip install flask requests flask-cors
        pause
        exit /b 1
    )
    echo ✅ تم تثبيت المكتبات
) else (
    echo ✅ جميع المكتبات مثبتة
)

echo.
echo 🚀 تشغيل النظام الكامل...
echo.

REM تشغيل النظام الكامل
python run_complete_system.py

REM إذا فشل التشغيل الكامل، جرب التشغيل اليدوي
if errorlevel 1 (
    echo.
    echo ⚠️  فشل التشغيل التلقائي، جاري المحاولة اليدوية...
    echo.
    
    echo 🤖 تشغيل AI Agent...
    start "AI Agent" python ai-agent\simple_run.py
    
    echo ⏳ انتظار 5 ثوان...
    timeout /t 5 /nobreak >nul
    
    echo 🌐 تشغيل الخادم الرئيسي...
    echo.
    echo 📋 الخدمات ستكون متاحة على:
    echo    🏠 الصفحة الرئيسية: http://localhost:8000
    echo    💬 الشات بوت: http://localhost:8000/web-integration/chatbot-widget.html
    echo    📊 لوحة التحكم: http://localhost:8000/dashboard/index.html
    echo    🤖 AI Agent: http://localhost:5000
    echo.
    echo ⌨️  اضغط Ctrl+C للإيقاف
    echo.
    
    python server.py
)

echo.
echo 👋 تم إيقاف النظام
pause
