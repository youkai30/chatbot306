@echo off
chcp 65001 >nul
title تشغيل سريع - النظام الآمن

echo 🚀 تشغيل سريع للنظام الآمن...

REM اختبار سريع
echo 🧪 اختبار سريع...
python quick_test.py

if errorlevel 1 (
    echo ❌ فشل الاختبار
    pause
    exit /b 1
)

echo ✅ الاختبار نجح

REM تشغيل الباك-إند
echo 🔐 تشغيل الباك-إند الآمن...
start "Unified Secure Backend" python real_backend.py

timeout /t 3 /nobreak >nul

echo ✅ النظام الموحد يعمل! (يفترض المنفذ 8001 أو كما في .env)
echo 🔐 تسجيل الدخول: http://localhost:8001/dashboard/secure_login.html
echo 💬 الشات: http://localhost:8001/web-integration/chatbot-widget.html

start http://localhost:8001/dashboard/secure_login.html

pause
