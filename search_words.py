import sqlite3
from typing import List, Iterable
import re

DB_PATH = 'chinese_words.db'


def load_words(db_path: str = DB_PATH) -> List[str]:
    """Load all simplified words from the database."""
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute('SELECT simplified FROM words').fetchall()
    return [r[0] for r in rows]


def segment_text(text: str, words: Iterable[str]) -> List[str]:
    """Segment *text* using known Chinese words.

    Non-Chinese characters are returned as-is. Chinese word matching
    prefers longer words first (up to four characters).
    """
    by_len: dict[int, set[str]] = {}
    for w in words:
        by_len.setdefault(len(w), set()).add(w)
    # Only consider word lengths up to 4 for efficiency
    lengths = sorted([l for l in by_len.keys() if l <= 4], reverse=True)

    i = 0
    result: List[str] = []
    chinese_re = re.compile(r"[\u4e00-\u9fff]+")
    while i < len(text):
        ch = text[i]
        if not chinese_re.match(ch):
            result.append(ch)
            i += 1
            continue

        matched = False
        for l in lengths:
            if i + l <= len(text):
                piece = text[i:i + l]
                if piece in by_len.get(l, set()):
                    result.append(piece)
                    i += l
                    matched = True
                    break
        if not matched:
            # consume single Chinese character if no word matched
            result.append(ch)
            i += 1
    return result


if __name__ == '__main__':
    import sys
    words = load_words()
    if len(sys.argv) < 2:
        print('Usage: python search_words.py <path>')
        sys.exit(1)
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        text = f.read()
    segments = segment_text(text, words)
    # Only print tokens that contain Chinese characters
    chinese_re = re.compile(r"[\u4e00-\u9fff]+")
    for w in segments:
        if chinese_re.search(w):
            print(w)
