import json
import os
import tempfile
import subprocess


def clone_and_prepare_repo(repo_path, branch=None):
    """Клонирует репозиторий в временную папку."""
    temp_dir = tempfile.mkdtemp()
    subprocess.run(["git", "clone", repo_path, temp_dir], check=True)
    if branch:
        subprocess.run(["git", "checkout", branch], cwd=temp_dir, check=True)
    return temp_dir


def pull_dvc_cache(repo_dir):
    """Пытается загрузить кэш DVC, если возможно."""
    try:
        subprocess.run(["dvc", "pull"], cwd=repo_dir, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Warning: Could not pull DVC cache. Error: {e}")


def save_metrics_to_file(commit, metrics, output_dir):
    """
    Сохраняет метрики для заданного коммита в JSON файл.

    :param commit: Хэш коммита.
    :param metrics: Метрики (словарь).
    :param output_dir: Папка для сохранения.
    """
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{commit}.json")
    with open(output_path, "w") as f:
        json.dump(metrics, f, indent=4)


def get_git_commits(repo_path, n):
    """
    Получает последние n коммитов в репозитории.

    :param repo_path: Путь к репозиторию.
    :param n: Количество последних коммитов.
    :return: Список хэшей коммитов (от старых к новым).
    """
    cmd = ["git", "log", "--format=%H", f"-n{n}"]
    result = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"Error running 'git log': {result.stderr.strip()}")

    return result.stdout.strip().split("\n")


def count_lines_in_file(file_path):
    """
    Подсчитывает количество строк в файле.

    :param file_path: Путь к файлу.
    :return: Количество строк.
    """
    try:
        with open(file_path, "r") as f:
            return sum(1 for _ in f)
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return 0
