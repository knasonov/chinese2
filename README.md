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
`generate_page.py`. It analyzes all `story*.txt` files and writes `stats.html`
with the statistics embedded directly in the page:

```bash
python generate_page.py
```

Open `stats.html` in a browser after running the command.
