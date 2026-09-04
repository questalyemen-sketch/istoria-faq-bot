from telebot import types


# =========================================================
# القائمة الرئيسية
# =========================================================

def main_menu():
    keyboard = types.InlineKeyboardMarkup(row_width=2)

    keyboard.add(
        types.InlineKeyboardButton(
            "❓ الأسئلة الشائعة",
            callback_data="faq_list"
        ),
        types.InlineKeyboardButton(
            "🔎 البحث",
            callback_data="search_faq"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "📚 عن iStoria",
            callback_data="about_istoria"
        ),
        types.InlineKeyboardButton(
            "💎 Premium",
            callback_data="premium_info"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "🆘 المساعدة",
            callback_data="help"
        )
    )

    return keyboard


# =========================================================
# لوحة الإدارة
# =========================================================

def admin_menu():
    keyboard = types.InlineKeyboardMarkup(row_width=2)

    keyboard.add(
        types.InlineKeyboardButton(
            "➕ إضافة سؤال",
            callback_data="admin_add"
        ),
        types.InlineKeyboardButton(
            "✏️ تعديل سؤال",
            callback_data="admin_edit"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "🗑 حذف سؤال",
            callback_data="admin_delete"
        ),
        types.InlineKeyboardButton(
            "📋 عرض الأسئلة",
            callback_data="admin_list"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "🔎 البحث",
            callback_data="admin_search"
        ),
        types.InlineKeyboardButton(
            "📊 الإحصائيات",
            callback_data="admin_stats"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "📥 استيراد الأسئلة",
            callback_data="admin_import"
        ),
        types.InlineKeyboardButton(
            "📤 تصدير الأسئلة",
            callback_data="admin_export"
        )
    )

    return keyboard


# =========================================================
# زر الرجوع
# =========================================================

def back_button(callback_data="back_main"):
    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            "🔙 رجوع",
            callback_data=callback_data
        )
    )

    return keyboard


# =========================================================
# تأكيد الحذف
# =========================================================

def confirm_delete(faq_id):
    keyboard = types.InlineKeyboardMarkup(row_width=2)

    keyboard.add(
        types.InlineKeyboardButton(
            "✅ نعم، احذف",
            callback_data=f"confirm_delete:{faq_id}"
        ),
        types.InlineKeyboardButton(
            "❌ إلغاء",
            callback_data="admin_list"
        )
    )

    return keyboard


# =========================================================
# تصنيفات الأسئلة
# =========================================================

def categories_menu():
    keyboard = types.InlineKeyboardMarkup(row_width=2)

    categories = [
        ("📱 التطبيق", "cat_app"),
        ("🆓 النسخة المجانية", "cat_free"),
        ("💎 Premium", "cat_premium"),
        ("📚 القصص", "cat_stories"),
        ("🎧 الاستماع", "cat_listening"),
        ("🗣 النطق", "cat_pronunciation"),
        ("📈 المستويات", "cat_levels"),
        ("🔥 Streak", "cat_streak"),
        ("💳 الدفع والاشتراك", "cat_payment"),
        ("👤 الحساب", "cat_account"),
        ("🧠 التعلم", "cat_learning"),
        ("❓ أخرى", "cat_other"),
    ]

    for name, callback in categories:
        keyboard.add(
            types.InlineKeyboardButton(
                name,
                callback_data=callback
            )
        )

    keyboard.add(
        types.InlineKeyboardButton(
            "🔙 رجوع",
            callback_data="back_main"
        )
    )

    return keyboard