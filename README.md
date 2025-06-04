# chinese2
The repository for testing Codex on my Chinese project

## Character statistics front-end

Run the analyzer with the `--json` option to produce `stats.json` which is
consumed by the web UI:

```bash
python analyze_characters.py --json stats.json
```

Then open `index.html` in a browser. The page will display the total and unique
character counts as well as a table listing every character with its count and
frequency.

## Generating a static page with Python

If you prefer a single self-contained HTML file you can run
`generate_page.py`. It analyzes all `stories/story*.txt` files and writes `stats.html`
with the statistics embedded directly in the page:

```bash
python generate_page.py
```

Open `stats.html` in a browser after running the command.

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

This writes `tokens.json` which is loaded by `text_selection.html`. Open the page in a browser to mark unknown words. Click words to highlight them and press **Show Results** to print the known and unknown lists.
