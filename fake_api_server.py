import http.server
import socketserver
import json

PORT = 8001

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/stats':
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            data = {
                "total_conversations": 1234,
                "active_users": 567,
                "response_time": 1.2,
                "satisfaction_rate": 94.5,
                "channels": {
                    "WhatsApp": 350,
                    "Messenger": 220,
                    "Telegram": 180,
                    "Instagram": 90,
                    "الموقع": 120
                },
                "hourly_stats": [
                    {"hour": h, "messages": (h*7)%100+20} for h in range(24)
                ],
                "recent_chats": [
                    {"time": "منذ 5 دقائق", "user": "أحمد محمد", "channel": "whatsapp", "message": "أريد معلومات عن المنتج", "status": "active"},
                    {"time": "منذ 12 دقيقة", "user": "فاطمة علي", "channel": "messenger", "message": "كيف يمكنني الطلب؟", "status": "resolved"},
                    {"time": "منذ 18 دقيقة", "user": "محمد سالم", "channel": "telegram", "message": "ما هي أوقات العمل؟", "status": "resolved"}
                ]
            }
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
        elif self.path == '/api/conversations':
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            data = {
                "conversations": [
                    {"id": 1, "user": "أحمد محمد", "channel": "whatsapp", "last_message": "أريد معلومات عن المنتج", "status": "active", "time": "منذ 5 دقائق"},
                    {"id": 2, "user": "فاطمة علي", "channel": "messenger", "last_message": "كيف يمكنني الطلب؟", "status": "resolved", "time": "منذ 12 دقيقة"},
                    {"id": 3, "user": "محمد سالم", "channel": "telegram", "last_message": "ما هي أوقات العمل؟", "status": "resolved", "time": "منذ 18 دقيقة"}
                ]
            }
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
        elif self.path == '/api/channels':
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            data = {
                "channels": [
                    {"name": "WhatsApp", "active": True, "users": 350},
                    {"name": "Messenger", "active": True, "users": 220},
                    {"name": "Telegram", "active": True, "users": 180},
                    {"name": "Instagram", "active": False, "users": 90},
                    {"name": "الموقع", "active": True, "users": 120}
                ]
            }
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
        elif self.path == '/api/analytics':
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            data = {
                "summary": {
                    "total_conversations": 1234,
                    "total_users": 567,
                    "avg_response_time": 1.2,
                    "satisfaction_rate": 94.5
                },
                "top_channels": ["WhatsApp", "Messenger", "Telegram"]
            }
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
        else:
            super().do_GET()

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving fake API at http://localhost:{PORT}/api/stats ...")
        httpd.serve_forever()
