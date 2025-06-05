from __future__ import annotations

import sqlite3
import re
from collections import Counter
from pathlib import Path

from import_words import import_excel
from search_words import load_words, segment_text
from server import update_user_progress

DEFAULT_DB_PATH = "chinese_words.db"
EXCEL_PATH = "bopomofo_translated.xlsx"
LESSON_DIR = "lessons"


def setup_database(excel_path: str = EXCEL_PATH, db_path: str = DEFAULT_DB_PATH) -> None:
    """Create the SQLite database from the vocabulary spreadsheet."""
    import_excel(excel_path, db_path)


def count_lesson_words(
    lesson_dir: str = LESSON_DIR, db_path: str = DEFAULT_DB_PATH
) -> Counter[str]:
    """Return word occurrence counts for all lesson texts."""
    words = load_words(db_path)
    chinese_re = re.compile(r"[\u4e00-\u9fff]+")
    counter: Counter[str] = Counter()
    for path in Path(lesson_dir).glob("Lesson*.txt"):
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        segments = segment_text(text, words)
        for seg in segments:
            if chinese_re.search(seg):
                counter[seg] += 1
    return counter


def update_lesson_statistics(
    db_path: str = DEFAULT_DB_PATH, lesson_dir: str = LESSON_DIR
) -> None:
    """Store lesson word counts in the ``user_words`` table."""
    counts = count_lesson_words(lesson_dir, db_path)
    with sqlite3.connect(db_path) as conn:
        conn.execute("UPDATE user_words SET number_in_texts = 0")
        for word, count in counts.items():
            conn.execute(
                "UPDATE user_words SET number_in_texts = ? WHERE simplified = ?",
                (count, word),
            )
        conn.commit()


def upload_lesson_interactions(
    db_path: str = DEFAULT_DB_PATH, lesson_dir: str = LESSON_DIR
) -> None:
    """Record reading interactions for all words found in the lessons."""
    words = load_words(db_path)
    chinese_re = re.compile(r"[\u4e00-\u9fff]+")
    known: list[str] = []
    for path in Path(lesson_dir).glob("Lesson*.txt"):
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        segments = segment_text(text, words)
        for seg in segments:
            if chinese_re.search(seg):
                known.append(seg)
    update_user_progress(known, [], db_path)


def main() -> None:
    setup_database()
    update_lesson_statistics()
    upload_lesson_interactions()


if __name__ == "__main__":
    main()
