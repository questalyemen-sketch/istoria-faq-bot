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
    print("=" * 50)
    print("🚀 تشغيل iStoria FAQ Bot")
    print("=" * 50)

    # -----------------------------------------------------
    # 1. التحقق من إعدادات البوت
    # -----------------------------------------------------
    print("⚙️ التحقق من الإعدادات...")

    try:
        validate_config()
    except Exception as error:
        print(f"❌ خطأ في إعدادات البوت: {error}")
        return

    print("✅ إعدادات البوت صحيحة.")

    # -----------------------------------------------------
    # 2. تهيئة قاعدة البيانات
    # -----------------------------------------------------
    print("🗄️ تهيئة قاعدة البيانات...")

    try:
        init_database()
        print("✅ قاعدة البيانات جاهزة.")
    except Exception as error:
        print(f"❌ فشل تهيئة قاعدة البيانات: {error}")
        return

    # -----------------------------------------------------
    # 3. تحميل قاعدة المعرفة
    # -----------------------------------------------------
    print("📚 تحميل قاعدة أسئلة iStoria...")

    try:
        added = seed_database()
        print(f"✅ تمت معالجة قاعدة المعرفة. تمت إضافة: {added} سؤال.")
    except Exception as error:
        print(f"❌ خطأ أثناء تحميل قاعدة المعرفة: {error}")
        return

    # -----------------------------------------------------
    # 4. إنشاء كائن البوت
    # -----------------------------------------------------
    print("🤖 إنشاء اتصال Telegram...")

    try:
        bot = telebot.TeleBot(
            BOT_TOKEN,
            parse_mode="HTML"
        )
    except Exception as error:
        print(f"❌ فشل إنشاء البوت: {error}")
        return

    # -----------------------------------------------------
    # 5. تسجيل الأوامر والأزرار والرسائل
    # -----------------------------------------------------
    print("🔧 تسجيل Handlers...")

    try:
        register_handlers(bot)
        print("✅ تم تسجيل جميع Handlers.")
    except Exception as error:
        print(f"❌ فشل تسجيل Handlers: {error}")
        return

    # -----------------------------------------------------
    # 6. تشغيل البوت
    # -----------------------------------------------------
    print("=" * 50)
    print("✅ iStoria FAQ Bot يعمل الآن")
    print("🤖 Telegram polling started...")
    print("=" * 50)

    while True:
        try:
            bot.infinity_polling(
                skip_pending=True,
                timeout=30,
                long_polling_timeout=30
            )

        except KeyboardInterrupt:
            print("\n🛑 تم إيقاف البوت يدويًا.")
            break

        except Exception as error:
            print(f"⚠️ حدث خطأ أثناء تشغيل البوت: {error}")
            print("🔄 إعادة الاتصال خلال 5 ثوانٍ...")
            time.sleep(5)


# =========================================================
# تشغيل البرنامج
# =========================================================

if __name__ == "__main__":
    main()