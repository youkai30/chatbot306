@echo off
chcp 65001 >nul
title نظام الشات بوت الحقيقي مع قاعدة البيانات

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║           🗄️  نظام الشات بوت الحقيقي                        ║
echo ║                                                              ║
echo ║                    مع قاعدة بيانات حقيقية                   ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo 🔄 بدء تشغيل النظام الحقيقي...
echo.

REM فحص Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python غير مثبت
    pause
    exit /b 1
)

echo ✅ Python متاح

REM فحص Flask
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo 📦 تثبيت Flask...
    pip install flask flask-cors
    if errorlevel 1 (
        echo ❌ فشل في تثبيت Flask
        pause
        exit /b 1
    )
)

echo ✅ Flask متاح

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

echo.
echo 🚀 تشغيل النظام الحقيقي...
echo.

REM تشغيل الباك-إند الحقيقي
echo 🗄️  تشغيل الباك-إند الحقيقي...
start "Real Backend" python real_backend.py

echo ⏳ انتظار 5 ثوان...
timeout /t 5 /nobreak >nul

REM تشغيل الفرونت-إند
echo 🌐 تشغيل الفرونت-إند...
start "Frontend Server" python simple_server.py --port 8000

echo ⏳ انتظار 3 ثوان...
timeout /t 3 /nobreak >nul

echo.
echo 📋 النظام الحقيقي يعمل على:
echo    🗄️  الباك-إند الحقيقي: http://localhost:8001
echo    🏠 الصفحة الرئيسية: http://localhost:8000
echo    💬 الشات بوت: http://localhost:8000/web-integration/chatbot-widget.html
echo    📊 لوحة التحكم: http://localhost:8000/dashboard/index.html
echo.

echo 🧪 اختبار الاتصال...
curl -s http://localhost:8001/api/health >nul 2>&1
if errorlevel 1 (
    echo ⚠️  الباك-إند قد يحتاج وقت إضافي للبدء
) else (
    echo ✅ الباك-إند يعمل بنجاح
)

echo.
echo 🌐 فتح المتصفح...
start http://localhost:8000/dashboard/index.html

echo.
echo 💡 المميزات الحقيقية:
echo    ✅ قاعدة بيانات SQLite حقيقية
echo    ✅ بيانات تُحفظ مع كل رسالة
echo    ✅ إحصائيات مباشرة ومحدثة
echo    ✅ محادثات مؤرخة ومنظمة
echo.
echo 🔐 بيانات الدخول:
echo    اسم المستخدم: admin
echo    كلمة المرور: admin123
echo.
echo ⌨️  اضغط أي مفتاح للإغلاق
pause >nul

echo.
echo 👋 تم إيقاف النظام
