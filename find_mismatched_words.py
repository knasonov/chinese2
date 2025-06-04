import sqlite3
import csv
from typing import List, Tuple


def find_mismatched_words(
    db_path: str = "chinese_words.db",
    frequency_path: str = "frequency_list.tsv",
    *,
    min_freq: int = 300,
    limit: int = 50,
) -> List[Tuple[str, int, int]]:
    """Return words frequent in general texts but rare for the user.

    Parameters
    ----------
    db_path:
        Path to the SQLite database containing ``user_words`` table.
    frequency_path:
        TSV file with general frequency information. The file is expected to
        have the word as the second column and its count as the third column.
    min_freq:
        Ignore entries from ``frequency_path`` whose frequency is below this
        value.
    limit:
        Number of results to return.
    """
    # Load general frequency list
    general: list[tuple[str, int]] = []
    with open(frequency_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            if len(row) < 3:
                continue
            try:
                freq = int(row[2])
            except ValueError:
                continue
            if freq < min_freq:
                continue
            word = row[1]
            general.append((word, freq))

    # Load user encounter counts
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            "SELECT simplified, number_in_texts FROM user_words"
        ).fetchall()
    user_counts = {w: c for w, c in rows}

    discrepancies: list[tuple[str, int, int, float]] = []
    for word, freq in general:
        count = user_counts.get(word, 0)
        score = freq / (count + 1)
        discrepancies.append((word, freq, count, score))

    discrepancies.sort(key=lambda x: x[3], reverse=True)
    top = [d[:3] for d in discrepancies[:limit]]
    return top


def print_mismatched_words() -> None:
    """Print 50 high-frequency words missing from the user's texts."""
    results = find_mismatched_words()
    for word, gen_freq, user_count in results:
        print(f"{word}\tGeneral: {gen_freq}\tUser: {user_count}")


if __name__ == "__main__":
    print_mismatched_words()
