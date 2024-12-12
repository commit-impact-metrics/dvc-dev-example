import argparse
import os
from cim.branches import compare_branches
from cim.commits import analyze_two_commits_with_cache


def main():
    parser = argparse.ArgumentParser(description="Сравнение веток и коммитов.")
    parser.add_argument("source", nargs="?", help="Исходная ветка или коммит.")
    parser.add_argument("base", help="Базовая ветка или коммит.")
    parser.add_argument("--commits", action="store_true", help="Сравнить два коммита.")
    parser.add_argument(
        "--output", default="output", help="Папка для сохранения результатов."
    )
    args = parser.parse_args()

    repo_path = os.getcwd()

    if args.commits:
        if not args.source or not args.base:
            parser.error("Для сравнения коммитов необходимо указать оба хэша коммитов.")
        analyze_two_commits_with_cache(repo_path, args.base, args.source, args.output)
    else:
        if not args.source:
            args.source = "HEAD"
        compare_branches(repo_path, args.source, args.base, args.output)


if __name__ == "__main__":
    main()
