import time
import telebot

from config import BOT_TOKEN, validate_config
from database import init_database
from faq_data import seed_database
from handlers import register_handlers


# =========================================================
# iStoria FAQ Bot
# =========================================================

def main():
    print("🚀 تشغيل iStoria FAQ Bot...")

    # التحقق من الإعدادات
    validate_config()

    # إنشاء قاعدة البيانات
    print("🗄️ تهيئة قاعدة البيانات...")
    init_database()

    # تحميل قاعدة الأسئلة الأولية
    print("📚 تحميل قاعدة المعرفة...")
    seed_database()

    # إنشاء البوت
    bot = telebot.TeleBot(
        BOT_TOKEN,
        parse_mode="HTML"
    )

    # تسجيل جميع الأوامر والأزرار
    register_handlers(bot)

    print("✅ البوت يعمل الآن.")
    print("🤖 iStoria FAQ Bot is running...")

    # تشغيل مستمر مع إعادة المحاولة عند حدوث خطأ
    while True:
        try:
            bot.infinity_polling(
                skip_pending=True,
                timeout=30,
                long_polling_timeout=30
            )

        except Exception as error:
            print(f"⚠️ حدث خطأ: {error}")
            print("🔄 إعادة تشغيل الاتصال خلال 5 ثوانٍ...")

            time.sleep(5)


if __name__ == "__main__":
    main()