import os
import logging
import threading
from flask import Flask
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from mcstatus import JavaServer

# إعدادات الـ Web Server
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is running!"

def run_web():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# إعدادات البوت
logging.basicConfig(level=logging.INFO)
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))
SERVER_HOST = os.getenv("SERVER_HOST")
SERVER_PORT = int(os.getenv("SERVER_PORT", 25565))

# متغير لتخزين الرسالة الأخيرة (سيفقد قيمته عند إعادة التشغيل)
last_message_id = None

async def get_server_status_text():
    try:
        # إضافة timeout لزيادة دقة الفحص ومنع الخطأ
        server = JavaServer.lookup(f"{SERVER_HOST}:{SERVER_PORT}", timeout=10)
        status = server.status()
        players = status.players.sample
        player_names = ", ".join([p.name for p in players]) if players else "لا يوجد لاعبون"
        return f"🟢 السيرفر يعمل!\nعدد اللاعبين: {status.players.online}/{status.players.max}\nاللاعبون: {player_names}\nالاستجابة: {status.latency:.2f}ms", True
    except Exception as e:
        return f"🔴 السيرفر متوقف حالياً.\n(السبب: {str(e)[:20]}...)", False

async def check_server(context: ContextTypes.DEFAULT_TYPE):
    global last_message_id
    text, is_online = await get_server_status_text()
    
    # محاولة حذف الرسالة القديمة قبل إرسال جديدة (للحفاظ على نظافة الجروب)
    if last_message_id:
        try:
            await context.bot.delete_message(chat_id=CHAT_ID, message_id=last_message_id)
        except:
            pass 
            
    # إرسال رسالة جديدة
    msg = await context.bot.send_message(chat_id=CHAT_ID, text=text)
    last_message_id = msg.message_id
    
    # تثبيت الرسالة
    try:
        await context.bot.pin_chat_message(chat_id=CHAT_ID, message_id=last_message_id)
    except:
        pass

def main():
    threading.Thread(target=run_web, daemon=True).start()
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # الجدول الزمني للفحص (كل دقيقة)
    if application.job_queue:
        application.job_queue.run_repeating(check_server, interval=60, first=5)
    
    application.run_polling()

if __name__ == '__main__':
    main()

