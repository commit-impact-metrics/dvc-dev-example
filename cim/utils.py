import json
import os
import tempfile
import subprocess
import yaml


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


def read_dvc_yaml(repo_dir: str = "."):
    """
    Читает файл dvc.yaml и возвращает его содержимое, разделяя зависимости на данные и py файлы.

    :param repo_dir: Путь к репозиторию.
    :return: Содержимое dvc.yaml в виде словаря с разделенными зависимостями.
    """
    dvc_yaml_path = os.path.join(repo_dir, "dvc.yaml")
    with open(dvc_yaml_path, "r") as f:
        dvc_yaml_content = yaml.safe_load(f)

    for stage in dvc_yaml_content.get("stages", {}).values():
        deps = stage.get("deps", [])
        stage["deps_py"] = [dep for dep in deps if dep.endswith(".py")]
        stage["deps"] = [dep for dep in deps if not dep.endswith(".py")]

    return dvc_yaml_content


def get_file_diff_stats(file_path, commit1, commit2):
    """
    Возвращает статистику изменений строк в файле между двумя коммитами.

    Args:
        file_path (str): Путь к файлу.
        commit1 (str): Хэш или идентификатор первого коммита.
        commit2 (str): Хэш или идентификатор второго коммита.

    Returns:
        dict: Статистика с количеством добавленных и удаленных строк.
    """
    try:
        # Выполняем команду git diff --numstat
        result = subprocess.run(
            ["git", "diff", "--numstat", commit1, commit2, "--", file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )

        # Проверяем вывод
        output = result.stdout.strip()
        if not output:
            return {"added": 0, "deleted": 0, "file": file_path}

        # Разбираем вывод (формат: добавленные удаленные файл)
        added, deleted, _ = output.split("\t")
        return {"added": int(added), "deleted": int(deleted), "file": file_path}
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Ошибка выполнения git diff: {e.stderr}")
    except ValueError:
        raise RuntimeError(f"Неверный формат вывода git diff: {result.stdout}")
