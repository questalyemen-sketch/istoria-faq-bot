from telebot import types

from config import ADMIN_IDS, MAX_SEARCH_RESULTS
from database import (
    add_faq,
    count_faqs,
    delete_faq,
    get_all_faqs,
    get_faq,
)
from knowledge import search_faq, search_multiple
from keyboards import (
    admin_menu,
    back_button,
    confirm_delete,
    main_menu,
)


# =========================================================
# حالات إضافة السؤال
# =========================================================

user_states = {}


def is_admin(user_id):
    return user_id in ADMIN_IDS


def clear_state(user_id):
    user_states.pop(user_id, None)


# =========================================================
# تسجيل Handlers
# =========================================================

def register_handlers(bot):

    # -----------------------------------------------------
    # /start
    # -----------------------------------------------------

    @bot.message_handler(commands=["start"])
    def start(message):
        clear_state(message.from_user.id)

        text = (
            "👋 أهلاً بك في بوت أسئلة iStoria.\n\n"
            "🤖 أرسل سؤالك عن تطبيق iStoria، "
            "وسأحاول العثور على الإجابة المناسبة.\n\n"
            "يمكنك أيضًا استخدام الأزرار الموجودة بالأسفل."
        )

        bot.send_message(
            message.chat.id,
            text,
            reply_markup=main_menu()
        )

    # -----------------------------------------------------
    # /help
    # -----------------------------------------------------

    @bot.message_handler(commands=["help"])
    def help_command(message):
        text = (
            "🆘 <b>مساعدة</b>\n\n"
            "أرسل سؤالك مباشرة، مثل:\n\n"
            "• كيف أغير المستوى؟\n"
            "• هل التطبيق مجاني؟\n"
            "• لماذا القصة مقفلة؟\n"
            "• كيف أستعيد الـ Streak؟\n"
            "• ما الفرق بين المجاني وPremium؟"
        )

        bot.send_message(
            message.chat.id,
            text,
            parse_mode="HTML",
            reply_markup=back_button()
        )

    # -----------------------------------------------------
    # /admin
    # -----------------------------------------------------

    @bot.message_handler(commands=["admin"])
    def admin_command(message):
        if not is_admin(message.from_user.id):
            bot.reply_to(
                message,
                "⛔ هذا القسم مخصص للمشرفين فقط."
            )
            return

        clear_state(message.from_user.id)

        bot.send_message(
            message.chat.id,
            "🛠 <b>لوحة الإدارة</b>\n\n"
            "اختر العملية التي تريد تنفيذها:",
            parse_mode="HTML",
            reply_markup=admin_menu()
        )

    # -----------------------------------------------------
    # /add
    # -----------------------------------------------------

    @bot.message_handler(commands=["add"])
    def add_command(message):
        if not is_admin(message.from_user.id):
            bot.reply_to(
                message,
                "⛔ هذا الأمر للمشرفين فقط."
            )
            return

        start_add_process(message)

    # -----------------------------------------------------
    # /cancel
    # -----------------------------------------------------

    @bot.message_handler(commands=["cancel"])
    def cancel_command(message):
        clear_state(message.from_user.id)

        bot.send_message(
            message.chat.id,
            "❌ تم إلغاء العملية."
        )

    # -----------------------------------------------------
    # /stats
    # -----------------------------------------------------

    @bot.message_handler(commands=["stats"])
    def stats_command(message):
        if not is_admin(message.from_user.id):
            return

        total = count_faqs()

        bot.send_message(
            message.chat.id,
            f"📊 <b>إحصائيات قاعدة المعرفة</b>\n\n"
            f"📚 عدد الأسئلة: <b>{total}</b>",
            parse_mode="HTML"
        )

    # -----------------------------------------------------
    # استقبال الرسائل النصية
    # -----------------------------------------------------

    @bot.message_handler(
        func=lambda message: True,
        content_types=["text"]
    )
    def handle_text(message):

        user_id = message.from_user.id
        text = message.text.strip()

        # إذا كان المستخدم داخل عملية إضافة
        if user_id in user_states:
            handle_add_process(message)
            return

        # تجاهل أوامر البوت
        if text.startswith("/"):
            return

        result = search_faq(text)

        if result:
            faq = result["faq"]

            response = (
                f"💡 <b>الإجابة:</b>\n\n"
                f"{faq['answer']}"
            )

            bot.send_message(
                message.chat.id,
                response,
                parse_mode="HTML"
            )

        else:
            bot.send_message(
                message.chat.id,
                "🤔 لم أجد إجابة دقيقة لهذا السؤال.\n\n"
                "حاول صياغة السؤال بطريقة أخرى، "
                "أو استخدم زر 🔎 البحث."
            )

    # =====================================================
    # Callback Queries
    # =====================================================

    @bot.callback_query_handler(func=lambda call: True)
    def callbacks(call):

        user_id = call.from_user.id
        data = call.data

        # -------------------------------------------------
        # القائمة الرئيسية
        # -------------------------------------------------

        if data == "back_main":
            clear_state(user_id)

            bot.edit_message_text(
                "🏠 <b>القائمة الرئيسية</b>\n\n"
                "اختر ما تريد:",
                call.message.chat.id,
                call.message.message_id,
                parse_mode="HTML",
                reply_markup=main_menu()
            )

        # -------------------------------------------------
        # عرض الأسئلة
        # -------------------------------------------------

        elif data == "faq_list":
            show_faq_list(call)

        # -------------------------------------------------
        # البحث
        # -------------------------------------------------

        elif data == "search_faq":
            bot.answer_callback_query(call.id)

            bot.send_message(
                call.message.chat.id,
                "🔎 أرسل السؤال الذي تريد البحث عنه."
            )

        # -------------------------------------------------
        # معلومات iStoria
        # -------------------------------------------------

        elif data == "about_istoria":
            bot.answer_callback_query(call.id)

            text = (
                "📚 <b>عن iStoria</b>\n\n"
                "iStoria تطبيق لتعلم اللغة الإنجليزية "
                "من خلال القصص والاستماع والمفردات "
                "والاختبارات والمستويات التعليمية."
            )

            bot.send_message(
                call.message.chat.id,
                text,
                parse_mode="HTML",
                reply_markup=back_button()
            )

        # -------------------------------------------------
        # Premium
        # -------------------------------------------------

        elif data == "premium_info":
            bot.answer_callback_query(call.id)

            text = (
                "💎 <b>iStoria Premium</b>\n\n"
                "يوفر Premium ميزات إضافية مثل "
                "التعلم والقراءة غير المحدودة، "
                "إزالة الإعلانات، وبعض ميزات "
                "التعلم والمحادثة والشهادات."
            )

            bot.send_message(
                call.message.chat.id,
                text,
                parse_mode="HTML",
                reply_markup=back_button()
            )

        # -------------------------------------------------
        # المساعدة
        # -------------------------------------------------

        elif data == "help":
            bot.answer_callback_query(call.id)

            bot.send_message(
                call.message.chat.id,
                "🆘 أرسل سؤالك عن iStoria مباشرة وسأبحث "
                "في قاعدة المعرفة.",
                reply_markup=back_button()
            )

        # =================================================
        # لوحة الإدارة
        # =================================================

        elif data.startswith("admin_"):

            if not is_admin(user_id):
                bot.answer_callback_query(
                    call.id,
                    "⛔ غير مصرح لك."
                )
                return

            admin_callback(call)

        # -------------------------------------------------
        # تأكيد حذف
        # -------------------------------------------------

        elif data.startswith("confirm_delete:"):

            if not is_admin(user_id):
                return

            faq_id = int(data.split(":")[1])

            if delete_faq(faq_id):
                text = "✅ تم حذف السؤال بنجاح."
            else:
                text = "❌ لم يتم العثور على السؤال."

            bot.answer_callback_query(call.id)

            bot.send_message(
                call.message.chat.id,
                text
            )

        bot.answer_callback_query(call.id)


    # =====================================================
    # بدء عملية إضافة سؤال
    # =====================================================

    def start_add_process(message):

        user_id = message.from_user.id

        user_states[user_id] = {
            "step": "question"
        }

        bot.send_message(
            message.chat.id,
            "➕ <b>إضافة سؤال جديد</b>\n\n"
            "أرسل الآن السؤال الذي تريد إضافته.\n\n"
            "مثال:\n"
            "كيف أغير مستواي في iStoria؟",
            parse_mode="HTML"
        )


    # =====================================================
    # معالجة إضافة السؤال
    # =====================================================

    def handle_add_process(message):

        user_id = message.from_user.id

        if not is_admin(user_id):
            clear_state(user_id)
            return

        state = user_states[user_id]
        text = message.text.strip()

        # -------------------------------------------------
        # السؤال
        # -------------------------------------------------

        if state["step"] == "question":

            state["question"] = text
            state["step"] = "answer"

            bot.send_message(
                message.chat.id,
                "✅ تم حفظ السؤال مؤقتًا.\n\n"
                "الآن أرسل <b>الإجابة</b>.",
                parse_mode="HTML"
            )

        # -------------------------------------------------
        # الإجابة
        # -------------------------------------------------

        elif state["step"] == "answer":

            state["answer"] = text
            state["step"] = "keywords"

            bot.send_message(
                message.chat.id,
                "👍 الآن أرسل الكلمات المفتاحية مفصولة بفواصل.\n\n"
                "مثال:\n"
                "تغيير المستوى, اغير الليفل, level, تعديل المستوى",
                parse_mode="HTML"
            )

        # -------------------------------------------------
        # الكلمات المفتاحية
        # -------------------------------------------------

        elif state["step"] == "keywords":

            state["keywords"] = text
            state["step"] = "category"

            bot.send_message(
                message.chat.id,
                "📂 أرسل تصنيف السؤال.\n\n"
                "مثال:\n"
                "المستويات"
            )

        # -------------------------------------------------
        # التصنيف
        # -------------------------------------------------

        elif state["step"] == "category":

            category = text or "عام"

            faq_id = add_faq(
                question=state["question"],
                answer=state["answer"],
                keywords=state["keywords"],
                category=category
            )

            clear_state(user_id)

            bot.send_message(
                message.chat.id,
                "🎉 <b>تمت إضافة السؤال بنجاح!</b>\n\n"
                f"🆔 رقم السؤال: <code>{faq_id}</code>\n"
                f"📂 التصنيف: <b>{category}</b>",
                parse_mode="HTML",
                reply_markup=admin_menu()
            )


    # =====================================================
    # عرض قائمة الأسئلة
    # =====================================================

    def show_faq_list(call):

        faqs = get_all_faqs()

        if not faqs:
            text = "📭 لا توجد أسئلة في قاعدة المعرفة."
        else:
            lines = ["📋 <b>الأسئلة الموجودة:</b>\n"]

            for faq in faqs[:30]:
                lines.append(
                    f"<code>{faq['id']}</code> — "
                    f"{faq['question']}"
                )

            if len(faqs) > 30:
                lines.append(
                    f"\n... ويوجد {len(faqs) - 30} سؤال إضافي."
                )

            text = "\n".join(lines)

        bot.answer_callback_query(call.id)

        bot.send_message(
            call.message.chat.id,
            text,
            parse_mode="HTML",
            reply_markup=back_button()
        )


    # =====================================================
    # عمليات الإدارة
    # =====================================================

    def admin_callback(call):

        data = call.data

        # إضافة
        if data == "admin_add":
            bot.answer_callback_query(call.id)
            start_add_process(call.message)

        # قائمة
        elif data == "admin_list":
            bot.answer_callback_query(call.id)
            show_faq_list(call)

        # إحصائيات
        elif data == "admin_stats":

            total = count_faqs()

            bot.answer_callback_query(call.id)

            bot.send_message(
                call.message.chat.id,
                f"📊 <b>إحصائيات البوت</b>\n\n"
                f"📚 إجمالي الأسئلة: <b>{total}</b>",
                parse_mode="HTML",
                reply_markup=back_button()
            )

        # حذف
        elif data == "admin_delete":

            bot.answer_callback_query(call.id)

            bot.send_message(
                call.message.chat.id,
                "🗑 أرسل رقم السؤال الذي تريد حذفه.\n\n"
                "مثال:\n"
                "<code>15</code>",
                parse_mode="HTML"
            )

            user_states[call.from_user.id] = {
                "step": "delete_id"
            }

        # بحث الإدارة
        elif data == "admin_search":

            bot.answer_callback_query(call.id)

            bot.send_message(
                call.message.chat.id,
                "🔎 أرسل كلمة أو سؤال للبحث في قاعدة المعرفة."
            )

        # تعديل
        elif data == "admin_edit":

            bot.answer_callback_query(call.id)

            bot.send_message(
                call.message.chat.id,
                "✏️ نظام تعديل الأسئلة سنفعّله في المرحلة التالية."
            )

        # استيراد
        elif data == "admin_import":

            bot.answer_callback_query(call.id)

            bot.send_message(
                call.message.chat.id,
                "📥 الاستيراد من JSON سنفعّله بعد اكتمال المشروع."
            )

        # تصدير
        elif data == "admin_export":

            bot.answer_callback_query(call.id)

            bot.send_message(
                call.message.chat.id,
                "📤 التصدير إلى JSON سنفعّله بعد اكتمال المشروع."
            )