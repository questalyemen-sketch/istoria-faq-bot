import sqlite3
from datetime import datetime, timezone

from config import DATABASE_NAME


def get_connection():
    """إنشاء اتصال بقاعدة البيانات."""
    conn = sqlite3.connect(DATABASE_NAME, timeout=30)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """إنشاء الجداول الأساسية إذا لم تكن موجودة."""
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS faqs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            keywords TEXT DEFAULT '',
            category TEXT DEFAULT 'عام',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_faq_category
        ON faqs(category)
    """)

    conn.commit()
    conn.close()


def add_faq(question, answer, keywords="", category="عام"):
    """إضافة سؤال جديد."""
    now = datetime.now(timezone.utc).isoformat()

    conn = get_connection()

    cursor = conn.execute("""
        INSERT INTO faqs
        (question, answer, keywords, category, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        question.strip(),
        answer.strip(),
        keywords.strip(),
        category.strip() or "عام",
        now,
        now
    ))

    faq_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return faq_id


def get_faq(faq_id):
    """الحصول على سؤال بواسطة ID."""
    conn = get_connection()

    faq = conn.execute("""
        SELECT *
        FROM faqs
        WHERE id = ?
    """, (faq_id,)).fetchone()

    conn.close()

    return faq


def get_all_faqs():
    """الحصول على جميع الأسئلة."""
    conn = get_connection()

    faqs = conn.execute("""
        SELECT *
        FROM faqs
        ORDER BY id ASC
    """).fetchall()

    conn.close()

    return faqs


def delete_faq(faq_id):
    """حذف سؤال."""
    conn = get_connection()

    cursor = conn.execute("""
        DELETE FROM faqs
        WHERE id = ?
    """, (faq_id,))

    deleted = cursor.rowcount > 0

    conn.commit()
    conn.close()

    return deleted


def update_faq(
    faq_id,
    question=None,
    answer=None,
    keywords=None,
    category=None
):
    """تعديل بيانات سؤال موجود."""

    faq = get_faq(faq_id)

    if not faq:
        return False

    new_question = (
        question.strip()
        if question is not None
        else faq["question"]
    )

    new_answer = (
        answer.strip()
        if answer is not None
        else faq["answer"]
    )

    new_keywords = (
        keywords.strip()
        if keywords is not None
        else faq["keywords"]
    )

    new_category = (
        category.strip()
        if category is not None
        else faq["category"]
    )

    now = datetime.now(timezone.utc).isoformat()

    conn = get_connection()

    conn.execute("""
        UPDATE faqs
        SET
            question = ?,
            answer = ?,
            keywords = ?,
            category = ?,
            updated_at = ?
        WHERE id = ?
    """, (
        new_question,
        new_answer,
        new_keywords,
        new_category,
        now,
        faq_id
    ))

    conn.commit()
    conn.close()

    return True


def count_faqs():
    """عدد الأسئلة الموجودة."""
    conn = get_connection()

    result = conn.execute("""
        SELECT COUNT(*) AS total
        FROM faqs
    """).fetchone()

    conn.close()

    return result["total"]