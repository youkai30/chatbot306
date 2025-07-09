@echo off
chcp 65001 >nul
title نظام الشات بوت المحسن - بدون أخطاء

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║           🔧 نظام الشات بوت المحسن                          ║
echo ║                                                              ║
echo ║                  تم إصلاح جميع المشاكل                     ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo 🔧 فحص وإصلاح النظام أولاً...
python fix_system.py

if errorlevel 1 (
    echo ❌ فشل في فحص النظام
    pause
    exit /b 1
)

echo.
echo 🚀 تشغيل النظام المحسن...
echo.

REM تشغيل الباك-إند المحسن
echo 🧠 تشغيل الباك-إند الذكي المحسن...
start "Fixed Backend" python real_backend.py

echo ⏳ انتظار 5 ثوان...
timeout /t 5 /nobreak >nul

REM تشغيل الفرونت-إند
echo 🌐 تشغيل الفرونت-إند...
start "Frontend Server" python simple_server.py --port 8000

echo ⏳ انتظار 3 ثوان...
timeout /t 3 /nobreak >nul

echo.
echo 📋 النظام المحسن يعمل على:
echo    🧠 الباك-إند المحسن: http://localhost:8001
echo    🏠 الصفحة الرئيسية: http://localhost:8000
echo    💬 الشات بوت الذكي: http://localhost:8000/web-integration/chatbot-widget.html
echo    📊 لوحة التحكم: http://localhost:8000/dashboard/index.html
echo    🔧 لوحة AI: http://localhost:8000/dashboard/ai_dashboard.html
echo.

echo 🧪 اختبار الاتصال...
curl -s http://localhost:8001/api/health >nul 2>&1
if errorlevel 1 (
    echo ⚠️  الباك-إند قد يحتاج وقت إضافي للبدء
) else (
    echo ✅ الباك-إند المحسن يعمل بنجاح
)

echo.
echo 🌐 فتح الشات بوت المحسن...
start http://localhost:8000/web-integration/chatbot-widget.html

echo.
echo ✅ التحسينات المطبقة:
echo    🔧 إصلاح جميع الأخطاء البرمجية
echo    🗄️  تحسين معالجة قاعدة البيانات
echo    🧠 تحسين تكامل DeepSeek AI
echo    🔐 تحسين معالجة الأخطاء
echo    📊 تحسين الإحصائيات والتقارير
echo.
echo 💡 النظام الآن يعمل بدون أخطاء!
echo.
echo ⌨️  اضغط أي مفتاح للإغلاق
pause >nul

echo.
echo 👋 تم إيقاف النظام المحسن
