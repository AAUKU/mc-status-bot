import os
import logging
from telegram.ext import ApplicationBuilder, ContextTypes

# إعداد الـ Logging (لمنع خطأ NameError)
logging.basicConfig(level=logging.INFO)

# قراءة المتغيرات من Render
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 60))

# فحص المتغيرات
if not BOT_TOKEN or not CHAT_ID:
    print("خطأ: يرجى التأكد من إضافة BOT_TOKEN و CHAT_ID في إعدادات Render")
    exit(1)

async def check_server(context: ContextTypes.DEFAULT_TYPE):
    # هنا ضع الكود الخاص بك لفحص السيرفر
    # تم وضع هذا الكود لضمان أن job_queue يعمل
    print("فحص السيرفر...")

def main():
    # بناء التطبيق
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # تفعيل الـ JobQueue
    if application.job_queue is not None:
        application.job_queue.run_repeating(check_server, interval=CHECK_INTERVAL, first=10)
    else:
        print("خطأ: لم يتم تفعيل JobQueue بشكل صحيح.")
        exit(1)

    print("البوت يعمل الآن!")
    application.run_polling()

if __name__ == '__main__':
    main()
    
