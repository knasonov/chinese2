"""Create an SQLite database from the bopomofo Excel data."""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

import pandas as pd


DEFAULT_DB_PATH = "chinese_words.db"


def import_excel(excel_path: str, db_path: str = DEFAULT_DB_PATH) -> None:
    """Read the Excel file and store its contents in an SQLite database.

    Parameters
    ----------
    excel_path:
        Path to ``bopomofo_translated.xlsx``.
    db_path:
        Location of the SQLite database to create or update.
    """
    df = pd.read_excel(excel_path)
    with sqlite3.connect(db_path) as conn:
        # main table with vocabulary
        df.to_sql("words", conn, index=False, if_exists="replace")
        # secondary table tracking a user's knowledge of each word
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_words (
                simplified TEXT PRIMARY KEY,
                user_knows_word INTEGER DEFAULT 0,
                known_probability REAL DEFAULT 0.0,
                number_in_texts INTEGER DEFAULT 0,
                FOREIGN KEY(simplified) REFERENCES words(simplified)
            )
            """
        )
        # prepopulate user_words with the word list if not already present
        existing = {
            row[0]
            for row in conn.execute(
                "SELECT simplified FROM user_words"
            )
        }
        to_insert = [(w,) for w in df["simplified"] if w not in existing]
        if to_insert:
            conn.executemany(
                "INSERT INTO user_words(simplified) VALUES (?)", to_insert
            )


def main() -> None:
    parser = argparse.ArgumentParser(description="Import words into an SQLite database")
    parser.add_argument(
        "excel", nargs="?", default="bopomofo_translated.xlsx",
        help="Path to the source Excel file"
    )
    parser.add_argument(
        "--db", default=DEFAULT_DB_PATH, help="Output SQLite database path"
    )
    args = parser.parse_args()
    import_excel(args.excel, args.db)
    print(f"Database written to {args.db}")


if __name__ == "__main__":
    main()
