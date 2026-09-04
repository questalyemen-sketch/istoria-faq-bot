import os
from dotenv import load_dotenv

load_dotenv()

# =========================================================
# iStoria FAQ Bot - Configuration
# =========================================================

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

# أرقام تيليجرام الخاصة بالمشرفين
# مثال:
# ADMIN_IDS=123456789,987654321
ADMIN_IDS = [
    int(user_id.strip())
    for user_id in os.getenv("ADMIN_IDS", "").split(",")
    if user_id.strip().isdigit()
]

# اسم قاعدة البيانات
DATABASE_NAME = "istoria_faq.db"

# عدد نتائج البحث القصوى
MAX_SEARCH_RESULTS = 5

# الحد الأدنى لدرجة تطابق السؤال
MATCH_THRESHOLD = 0.45


def validate_config():
    """التأكد من وجود الإعدادات الأساسية."""
    if not BOT_TOKEN:
        raise ValueError(
            "BOT_TOKEN غير موجود. أضفه في متغيرات البيئة."
        )

    if not ADMIN_IDS:
        print(
            "⚠️ تحذير: لم يتم تحديد ADMIN_IDS. "
            "لن تعمل وظائف الإدارة."
        )