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
if not exist "backend_server.py" (
    echo ❌ ملف backend_server.py غير موجود
    pause
    exit /b 1
)

echo ✅ جميع الملفات موجودة

echo.
echo 🚀 تشغيل النظام الكامل...
echo.

REM تشغيل النظام الكامل
python run_full_system.py

REM إذا فشل، جرب التشغيل اليدوي
if errorlevel 1 (
    echo.
    echo ⚠️  فشل التشغيل التلقائي، جاري التشغيل اليدوي...
    echo.
    
    echo 🗄️  تشغيل الباك-إند الحقيقي...
    start "Backend Server" python backend_server.py
    
    echo ⏳ انتظار 5 ثوان...
    timeout /t 5 /nobreak >nul
    
    echo 🌐 تشغيل الفرونت-إند...
    start "Frontend Server" python simple_server.py --port 8000
    
    echo ⏳ انتظار 3 ثوان...
    timeout /t 3 /nobreak >nul
    
    echo 🤖 تشغيل AI Agent...
    start "AI Agent" python ai-agent\simple_run.py
    
    echo ⏳ انتظار 3 ثوان...
    timeout /t 3 /nobreak >nul
    
    echo.
    echo 📋 الخدمات متاحة على:
    echo    🗄️  الباك-إند: http://localhost:8001
    echo    🏠 الصفحة الرئيسية: http://localhost:8000
    echo    💬 الشات بوت: http://localhost:8000/web-integration/chatbot-widget.html
    echo    📊 لوحة التحكم: http://localhost:8000/dashboard/index.html
    echo    🤖 AI Agent: http://localhost:5000
    echo.
    echo 🌐 فتح المتصفح...
    start http://localhost:8000
    
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
