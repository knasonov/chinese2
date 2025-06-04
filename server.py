from __future__ import annotations

from collections import Counter
import json
import sqlite3
from flask import Flask, jsonify, request, send_from_directory

DB_PATH = "chinese_words.db"

app = Flask(__name__, static_url_path="", static_folder=".")


@app.route("/")
def index():
    return send_from_directory(".", "text_selection.html")


@app.route("/tokens.json")
def tokens():
    return send_from_directory(".", "tokens.json")


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


@app.route("/update_words", methods=["POST"])
def update_words():
    data = request.get_json(force=True)
    known = data.get("known", [])
    unknown = data.get("unknown", [])
    update_user_progress(known, unknown, DB_PATH)
    return jsonify({"status": "ok"})


def probability_from_interactions(count: int) -> float:
    """Return a knowledge probability based on how often the word was seen.

    One encounter corresponds to ~1%% probability, 15 encounters to about 50%%
    and 100 encounters reach roughly 95%%. Values in between are interpolated
    linearly. Anything above 100 interactions is clamped at 95%%.
    """
    if count <= 1:
        return 0.01
    if count <= 15:
        return 0.01 + (count - 1) * (0.5 - 0.01) / 14
    if count >= 100:
        return 0.95
    return 0.5 + (count - 15) * (0.95 - 0.5) / 85


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
            user_knows, _, num = row
            num += count
            prob = probability_from_interactions(num)
            if word in known_set:
                user_knows = 1
            elif word in unknown_set:
                user_knows = 0
            conn.execute(
                "UPDATE user_words SET user_knows_word = ?, known_probability = ?, number_in_texts = ? WHERE simplified = ?",
                (user_knows, prob, num, word),
            )
        conn.commit()


if __name__ == "__main__":
    app.run(debug=True)
