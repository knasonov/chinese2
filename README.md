# chinese2
The repository for testing Codex on my Chinese project


## Vocabulary database

`initial.py` sets up the SQLite database and preloads it with the lesson
statistics. Run it with Python (requires `pandas`):

```bash
python initial.py
```

This creates `chinese_words.db` containing three tables: `words` with the
vocabulary data, `user_words` for tracking individual progress and
`word_interactions` which logs every encounter with a word. See
`DATABASE.md` for a complete description of the schema.

## Function Reference

See [FUNCTION_REFERENCE.md](FUNCTION_REFERENCE.md) for a description of all Python functions provided by this repository.

## Word selection demo

Generate a list of tokens from one of the sample stories and open the demo page:

```bash
python generate_tokens.py stories/story1.txt
```

This writes `tokens.json` which is loaded by `text.html`.
Run `python server.py` and open `http://localhost:5000/text` to mark unknown
words in the browser. Click words to highlight them and press
**Show Results** to record your interaction with each word. The
`user_words` table is no longer modified directly; instead every
interaction is stored in `word_interactions` with a timestamp.

## Viewing learning statistics

While the server is running, open `http://localhost:5000/stats` to see a table
of all words that have been encountered. The page lists each word together with
its current probability of being known and how many times it occurred in the
texts. A **Recalculate based on the number of interactions** button lets you
recompute all probabilities from the stored interaction counts.

## Inspecting the database

While the server is running, open `http://localhost:5000/database` to see the
structure of each table and browse their contents.
