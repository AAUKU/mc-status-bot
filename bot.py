import logging
import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
import os
from dotenv import load_dotenv

# هذا السطر سيجعل البوت لا يتوقف إذا لم يجد الملف
load_dotenv(override=True) 

# الآن، اجعل البوت يقرأ المتغيرات مباشرة من نظام Render
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")


# إعداد السجلات (Logging) لمتابعة أي أخطاء في Console
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

load_dotenv()

# المتغيرات
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))
SERVER_HOST = os.getenv("SERVER_HOST")
SERVER_PORT = int(os.getenv("SERVER_PORT"))
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "60"))

# تخزين الحالة محلياً
status_cache = {"last_status": None, "last_players": 0}

async def check_server(context: ContextTypes.DEFAULT_TYPE):
    """وظيفة الفحص الدوري للسيرفر"""
    try:
        server = BedrockServer.lookup(f"{SERVER_HOST}:{SERVER_PORT}")
        status = server.status()
        
        current_status = "online"
        current_players = status.players_online
        
        # إشعار التشغيل
        if status_cache["last_status"] != "online":
            await context.bot.send_message(
                chat_id=CHAT_ID, 
                text=f"✅ **السيرفر يعمل الآن!**\nاللاعبين: {current_players}/{status.players_max}"
            )
            
        status_cache["last_status"] = "online"
        status_cache["last_players"] = current_players

    except Exception as e:
        # إشعار التوقف
        if status_cache["last_status"] != "offline":
            await context.bot.send_message(chat_id=CHAT_ID, text="❌ **السيرفر متوقف حالياً.**")
            status_cache["last_status"] = "offline"

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر /status"""
    try:
        server = BedrockServer.lookup(f"{SERVER_HOST}:{SERVER_PORT}")
        status = server.status()
        await update.message.reply_text(
            f"📊 **حالة السيرفر:** يعمل\n"
            f"👥 **اللاعبين:** {status.players_online}/{status.players_max}\n"
            f"📍 **Ping:** {int(status.latency)}ms"
        )
    except:
        await update.message.reply_text("🔴 **السيرفر متوقف حالياً.**")

async def players_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر /players"""
    try:
        server = BedrockServer.lookup(f"{SERVER_HOST}:{SERVER_PORT}")
        status = server.status()
        await update.message.reply_text(f"👥 **اللاعبين المتصلين:** {status.players_online}/{status.players_max}")
    except:
        await update.message.reply_text("🔴 **السيرفر متوقف، لا يوجد لاعبين.**")

if __name__ == '__main__':
    # بناء البوت
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # إضافة الأوامر
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("players", players_command))
    
    # إعداد الفحص الدوري كل 60 ثانية
    job_queue = application.job_queue
    job_queue.run_repeating(check_server, interval=CHECK_INTERVAL, first=10)
    
    print("Bot is running...")
    application.run_polling()
  
