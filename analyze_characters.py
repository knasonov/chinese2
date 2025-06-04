import glob
from collections import Counter
import argparse


def analyze_stories(pattern: str) -> tuple[int, list[tuple[str, int]]]:
    files = sorted(glob.glob(pattern))
    counter = Counter()
    for path in files:
        with open(path, 'r', encoding='utf-8') as f:
            for ch in f.read():
                if not ch.isspace():
                    counter[ch] += 1
    total = sum(counter.values())
    return total, counter.most_common()


def print_stats(total: int, sorted_counts: list[tuple[str, int]], top: int) -> None:
    print(f"Total characters counted: {total}")
    print(f"Unique characters: {len(sorted_counts)}\n")
    print("Top characters:")
    header = f"{'Character':^10} {'Count':>10} {'Frequency':>10}"
    print(header)
    print('-' * len(header))
    for ch, count in sorted_counts[:top]:
        freq = count / total * 100
        print(f"{ch:^10} {count:>10} {freq:>9.2f}%")


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze story character frequencies")
    parser.add_argument('-p', '--pattern', default='story*.txt',
                        help='Glob pattern for story files')
    parser.add_argument('-t', '--top', type=int, default=10,
                        help='Number of top characters to display')
    args = parser.parse_args()

    total, counts = analyze_stories(args.pattern)
    print_stats(total, counts, args.top)


if __name__ == '__main__':
    main()
