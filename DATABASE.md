# Chinese Words SQLite Database

This repository now includes a script to convert the Excel word list
`bopomofo_translated.xlsx` into a structured SQLite database. The goal is to
make it easy to query vocabulary data and track personal learning progress.

## Schema

The resulting database contains three tables:

### `words`
- `simplified` – the simplified Chinese form of the word
- `frequency` – how often the word occurs in the source material
- `pinyin` – standard pinyin pronunciation
- `meaning` – English meaning or gloss
- `bopomofo` – phonetic transcription in bopomofo

All rows come directly from the Excel spreadsheet.

### `user_words`
- `simplified` – references a word in the `words` table (primary key)
- `user_knows_word` – `0` or `1` indicating if the user claims to know the word
- `known_probability` – floating value representing confidence (0–1 range)
- `number_in_texts` – how many times the word appears in the reading texts

Each word from the `words` table is automatically inserted into this table with
default values so that learning progress can be tracked immediately.

### `word_interactions`
- `id` – auto-incrementing unique row identifier
- `simplified` – references a word in the `words` table
- `interaction` – short string describing the type of interaction
- `known` – `0` or `1` if the user indicated knowledge (may be `NULL`)
- `timestamp` – Unix epoch time (seconds)

Every encounter with a word is recorded in this table. It allows analysing the
time between reviews and supports future interaction types beyond reading.

## Usage

Run the converter with Python (requires `pandas` and `sqlite3` which ships with
Python):

```bash
python import_words.py
```

By default it reads `bopomofo_translated.xlsx` and writes
`chinese_words.db`. You can supply custom paths:

```bash
python import_words.py path/to/file.xlsx --db my.db
```

## Possible Extensions

- Add extra columns to `user_words` such as the date a word was first seen or
  last reviewed.
- Store multiple users' progress by introducing a separate `users` table and
  referencing it from `user_words` with a `user_id` column.
- Include links to example sentences or audio pronunciations in the `words`
  table for richer study material.
