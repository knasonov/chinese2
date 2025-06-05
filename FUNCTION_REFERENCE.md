# Function Reference

This document lists the public Python functions in this repository and briefly explains what each of them does.

## analyze_characters.py

- `analyze_stories(pattern: str) -> tuple[int, list[tuple[str, int]]]`
  
  Scans all files matching a glob pattern and counts every non-whitespace Chinese character. Returns the total number of characters and a list of `(character, count)` tuples sorted by frequency.

- `print_stats(total: int, sorted_counts: list[tuple[str, int]], top: int) -> None`
  
  Prints an overview of the character statistics to the console including the total, the number of unique characters and a table of the `top` most frequent characters.

- `write_json(total: int, sorted_counts: list[tuple[str, int]], path: str) -> None`
  
  Writes the complete statistics to a JSON file. Each entry contains the character, its count and its percentage frequency.

- `main() -> None`
  
  Command line entry point. Parses arguments, runs `analyze_stories` and outputs the statistics. Optionally writes them to JSON when the `--json` option is provided.


## import_words.py

- `import_excel(excel_path: str, db_path: str = DEFAULT_DB_PATH) -> None`
  
  Reads the vocabulary spreadsheet and stores its contents in an SQLite database. The `words` table holds the actual vocabulary while `user_words` tracks a user's progress.

- `main() -> None`
  
  Command line entry point for the importer. Takes an optional path to the Excel file and database location, then calls `import_excel`.

## search_words.py

- `load_words(db_path: str = DB_PATH) -> List[str]`
  
  Loads the simplified Chinese words from the `words` table in the SQLite database and returns them as a list.

- `segment_text(text: str, words: Iterable[str]) -> List[str]`
  
  Splits a text into tokens using the supplied word list. The function matches longer words first (up to four characters) and falls back to individual characters when no word matches. Non‑Chinese characters are returned unchanged.

## update_lesson_stats.py

- `count_lesson_words(lesson_dir: str, db_path: str) -> Counter`
  
  Tokenises every `Lesson*.txt` file using `segment_text` and counts how often each known word occurs.

- `update_database(word_counts: Counter, db_path: str) -> None`
  
  Resets the `number_in_texts` column in `user_words` and updates it with the counts produced by `count_lesson_words`.

- `fetch_statistics(db_path: str) -> list[tuple[str, int]]`
  
  Retrieves the words that have a non-zero `number_in_texts` value ordered by frequency.

- `main() -> None`
  
  Runs the full workflow: counting lesson words, updating the database and printing a summary of the top results.

## find_mismatched_words.py

- `find_mismatched_words(db_path: str = "chinese_words.db", frequency_path: str = "frequency_list.tsv", *, min_freq: int = 300, limit: int = 50) -> List[Tuple[str, int, int]]`
  
  Compares a general Chinese word frequency list with the user's encounter counts. Returns words that appear frequently in general texts but not in the user's own material.

- `print_mismatched_words() -> None`
  
  Convenience wrapper that prints the top discrepancies from `find_mismatched_words`.



## generate_tokens.py

- `main() -> None`

  Segments a story with `segment_text` and writes the tokens to a JSON
  file. The output is consumed by `text_selection.html` for marking
  known and unknown words.

## server.py

- `update_user_progress(known: list[str], unknown: list[str], db_path: str = "chinese_words.db") -> None`

  Updates the `user_words` table and records every interaction in the
  `word_interactions` table. Encounter counts are increased but probabilities
  are not recomputed automatically. Instead `known_probability` is set to `1.10`
  for words marked as known and `0.50` for words marked as unknown. The
  `user_knows_word` column is updated accordingly.

- `probability_from_interactions(count: int) -> float`

  Convert the number of times a word has been encountered into a probability of
  being known. One encounter yields 1% probability, 15 encounters about 50% and
  100 encounters about 95%.

- `record_interaction(conn: sqlite3.Connection, word: str, interaction: str, known: int | None) -> None`

  Inserts a single row into `word_interactions` with the current timestamp.

- `app`

  Flask application serving the selection page and providing the
  `/update_words` endpoint to receive the user's choices. It also exposes a
  `/recalculate` endpoint to recompute all probabilities from the stored
  interaction counts.

## initial.py

- `setup_database(excel_path: str = "bopomofo_translated.xlsx", db_path: str = "chinese_words.db") -> None`

  Create the SQLite database from the Excel word list.

- `count_lesson_words(lesson_dir: str = "lessons", db_path: str = "chinese_words.db") -> Counter`

  Return a `Counter` with the number of times each word occurs across all lesson texts.

- `update_lesson_statistics(db_path: str = "chinese_words.db", lesson_dir: str = "lessons") -> None`

  Store the lesson word counts in the `user_words` table.

- `upload_lesson_interactions(db_path: str = "chinese_words.db", lesson_dir: str = "lessons") -> None`

  Record interactions for every word in the lesson texts as if the user had read them.

- `main() -> None`

  Execute the full initialisation workflow: create the database, populate statistics and log lesson interactions.
