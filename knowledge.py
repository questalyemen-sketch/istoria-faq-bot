import re
from difflib import SequenceMatcher

from database import get_all_faqs


# =========================================================
# تنظيف وتوحيد النص
# =========================================================

def normalize_text(text):
    """توحيد النص العربي لتسهيل البحث."""

    if not text:
        return ""

    text = text.lower().strip()

    # إزالة التشكيل
    text = re.sub(r"[\u064B-\u065F\u0670]", "", text)

    # توحيد بعض الحروف العربية
    replacements = {
        "أ": "ا",
        "إ": "ا",
        "آ": "ا",
        "ى": "ي",
        "ة": "ه",
        "ؤ": "و",
        "ئ": "ي",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # إزالة الرموز وعلامات الترقيم
    text = re.sub(r"[^\w\s]", " ", text)

    # إزالة المسافات الزائدة
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# =========================================================
# تقسيم السؤال إلى كلمات
# =========================================================

def get_words(text):
    normalized = normalize_text(text)
    return set(normalized.split())


# =========================================================
# حساب التشابه
# =========================================================

def similarity_score(user_text, faq):
    """
    حساب درجة التشابه بين سؤال المستخدم
    والسؤال المخزن في قاعدة المعرفة.
    """

    user_normalized = normalize_text(user_text)
    question_normalized = normalize_text(faq["question"])

    if not user_normalized or not question_normalized:
        return 0.0

    # تطابق مباشر
    if user_normalized == question_normalized:
        return 1.0

    # تشابه النص الكامل
    sequence_score = SequenceMatcher(
        None,
        user_normalized,
        question_normalized
    ).ratio()

    # تشابه الكلمات
    user_words = get_words(user_text)
    question_words = get_words(faq["question"])

    if user_words and question_words:
        common_words = user_words.intersection(question_words)

        word_score = (
            len(common_words)
            / max(len(user_words), len(question_words))
        )
    else:
        word_score = 0.0

    # البحث داخل الكلمات المفتاحية
    keyword_score = 0.0

    keywords = faq["keywords"] or ""

    if keywords:
        keyword_list = [
            normalize_text(keyword)
            for keyword in keywords.split(",")
            if keyword.strip()
        ]

        for keyword in keyword_list:
            if keyword and keyword in user_normalized:
                keyword_score = max(keyword_score, 0.85)

    # الدرجة النهائية
    score = max(
        sequence_score,
        (sequence_score * 0.55) + (word_score * 0.45),
        keyword_score
    )

    return round(score, 4)


# =========================================================
# البحث عن أفضل إجابة
# =========================================================

def search_faq(user_text, threshold=0.45):
    """
    البحث عن أفضل سؤال مطابق.
    """

    faqs = get_all_faqs()

    if not faqs:
        return None

    best_faq = None
    best_score = 0.0

    for faq in faqs:
        score = similarity_score(user_text, faq)

        if score > best_score:
            best_score = score
            best_faq = faq

    if best_faq and best_score >= threshold:
        return {
            "faq": best_faq,
            "score": best_score
        }

    return None


# =========================================================
# البحث عن عدة نتائج
# =========================================================

def search_multiple(user_text, limit=5):
    """
    إرجاع عدة نتائج مرتبة حسب درجة التطابق.
    """

    faqs = get_all_faqs()

    results = []

    for faq in faqs:
        score = similarity_score(user_text, faq)

        results.append({
            "faq": faq,
            "score": score
        })

    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return results[:limit]