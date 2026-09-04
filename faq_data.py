import json
import os

from database import add_faq, count_faqs


# =========================================================
# مسار قاعدة المعرفة
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FAQ_FILE = os.path.join(BASE_DIR, "data", "istoria_faq.json")


# =========================================================
# قراءة ملف الأسئلة
# =========================================================

def load_faq_file():
    """قراءة الأسئلة من ملف JSON."""

    if not os.path.exists(FAQ_FILE):
        print(f"⚠️ ملف قاعدة المعرفة غير موجود: {FAQ_FILE}")
        return []

    try:
        with open(FAQ_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        # الشكل المتوقع:
        # {
        #   "faqs": [...]
        # }

        if isinstance(data, dict):
            return data.get("faqs", [])

        if isinstance(data, list):
            return data

        print("⚠️ صيغة ملف JSON غير صحيحة.")
        return []

    except json.JSONDecodeError as error:
        print(f"❌ خطأ في قراءة JSON: {error}")
        return []

    except Exception as error:
        print(f"❌ خطأ غير متوقع: {error}")
        return []


# =========================================================
# استيراد قاعدة المعرفة
# =========================================================

def seed_database():
    """
    إضافة الأسئلة الموجودة في JSON
    إلى قاعدة البيانات إذا كانت فارغة.
    """

    current_count = count_faqs()

    if current_count > 0:
        print(
            f"ℹ️ قاعدة البيانات تحتوي بالفعل على "
            f"{current_count} سؤال."
        )
        return 0

    faqs = load_faq_file()

    if not faqs:
        print("⚠️ لا توجد أسئلة لإضافتها.")
        return 0

    added = 0

    for item in faqs:
        question = str(item.get("question", "")).strip()
        answer = str(item.get("answer", "")).strip()
        keywords = str(item.get("keywords", "")).strip()
        category = str(item.get("category", "عام")).strip()

        # تجاهل البيانات الناقصة
        if not question or not answer:
            continue

        try:
            add_faq(
                question=question,
                answer=answer,
                keywords=keywords,
                category=category
            )

            added += 1

        except Exception as error:
            print(
                f"⚠️ تعذر إضافة السؤال: {question}"
            )
            print(error)

    print(
        f"✅ تمت إضافة {added} سؤال إلى قاعدة البيانات."
    )

    return added