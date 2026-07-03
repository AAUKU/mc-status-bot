import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from mcstatus import JavaServer

# إعدادات
logging.basicConfig(level=logging.INFO)
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))
SERVER_HOST = os.getenv("SERVER_HOST")
SERVER_PORT = int(os.getenv("SERVER_PORT", 25565))
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 60))

last_message_id = None
last_status = None # لتخزين الحالة السابقة

def get_server_info():
    try:
        server = JavaServer.lookup(f"{SERVER_HOST}:{SERVER_PORT}")
        status = server.status()
        players = status.players.sample
        player_names = ", ".join([p.name for p in players]) if players else "لا يوجد لاعبون"
        text = (f"🟢 السيرفر يعمل!\n"
                f"عدد اللاعبين: {status.players.online}/{status.players.max}\n"
                f"اللاعبون: {player_names}\n"
                f"سرعة الاستجابة (Ping): {status.latency:.2f}ms")
        return text, True
    except:
        return "🔴 السيرفر متوقف حالياً.", False

async def check_server(context: ContextTypes.DEFAULT_TYPE):
    global last_message_id, last_status
    text, is_online = get_server_info()
    
    # تحديث الرسالة المثبتة
    if last_message_id:
        try:
            await context.bot.edit_message_text(chat_id=CHAT_ID, message_id=last_message_id, text=text)
        except:
            msg = await context.bot.send_message(chat_id=CHAT_ID, text=text)
            last_message_id = msg.message_id
    else:
        msg = await context.bot.send_message(chat_id=CHAT_ID, text=text)
        last_message_id = msg.message_id
        await context.bot.pin_chat_message(chat_id=CHAT_ID, message_id=last_message_id)

    # تنبيه ذكي عند تغير الحالة
    if last_status is not None and last_status != is_online:
        await context.bot.send_message(chat_id=CHAT_ID, text=f"⚠️ تنبيه: حالة السيرفر تغيرت! \n{text}")
    
    last_status = is_online

# أوامر تفاعلية
async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text, _ = get_server_info()
    await update.message.reply_text(text)

async def players_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    _, is_online = get_server_info()
    if not is_online:
        await update.message.reply_text("السيرفر متوقف حالياً.")
        return
    server = JavaServer.lookup(f"{SERVER_HOST}:{SERVER_PORT}")
    players = server.status().players.sample
    names = ", ".join([p.name for p in players]) if players else "لا أحد متصل."
    await update.message.reply_text(f"اللاعبون المتصلون: {names}")

async def ping_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        server = JavaServer.lookup(f"{SERVER_HOST}:{SERVER_PORT}")
        latency = server.status().latency
        await update.message.reply_text(f"الاستجابة (Ping): {latency:.2f}ms")
    except:
        await update.message.reply_text("لا يمكن الوصول للسيرفر.")

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # إضافة الأوامر
    application.add_handler(CommandHandler("status", status_cmd))
    application.add_handler(CommandHandler("players", players_cmd))
    application.add_handler(CommandHandler("ping", ping_cmd))

    if application.job_queue:
        application.job_queue.run_repeating(check_server, interval=CHECK_INTERVAL, first=5)
    
    application.run_polling()

if __name__ == '__main__':
    main()
    
