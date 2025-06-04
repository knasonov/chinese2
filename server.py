from __future__ import annotations

from collections import Counter
import json
import sqlite3
import re
import math
from flask import Flask, jsonify, request, send_from_directory

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


@app.route("/stats_data")
def stats_data():
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT simplified, known_probability, number_in_texts "
            "FROM user_words WHERE number_in_texts > 0 "
            "ORDER BY number_in_texts DESC, simplified"
        ).fetchall()
    data = [
        {"word": w, "probability": p, "interactions": n}
        for w, p, n in rows
    ]
    return jsonify(data)


@app.route("/recalculate", methods=["POST"])
def recalculate_probabilities():
    """Recompute known probabilities from the interaction counts."""
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT simplified, number_in_texts FROM user_words"
        ).fetchall()
        for word, num in rows:
            prob = probability_from_interactions(num)
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


def update_user_progress(known: list[str], unknown: list[str], db_path: str = DB_PATH) -> None:
    counts = Counter(known + unknown)
    known_set = set(known)
    unknown_set = set(unknown)
    with sqlite3.connect(db_path) as conn:
        for word, count in counts.items():
            row = conn.execute(
                "SELECT user_knows_word, known_probability, number_in_texts FROM user_words WHERE simplified = ?",
                (word,),
            ).fetchone()
            if row is None:
                continue
            user_knows, prob, num = row
            num += count
            if word in known_set:
                user_knows = 1
                prob = 1.10
            elif word in unknown_set:
                user_knows = 0
                prob = 0.50
            conn.execute(
                "UPDATE user_words SET user_knows_word = ?, known_probability = ?, number_in_texts = ? WHERE simplified = ?",
                (user_knows, prob, num, word),
            )
        conn.commit()


if __name__ == "__main__":
    app.run(debug=True)
