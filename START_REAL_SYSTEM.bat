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
echo 🚀 تشغيل النظام الحقيقي الموحد...
echo.

REM الأولوية لتشغيل سكريبت البايثون إذا كان موجودًا ومحدثًا
if exist "start_real_system.py" (
    echo 🐍 تشغيل عبر start_real_system.py...
    python start_real_system.py
) else (
    echo  সরাসরি تشغيل real_backend.py مباشرة...
    REM تشغيل الباك-إند الموحد (API + واجهة أمامية)
    echo 🗄️  تشغيل الباك-إند الموحد...
    start "Unified Real Backend" python real_backend.py

    echo ⏳ انتظار 5 ثوان...
    timeout /t 5 /nobreak >nul
)

echo.
echo 📋 النظام الحقيقي الموحد يعمل على (يفترض المنفذ 8001 أو كما في .env):
echo    🗄️  الباك-إند و الواجهة: http://localhost:8001
echo    🏠 الصفحة الرئيسية: http://localhost:8001/
echo    💬 الشات بوت: http://localhost:8001/web-integration/chatbot-widget.html
echo    📊 لوحة التحكم: http://localhost:8001/dashboard/index.html
echo.

echo 🧪 اختبار الاتصال...
curl -s http://localhost:8001/api/health >nul 2>&1
if errorlevel 1 (
    echo ⚠️  الباك-إند قد يحتاج وقت إضافي للبدء أو تأكد من تشغيله على المنفذ الصحيح.
) else (
    echo ✅ الباك-إند الموحد يستجيب بنجاح.
)

echo.
echo 🌐 فتح المتصفح للوحة التحكم...
start http://localhost:8001/dashboard/index.html

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
