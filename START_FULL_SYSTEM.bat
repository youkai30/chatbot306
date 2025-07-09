@echo off
chcp 65001 >nul
title نظام الشات بوت الكامل مع باك-إند حقيقي

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║           🚀 نظام الشات بوت الكامل مع باك-إند حقيقي         ║
echo ║                                                              ║
echo ║                    🗄️  قاعدة بيانات + APIs                  ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo 🔄 بدء تشغيل النظام الكامل...
echo.

REM فحص Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python غير مثبت
    pause
    exit /b 1
)

echo ✅ Python متاح

REM فحص الملفات
if not exist "real_backend.py" (
    echo ❌ ملف real_backend.py غير موجود
    pause
    exit /b 1
)
if not exist "run_full_system.py" (
    echo ❌ ملف run_full_system.py غير موجود
    pause
    exit /b 1
)
if not exist "ai-agent\simple_run.py" (
    echo ❌ ملف ai-agent\simple_run.py غير موجود
    pause
    exit /b 1
)

echo ✅ جميع الملفات الرئيسية موجودة

echo.
echo 🚀 تشغيل النظام الكامل الموحد...
echo.

REM تشغيل النظام الكامل عبر السكريبت البايثون المحدث
python run_full_system.py

REM إذا فشل، جرب التشغيل اليدوي للمكونات الأساسية
if errorlevel 1 (
    echo.
    echo ⚠️  فشل التشغيل التلقائي عبر run_full_system.py، جاري التشغيل اليدوي للمكونات...
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
    echo 📋 الخدمات متاحة على:
    echo    🗄️  النظام الموحد (API + واجهة): http://localhost:8001 (أو المنفذ المحدد في .env)
    echo    🏠 الصفحة الرئيسية: http://localhost:8001/
    echo    💬 الشات بوت: http://localhost:8001/web-integration/chatbot-widget.html
    echo    📊 لوحة التحكم: http://localhost:8001/dashboard/index.html
    echo    🤖 AI Agent: http://localhost:5000
    echo.
    echo 🌐 فتح المتصفح (يفترض أن المنفذ هو 8001 أو كما في .env)...
    start http://localhost:8001
    
    echo.
    echo 💡 المميزات الجديدة:
    echo    ✅ قاعدة بيانات SQLite حقيقية
    echo    ✅ بيانات واقعية ومباشرة
    echo    ✅ إحصائيات تتحدث مع كل رسالة
    echo    ✅ محادثات محفوظة ومؤرخة
    echo.
    echo ⌨️  اضغط أي مفتاح للإغلاق
    pause >nul
)

echo.
echo 👋 تم إيقاف النظام
