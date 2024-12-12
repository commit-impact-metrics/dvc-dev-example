import shutil
import subprocess

from cim.commits import analyze_two_commits_with_cache
from cim.utils import clone_and_prepare_repo


def compare_branches(repo_path, branch1, branch2, output_dir):
    """
    Сравнивает HEAD коммиты двух веток и записывает результаты в output_dir.

    :param repo_path: Путь к репозиторию.
    :param branch1: Первая ветка.
    :param branch2: Вторая ветка.
    :param output_dir: Папка для сохранения результатов.
    """
    temp_repo = clone_and_prepare_repo(repo_path)
    try:
        # Получаем последний коммит для каждой ветки
        subprocess.run(
            ["git", "checkout", branch1],
            cwd=temp_repo,
            check=True,
        )
        head_commit_branch1 = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=temp_repo,
            capture_output=True,
            text=True,
        ).stdout.strip()

        subprocess.run(
            ["git", "checkout", branch2],
            cwd=temp_repo,
            check=True,
        )
        head_commit_branch2 = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=temp_repo,
            capture_output=True,
            text=True,
        ).stdout.strip()

        analyze_two_commits_with_cache(
            repo_path, head_commit_branch1, head_commit_branch2, output_dir
        )

    except Exception as e:
        print(f"Error comparing branches {branch1} and {branch2}: {e}")

    finally:
        shutil.rmtree(temp_repo)
