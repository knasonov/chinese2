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


@app.route("/update_words", methods=["POST"])
def update_words():
    data = request.get_json(force=True)
    known = data.get("known", [])
    unknown = data.get("unknown", [])
    update_user_progress(known, unknown, DB_PATH)
    return jsonify({"status": "ok"})


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
            if prob < 0.01:
                prob = 0.01
            if word in known_set:
                user_knows = 1
                prob *= 1.2
            elif word in unknown_set:
                user_knows = 0
                prob *= 0.5
            if prob < 0.01:
                prob = 0.01
            if prob > 1:
                prob = 1
            conn.execute(
                "UPDATE user_words SET user_knows_word = ?, known_probability = ?, number_in_texts = ? WHERE simplified = ?",
                (user_knows, prob, num, word),
            )
        conn.commit()


if __name__ == "__main__":
    app.run(debug=True)
