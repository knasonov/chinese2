import argparse
import json
from search_words import load_words, segment_text


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate token list for a story")
    parser.add_argument("path", nargs="?", default="stories/story3.txt", help="Story file")
    parser.add_argument("-o", "--out", default="tokens.json", help="Output JSON file")
    parser.add_argument("-d", "--db", default="chinese_words.db", help="Path to words database")
    args = parser.parse_args()

    words = load_words(args.db)
    with open(args.path, "r", encoding="utf-8") as f:
        text = f.read()
    tokens = segment_text(text, words)

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(tokens, f, ensure_ascii=False, indent=2)
    print(f"Wrote {len(tokens)} tokens to {args.out}")


if __name__ == "__main__":
    main()
