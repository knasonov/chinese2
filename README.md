# chinese2
The repository for testing Codex on my Chinese project


## Vocabulary database

`import_words.py` converts the Excel word list into an SQLite database. Run it
with Python (requires `pandas`):

```bash
python import_words.py
```

This creates `chinese_words.db` containing two tables: `words` with the
vocabulary data and `user_words` for tracking individual progress. See
`DATABASE.md` for a complete description of the schema.

## Function Reference

See [FUNCTION_REFERENCE.md](FUNCTION_REFERENCE.md) for a description of all Python functions provided by this repository.

## Word selection demo

Generate a list of tokens from one of the sample stories and open the demo page:

```bash
python generate_tokens.py stories/story1.txt
```

This writes `tokens.json` which is loaded by `text_selection.html`.
Run `python server.py` and open `http://localhost:5000` to mark unknown
words in the browser. Click words to highlight them and press
**Show Results** to store the results in the database.
