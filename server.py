from __future__ import annotations

from collections import Counter
import json
import sqlite3
import re
import math
import time
from flask import Flask, jsonify, request, send_from_directory
from algo import WordPredictor


DB_PATH = "chinese_words.db"

app = Flask(__name__, static_url_path="", static_folder=".")


@app.route("/")
def index():
    return send_from_directory(".", "text_selection.html")


@app.route("/tokens.json")
def tokens():
    return send_from_directory(".", "tokens.json")


@app.route("/unknown_words")
def unknown_words():
    with open("tokens.json", "r", encoding="utf-8") as f:
        tokens = json.load(f)
    chinese_re = re.compile(r"[\u4e00-\u9fff]+")
    words = {t for t in tokens if chinese_re.search(t)}
    if not words:
        return jsonify([])
    placeholders = ",".join(["?"] * len(words))
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            f"SELECT simplified, known_probability FROM user_words WHERE simplified IN ({placeholders})",
            list(words),
        ).fetchall()
    unknown = [w for w, p in rows if p <= 0.30]
    if not unknown:
        return jsonify([])

    placeholders = ",".join(["?"] * len(unknown))
    with sqlite3.connect(DB_PATH) as conn:
        details = conn.execute(
            f"SELECT simplified, pinyin, meaning FROM words WHERE simplified IN ({placeholders})",
            unknown,
        ).fetchall()

    result = []
    for word, pinyin, meaning in details:
        first = meaning.split(';')[0].split(',')[0].strip().rstrip('.')
        result.append({"word": word, "pinyin": pinyin, "meaning": first})

    # preserve original order
    result.sort(key=lambda x: unknown.index(x["word"]))
    return jsonify(result)


@app.route("/text_selection.js")
def js_file():
    return send_from_directory(".", "text_selection.js")


@app.route("/stats")
def stats_page():
    return send_from_directory(".", "stats.html")


@app.route("/stats.js")
def stats_js():
    return send_from_directory(".", "stats.js")


@app.route("/flashcard")
def flashcard_page():
    return send_from_directory(".", "flashcard.html")


@app.route("/flashcard.js")
def flashcard_js():
    return send_from_directory(".", "flashcard.js")


@app.route("/next_word")
def next_word():
    """Return the next flashcard word ordered by frequency."""
    offset = int(request.args.get("offset", 0))
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT w.simplified, w.pinyin, w.meaning "
            "FROM words AS w JOIN user_words AS u ON w.simplified = u.simplified "
            "WHERE u.known_probability < 0.7 "
            "ORDER BY w.frequency LIMIT 1 OFFSET ?",
            (offset,),
        ).fetchone()
    if not row:
        return jsonify({})
    return jsonify({"word": row[0], "pinyin": row[1], "meaning": row[2]})


@app.route("/record_flashcard", methods=["POST"])
def record_flashcard():
    """Record the user's flashcard response."""
    data = request.get_json(force=True)
    word = data.get("word")
    known = data.get("known")
    if not word:
        return jsonify({"status": "error", "msg": "missing word"})
    flag = 1 if known else 0
    with sqlite3.connect(DB_PATH) as conn:
        record_interaction(conn, word, "flashcard", flag)
        conn.commit()
    return jsonify({"status": "ok"})


@app.route("/stats_data")
def stats_data():
    """Return basic statistics derived from interaction logs."""
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT w.simplified, u.known_probability, COUNT(*) "
            "FROM word_interactions AS w "
            "JOIN user_words AS u ON w.simplified = u.simplified "
            "GROUP BY w.simplified ORDER BY COUNT(*) DESC, w.simplified"
        ).fetchall()
    data = [
        {
            "word": word,
            "probability": prob,
            "interactions": count,
        }
        for word, prob, count in rows
    ]
    return jsonify(data)


@app.route("/recalculate", methods=["POST"])
def recalculate_probabilities():
    """Recompute known probabilities using the WordPredictor algorithm."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT simplified, interaction, known, timestamp "
            "FROM word_interactions ORDER BY simplified, timestamp"
        ).fetchall()

        events: dict[str, list[sqlite3.Row]] = {}
        for row in rows:
            events.setdefault(row["simplified"], []).append(row)

        now = time.time()
        for word, evs in events.items():
            wp = WordPredictor()
            for ev in evs:
                mode = ev["interaction"].split("_")[0]
                outcome = int(ev["known"] or 0)
                wp.update(mode, outcome, ev["timestamp"])
            prob = float(wp.probability(now))
            conn.execute(
                "UPDATE user_words SET known_probability = ? WHERE simplified = ?",
                (prob, word),
            )
        conn.commit()
    return jsonify({"status": "ok"})


@app.route("/update_words", methods=["POST"])
def update_words():
    data = request.get_json(force=True)
    known = data.get("known", [])
    unknown = data.get("unknown", [])
    update_user_progress(known, unknown, DB_PATH)
    return jsonify({"status": "ok"})


# ---- Database viewer endpoints ----

@app.route("/database")
def database_page():
    return send_from_directory(".", "database.html")


@app.route("/database.js")
def database_js():
    return send_from_directory(".", "database.js")


@app.route("/db_schema")
def db_schema():
    """Return list of tables and their columns."""
    schema = {}
    with sqlite3.connect(DB_PATH) as conn:
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
        for (name,) in tables:
            cols = conn.execute(f"PRAGMA table_info({name})").fetchall()
            schema[name] = [{"name": c[1], "type": c[2]} for c in cols]
    return jsonify(schema)


@app.route("/table/<name>")
def table_data(name: str):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute(f"SELECT * FROM {name}").fetchall()
        except sqlite3.Error:
            return jsonify([])
        data = [dict(row) for row in rows]
    return jsonify(data)


def probability_from_interactions(count: int) -> float:
    """Return a knowledge probability based on how often the word was seen.

    Uses a logistic curve that starts around 1% when the user first
    encounters a word, reaches 50% after roughly 15 interactions and
    slowly approaches 1. Probabilities above 95% are capped to avoid
    absolute certainty.
    """
    k = 0.3
    x0 = 15
    l0 = 1 / (1 + math.exp(-k * (0 - x0)))
    scale = (0.5 - 0.01) / (0.5 - l0)
    base = 0.01 - scale * l0
    p = base + scale / (1 + math.exp(-k * (count - x0)))
    if p > 0.95:
        return 0.95
    if p < 0:
        return 0.0
    return p


def record_interaction(conn: sqlite3.Connection, word: str, interaction: str, known: int | None) -> None:
    """Insert a single interaction entry into the database."""
    ts = int(time.time())
    conn.execute(
        "INSERT INTO word_interactions(simplified, interaction, known, timestamp) VALUES (?,?,?,?)",
        (word, interaction, known, ts),
    )


def update_user_progress(known: list[str], unknown: list[str], db_path: str = DB_PATH) -> None:
    """Record reading interactions without modifying user progress directly."""
    counts = Counter(known + unknown)
    known_set = set(known)
    unknown_set = set(unknown)
    with sqlite3.connect(db_path) as conn:
        for word, count in counts.items():
            # ensure the word exists in the vocabulary list
            exists = conn.execute(
                "SELECT 1 FROM user_words WHERE simplified = ?",
                (word,),
            ).fetchone()
            if not exists:
                continue
            interaction = "read_known" if word in known_set else "read_unknown"
            flag = 1 if word in known_set else 0
            for _ in range(count):
                record_interaction(conn, word, interaction, flag)
        conn.commit()


if __name__ == "__main__":
    app.run(debug=True)
