"""Generate a static HTML page with character statistics."""

from analyze_characters import analyze_stories

STYLE = """
body {
    font-family: Arial, sans-serif;
    background: #f8f9fa;
    color: #333;
    margin: 0;
    padding: 20px;
}

.container {
    max-width: 800px;
    margin: auto;
    background: #fff;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

h1 {
    text-align: center;
}

#stats {
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
}

#stats th, #stats td {
    padding: 8px 12px;
    border-bottom: 1px solid #ddd;
    text-align: center;
}

#stats th {
    background: #007bff;
    color: #fff;
}
"""

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>Character Statistics</title>
    <style>{style}</style>
</head>
<body>
    <div class=\"container\">
        <h1>Character Statistics</h1>
        <p>Total characters: {total}</p>
        <p>Unique characters: {unique}</p>
        <table id=\"stats\">
            <thead>
                <tr><th>Character</th><th>Count</th><th>Frequency</th></tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    </div>
</body>
</html>
"""


def generate_html(total: int, counts: list[tuple[str, int]]) -> str:
    """Return HTML for the given statistics."""
    rows = []
    for ch, count in counts:
        freq = count / total * 100
        rows.append(
            f"<tr><td>{ch}</td><td>{count}</td><td>{freq:.2f}%</td></tr>"
        )
    return HTML_TEMPLATE.format(
        style=STYLE,
        total=total,
        unique=len(counts),
        rows="\n".join(rows),
    )


def main() -> None:
    total, counts = analyze_stories("story*.txt")
    html = generate_html(total, counts)
    with open("stats.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Wrote stats.html")


if __name__ == "__main__":
    main()
