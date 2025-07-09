#!/bin/bash

# اختبار مفتاح DeepSeek API
# Test DeepSeek API Key

echo "🚀 اختبار مفتاح DeepSeek API..."
echo "Testing DeepSeek API Key..."
echo ""

# اختبار بسيط
echo "📡 إرسال طلب اختبار..."
echo "Sending test request..."

curl -s https://api.deepseek.com/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-b451df17c5034399a1795f68b7ac4f5b" \
  -d '{
    "model": "deepseek-chat",
    "messages": [
      {
        "role": "user",
        "content": "مرحبا، هذا اختبار سريع لمفتاح DeepSeek API"
      }
    ],
    "max_tokens": 100,
    "temperature": 0.7
  }' | jq '.'

echo ""
echo "✅ إذا رأيت رداً من DeepSeek أعلاه، فالمفتاح يعمل بشكل صحيح!"
echo "✅ If you see a response from DeepSeek above, your API key is working correctly!"
echo ""
echo "💰 تكلفة هذا الاختبار: ~$0.000014 (أقل من سنت واحد!)"
echo "💰 Cost of this test: ~$0.000014 (less than a penny!)"
