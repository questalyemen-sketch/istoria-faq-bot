import html

from telebot import types

from config import ADMIN_IDS, MAX_SEARCH_RESULTS
from database import (
    add_faq,
    count_faqs,
    delete_faq,
    get_all_faqs,
    get_faq,
    update_faq,
)
from knowledge import search_faq, search_multiple
from keyboards import (
    admin_menu,
    back_button,
    confirm_delete,
    main_menu,
)


# =========================================================
# حالات المستخدمين
# =========================================================

user_states = {}


# =========================================================
# أدوات مساعدة
# =========================================================

def is_admin(user_id):
    return user_id in ADMIN_IDS


def clear_state(user_id):
    user_states.pop(user_id, None)


def safe_text(text):
    """حماية النص عند استخدام HTML."""
    return html.escape(str(text or ""))


def answer_callback(bot, call, text=None):
    """إجابة آمنة على ضغط الزر."""
    try:
        if text:
            bot.answer_callback_query(call.id, text)
        else:
            bot.answer_callback_query(call.id)
    except Exception:
        pass


# =========================================================
# تسجيل جميع Handlers
# =========================================================

def register_handlers(bot):

    # =====================================================
    # /start
    # =====================================================

    @bot.message_handler(commands=["start"])
    def start(message):

        user_id = message.from_user.id
        clear_state(user_id)

        text = (
            "👋 <b>أهلاً بك في بوت أسئلة iStoria</b>\n\n"
            "🤖 أرسل سؤالك عن تطبيق iStoria، "
            "وسأبحث لك عن أفضل إجابة موجودة في قاعدة المعرفة.\n\n"
            "يمكنك أيضًا استخدام الأزرار الموجودة بالأسفل."
        )

        bot.send_message(
            message.chat.id,
            text,
            parse_mode="HTML",
            reply_markup=main_menu()
        )

    # =====================================================
    # /help
    # =====================================================

    @bot.message_handler(commands=["help"])
    def help_command(message):

        clear_state(message.from_user.id)

        text = (
            "🆘 <b>مساعدة</b>\n\n"
            "أرسل سؤالك عن iStoria مباشرة.\n\n"
            "أمثلة:\n"
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

    # =====================================================
    # /admin
    # =====================================================

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

    # =====================================================
    # /add
    # =====================================================

    @bot.message_handler(commands=["add"])
    def add_command(message):

        if not is_admin(message.from_user.id):
            bot.reply_to(
                message,
                "⛔ هذا الأمر للمشرفين فقط."
            )
            return

        start_add_process(message)

    # =====================================================
    # /cancel
    # =====================================================

    @bot.message_handler(commands=["cancel"])
    def cancel_command(message):

        clear_state(message.from_user.id)

        bot.send_message(
            message.chat.id,
            "❌ تم إلغاء العملية."
        )

    # =====================================================
    # /stats
    # =====================================================

    @bot.message_handler(commands=["stats"])
    def stats_command(message):

        if not is_admin(message.from_user.id):
            bot.reply_to(
                message,
                "⛔ هذا الأمر للمشرفين فقط."
            )
            return

        total = count_faqs()

        bot.send_message(
            message.chat.id,
            "📊 <b>إحصائيات قاعدة المعرفة</b>\n\n"
            f"📚 عدد الأسئلة: <b>{total}</b>",
            parse_mode="HTML"
        )

    # =====================================================
    # استقبال الرسائل النصية
    # =====================================================

    @bot.message_handler(
        func=lambda message: True,
        content_types=["text"]
    )
    def handle_text(message):

        user_id = message.from_user.id
        text = message.text.strip()

        if not text:
            return

        # -----------------------------------------------
        # إذا كان المستخدم داخل عملية إدارية
        # -----------------------------------------------

        if user_id in user_states:

            handle_state_message(message)
            return

        # -----------------------------------------------
        # تجاهل الأوامر
        # -----------------------------------------------

        if text.startswith("/"):
            return

        # -----------------------------------------------
        # البحث في قاعدة المعرفة
        # -----------------------------------------------

        result = search_faq(text)

        if result:

            faq = result["faq"]

            response = (
                "💡 <b>الإجابة:</b>\n\n"
                f"{safe_text(faq['answer'])}"
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
                "جرّب صياغة السؤال بطريقة أخرى، "
                "أو استخدم زر 🔎 البحث."
            )

    # =====================================================
    # Callback Queries
    # =====================================================

    @bot.callback_query_handler(func=lambda call: True)
    def callbacks(call):

        user_id = call.from_user.id
        data = call.data

        # =================================================
        # الرئيسية
        # =================================================

        if data == "back_main":

            clear_state(user_id)

            answer_callback(bot, call)

            try:
                bot.edit_message_text(
                    "🏠 <b>القائمة الرئيسية</b>\n\n"
                    "اختر ما تريد:",
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode="HTML",
                    reply_markup=main_menu()
                )
            except Exception:
                bot.send_message(
                    call.message.chat.id,
                    "🏠 <b>القائمة الرئيسية</b>",
                    parse_mode="HTML",
                    reply_markup=main_menu()
                )

            return

        # =================================================
        # الأسئلة الشائعة
        # =================================================

        if data == "faq_list":

            answer_callback(bot, call)
            show_faq_list(call)
            return

        # =================================================
        # البحث
        # =================================================

        if data == "search_faq":

            answer_callback(bot, call)

            bot.send_message(
                call.message.chat.id,
                "🔎 أرسل سؤالك الآن وسأبحث في قاعدة المعرفة."
            )

            return

        # =================================================
        # عن iStoria
        # =================================================

        if data == "about_istoria":

            answer_callback(bot, call)

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

            return

        # =================================================
        # Premium
        # =================================================

        if data == "premium_info":

            answer_callback(bot, call)

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

            return

        # =================================================
        # المساعدة
        # =================================================

        if data == "help":

            answer_callback(bot, call)

            bot.send_message(
                call.message.chat.id,
                "🆘 أرسل سؤالك عن iStoria مباشرة، "
                "وسأبحث في قاعدة المعرفة.",
                reply_markup=back_button()
            )

            return

        # =================================================
        # أزرار الإدارة
        # =================================================

        if data.startswith("admin_"):

            if not is_admin(user_id):

                answer_callback(
                    bot,
                    call,
                    "⛔ غير مصرح لك."
                )

                return

            admin_callback(call)
            return

        # =================================================
        # تأكيد الحذف
        # =================================================

        if data.startswith("confirm_delete:"):

            if not is_admin(user_id):

                answer_callback(
                    bot,
                    call,
                    "⛔ غير مصرح لك."
                )

                return

            try:
                faq_id = int(
                    data.split(":", 1)[1]
                )
            except (ValueError, IndexError):

                answer_callback(
                    bot,
                    call,
                    "❌ رقم السؤال غير صحيح."
                )

                return

            deleted = delete_faq(faq_id)

            if deleted:

                answer_callback(
                    bot,
                    call,
                    "✅ تم الحذف."
                )

                bot.send_message(
                    call.message.chat.id,
                    f"✅ تم حذف السؤال رقم <code>{faq_id}</code> بنجاح.",
                    parse_mode="HTML",
                    reply_markup=admin_menu()
                )

            else:

                answer_callback(
                    bot,
                    call,
                    "❌ السؤال غير موجود."
                )

            return

        # =================================================
        # التصنيفات
        # =================================================

        if data.startswith("cat_"):

            category_map = {
                "cat_app": "التطبيق",
                "cat_free": "النسخة المجانية",
                "cat_premium": "Premium",
                "cat_stories": "القصص",
                "cat_listening": "الاستماع",
                "cat_pronunciation": "النطق",
                "cat_levels": "المستويات",
                "cat_streak": "Streak",
                "cat_payment": "الدفع والاشتراك",
                "cat_account": "الحساب",
                "cat_learning": "التعلم",
                "cat_other": "أخرى",
            }

            category = category_map.get(data)

            answer_callback(bot, call)

            if category:
                show_category(call, category)

            return

        # =================================================
        # أي Callback غير معروف
        # =================================================

        answer_callback(bot, call)


    # =====================================================
    # بدء إضافة سؤال
    # =====================================================

    def start_add_process(message):

        user_id = message.from_user.id

        if not is_admin(user_id):
            return

        user_states[user_id] = {
            "step": "question"
        }

        bot.send_message(
            message.chat.id,
            "➕ <b>إضافة سؤال جديد</b>\n\n"
            "أرسل الآن السؤال الذي تريد إضافته.\n\n"
            "مثال:\n"
            "كيف أغير مستواي في iStoria؟\n\n"
            "❌ لإلغاء العملية اكتب /cancel",
            parse_mode="HTML"
        )


    # =====================================================
    # معالجة الحالات
    # =====================================================

    def handle_state_message(message):

        user_id = message.from_user.id
        text = message.text.strip()

        if not is_admin(user_id):

            clear_state(user_id)

            bot.send_message(
                message.chat.id,
                "⛔ غير مصرح لك."
            )

            return

        state = user_states.get(user_id)

        if not state:
            return

        step = state.get("step")

        # -------------------------------------------------
        # إضافة سؤال
        # -------------------------------------------------

        if step == "question":

            if len(text) < 3:

                bot.send_message(
                    message.chat.id,
                    "⚠️ السؤال قصير جدًا.\n"
                    "أرسل سؤالًا واضحًا."
                )

                return

            state["question"] = text
            state["step"] = "answer"

            bot.send_message(
                message.chat.id,
                "✅ تم حفظ السؤال.\n\n"
                "الآن أرسل <b>الإجابة</b>.",
                parse_mode="HTML"
            )

            return

        # -------------------------------------------------
        # إضافة إجابة
        # -------------------------------------------------

        if step == "answer":

            if len(text) < 2:

                bot.send_message(
                    message.chat.id,
                    "⚠️ الإجابة قصيرة جدًا."
                )

                return

            state["answer"] = text
            state["step"] = "keywords"

            bot.send_message(
                message.chat.id,
                "👍 الآن أرسل الكلمات المفتاحية "
                "مفصولة بفواصل.\n\n"
                "مثال:\n"
                "تغيير المستوى, اغير الليفل, level, تعديل المستوى",
                parse_mode="HTML"
            )

            return

        # -------------------------------------------------
        # الكلمات المفتاحية
        # -------------------------------------------------

        if step == "keywords":

            state["keywords"] = text
            state["step"] = "category"

            bot.send_message(
                message.chat.id,
                "📂 الآن أرسل تصنيف السؤال.\n\n"
                "مثال:\n"
                "المستويات"
            )

            return

        # -------------------------------------------------
        # التصنيف
        # -------------------------------------------------

        if step == "category":

            category = text or "عام"

            try:

                faq_id = add_faq(
                    question=state["question"],
                    answer=state["answer"],
                    keywords=state["keywords"],
                    category=category
                )

            except Exception as error:

                clear_state(user_id)

                print(
                    f"❌ خطأ أثناء إضافة السؤال: {error}"
                )

                bot.send_message(
                    message.chat.id,
                    "❌ حدث خطأ أثناء حفظ السؤال."
                )

                return

            clear_state(user_id)

            bot.send_message(
                message.chat.id,
                "🎉 <b>تمت إضافة السؤال بنجاح!</b>\n\n"
                f"🆔 رقم السؤال: <code>{faq_id}</code>\n"
                f"📂 التصنيف: <b>{safe_text(category)}</b>",
                parse_mode="HTML",
                reply_markup=admin_menu()
            )

            return

        # -------------------------------------------------
        # حذف سؤال
        # -------------------------------------------------

        if step == "delete_id":

            try:
                faq_id = int(text)
            except ValueError:

                bot.send_message(
                    message.chat.id,
                    "⚠️ أرسل رقم السؤال فقط.\n\n"
                    "مثال:\n"
                    "<code>15</code>",
                    parse_mode="HTML"
                )

                return

            faq = get_faq(faq_id)

            if not faq:

                bot.send_message(
                    message.chat.id,
                    "❌ لا يوجد سؤال بهذا الرقم."
                )

                return

            state["faq_id"] = faq_id
            state["step"] = "delete_confirm"

            bot.send_message(
                message.chat.id,
                "⚠️ <b>تأكيد الحذف</b>\n\n"
                f"🆔 الرقم: <code>{faq_id}</code>\n"
                f"❓ السؤال:\n{safe_text(faq['question'])}\n\n"
                "هل تريد حذف هذا السؤال؟",
                parse_mode="HTML",
                reply_markup=confirm_delete(faq_id)
            )

            return

        # -------------------------------------------------
        # تعديل سؤال
        # -------------------------------------------------

        if step == "edit_id":

            try:
                faq_id = int(text)
            except ValueError:

                bot.send_message(
                    message.chat.id,
                    "⚠️ أرسل رقم السؤال فقط."
                )

                return

            faq = get_faq(faq_id)

            if not faq:

                bot.send_message(
                    message.chat.id,
                    "❌ لا يوجد سؤال بهذا الرقم."
                )

                return

            state["faq_id"] = faq_id
            state["step"] = "edit_question"

            bot.send_message(
                message.chat.id,
                "✏️ أرسل السؤال الجديد.\n\n"
                f"السؤال الحالي:\n"
                f"{safe_text(faq['question'])}",
                parse_mode="HTML"
            )

            return

        # -------------------------------------------------
        # تعديل نص السؤال
        # -------------------------------------------------

        if step == "edit_question":

            state["question"] = text
            state["step"] = "edit_answer"

            bot.send_message(
                message.chat.id,
                "✏️ أرسل الإجابة الجديدة."
            )

            return

        # -------------------------------------------------
        # تعديل الإجابة
        # -------------------------------------------------

        if step == "edit_answer":

            state["answer"] = text
            state["step"] = "edit_keywords"

            bot.send_message(
                message.chat.id,
                "🔑 أرسل الكلمات المفتاحية الجديدة.\n\n"
                "استخدم الفواصل بين الكلمات."
            )

            return

        # -------------------------------------------------
        # تعديل الكلمات المفتاحية
        # -------------------------------------------------

        if step == "edit_keywords":

            state["keywords"] = text
            state["step"] = "edit_category"

            bot.send_message(
                message.chat.id,
                "📂 أرسل التصنيف الجديد."
            )

            return

        # -------------------------------------------------
        # تعديل التصنيف وحفظ التعديل
        # -------------------------------------------------

        if step == "edit_category":

            category = text or "عام"

            faq_id = state["faq_id"]

            success = update_faq(
                faq_id=faq_id,
                question=state["question"],
                answer=state["answer"],
                keywords=state["keywords"],
                category=category
            )

            clear_state(user_id)

            if success:

                bot.send_message(
                    message.chat.id,
                    "✅ <b>تم تعديل السؤال بنجاح.</b>\n\n"
                    f"🆔 رقم السؤال: <code>{faq_id}</code>",
                    parse_mode="HTML",
                    reply_markup=admin_menu()
                )

            else:

                bot.send_message(
                    message.chat.id,
                    "❌ تعذر تعديل السؤال."
                )

            return

        # -------------------------------------------------
        # البحث الإداري
        # -------------------------------------------------

        if step == "admin_search":

            results = search_multiple(
                text,
                limit=MAX_SEARCH_RESULTS
            )

            clear_state(user_id)

            send_search_results(
                message.chat.id,
                results,
                admin=True
            )

            return


    # =====================================================
    # عرض قائمة الأسئلة
    # =====================================================

    def show_faq_list(call):

        faqs = get_all_faqs()

        if not faqs:

            bot.send_message(
                call.message.chat.id,
                "📭 لا توجد أسئلة في قاعدة المعرفة.",
                reply_markup=back_button()
            )

            return

        lines = [
            "📋 <b>الأسئلة الموجودة:</b>\n"
        ]

        for faq in faqs[:30]:

            lines.append(
                f"<code>{faq['id']}</code> — "
                f"{safe_text(faq['question'])}"
            )

        if len(faqs) > 30:

            lines.append(
                f"\n📚 ويوجد {len(faqs) - 30} سؤال إضافي."
            )

        bot.send_message(
            call.message.chat.id,
            "\n".join(lines),
            parse_mode="HTML",
            reply_markup=back_button()
        )


    # =====================================================
    # عرض تصنيف
    # =====================================================

    def show_category(call, category):

        faqs = [
            faq
            for faq in get_all_faqs()
            if faq["category"] == category
        ]

        if not faqs:

            bot.send_message(
                call.message.chat.id,
                f"📭 لا توجد أسئلة في تصنيف <b>{safe_text(category)}</b>.",
                parse_mode="HTML",
                reply_markup=back_button()
            )

            return

        lines = [
            f"📚 <b>{safe_text(category)}</b>\n"
        ]

        for faq in faqs[:30]:

            lines.append(
                f"❓ <code>{faq['id']}</code> — "
                f"{safe_text(faq['question'])}\n"
                f"💡 {safe_text(faq['answer'])}"
            )

        bot.send_message(
            call.message.chat.id,
            "\n\n".join(lines),
            parse_mode="HTML",
            reply_markup=back_button()
        )


    # =====================================================
    # نتائج البحث
    # =====================================================

    def send_search_results(chat_id, results, admin=False):

        if not results:

            bot.send_message(
                chat_id,
                "🔎 لم أجد نتائج."
            )

            return

        lines = [
            "🔎 <b>نتائج البحث:</b>\n"
        ]

        for item in results:

            faq = item["faq"]
            score = item["score"]

            if score <= 0:
                continue

            if admin:

                lines.append(
                    f"🆔 <code>{faq['id']}</code>\n"
                    f"❓ {safe_text(faq['question'])}\n"
                    f"📊 التطابق: <b>{score:.0%}</b>\n"
                    f"📂 {safe_text(faq['category'])}"
                )

            else:

                lines.append(
                    f"❓ <b>{safe_text(faq['question'])}</b>\n"
                    f"💡 {safe_text(faq['answer'])}\n"
                    f"📊 التطابق: {score:.0%}"
                )

        bot.send_message(
            chat_id,
            "\n\n".join(lines),
            parse_mode="HTML"
        )


    # =====================================================
    # وظائف الإدارة
    # =====================================================

    def admin_callback(call):

        data = call.data
        user_id = call.from_user.id

        # -------------------------------------------------
        # إضافة
        # -------------------------------------------------

        if data == "admin_add":

            answer_callback(bot, call)
            start_add_process(call.message)

            return

        # -------------------------------------------------
        # قائمة الأسئلة
        # -------------------------------------------------

        if data == "admin_list":

            answer_callback(bot, call)
            show_faq_list(call)

            return

        # -------------------------------------------------
        # الإحصائيات
        # -------------------------------------------------

        if data == "admin_stats":

            total = count_faqs()

            answer_callback(bot, call)

            bot.send_message(
                call.message.chat.id,
                "📊 <b>إحصائيات البوت</b>\n\n"
                f"📚 إجمالي الأسئلة: <b>{total}</b>",
                parse_mode="HTML",
                reply_markup=back_button()
            )

            return

        # -------------------------------------------------
        # حذف
        # -------------------------------------------------

        if data == "admin_delete":

            answer_callback(bot, call)

            clear_state(user_id)

            user_states[user_id] = {
                "step": "delete_id"
            }

            bot.send_message(
                call.message.chat.id,
                "🗑 <b>حذف سؤال</b>\n\n"
                "أرسل رقم السؤال الذي تريد حذفه.\n\n"
                "مثال:\n"
                "<code>15</code>\n\n"
                "❌ للإلغاء: /cancel",
                parse_mode="HTML"
            )

            return

        # -------------------------------------------------
        # البحث
        # -------------------------------------------------

        if data == "admin_search":

            answer_callback(bot, call)

            clear_state(user_id)

            user_states[user_id] = {
                "step": "admin_search"
            }

            bot.send_message(
                call.message.chat.id,
                "🔎 أرسل كلمة أو سؤالًا للبحث "
                "في قاعدة المعرفة."
            )

            return

        # -------------------------------------------------
        # تعديل
        # -------------------------------------------------

        if data == "admin_edit":

            answer_callback(bot, call)

            clear_state(user_id)

            user_states[user_id] = {
                "step": "edit_id"
            }

            bot.send_message(
                call.message.chat.id,
                "✏️ <b>تعديل سؤال</b>\n\n"
                "أرسل رقم السؤال الذي تريد تعديله.\n\n"
                "مثال:\n"
                "<code>15</code>",
                parse_mode="HTML"
            )

            return

        # -------------------------------------------------
        # استيراد
        # -------------------------------------------------

        if data == "admin_import":

            answer_callback(bot, call)

            bot.send_message(
                call.message.chat.id,
                "📥 استيراد الأسئلة من JSON "
                "سيتم تفعيله في المرحلة التالية.",
                reply_markup=back_button()
            )

            return

        # -------------------------------------------------
        # تصدير
        # -------------------------------------------------

        if data == "admin_export":

            answer_callback(bot, call)

            bot.send_message(
                call.message.chat.id,
                "📤 تصدير قاعدة المعرفة إلى JSON "
                "سيتم تفعيله في المرحلة التالية.",
                reply_markup=back_button()
            )

            return