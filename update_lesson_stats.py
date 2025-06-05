import sqlite3
import re
from pathlib import Path
from collections import Counter

from search_words import load_words, segment_text

DB_PATH = "chinese_words.db"
LESSON_DIR = "lessons"
USER = "Kosmos1"


def count_lesson_words(lesson_dir: str, db_path: str) -> Counter:
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


def update_database(word_counts: Counter, db_path: str) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute("UPDATE user_words SET number_in_texts = 0")
        for word, count in word_counts.items():
            conn.execute(
                "UPDATE user_words SET number_in_texts = ? WHERE simplified = ?",
                (count, word),
            )
        conn.commit()


def fetch_statistics(db_path: str) -> list[tuple[str, int]]:
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            "SELECT simplified, number_in_texts FROM user_words "
            "WHERE number_in_texts > 0 ORDER BY number_in_texts DESC"
        ).fetchall()
    return rows


def main() -> None:
    #counts = count_lesson_words(LESSON_DIR, DB_PATH)
    #update_database(counts, DB_PATH)
    stats = fetch_statistics(DB_PATH)
    total = sum(count for _, count in stats)
    print(f"Word encounter statistics for {USER}:")
    for word, count in stats[:500]:
        print(f"{word}: {count}")
    print(f"Total word occurrences: {total}")


if __name__ == "__main__":
    main()
