import os

from cim.utils import count_lines_in_file


def collect_file_states(repo_path):
    """
    Собирает состояние файлов в репозитории.

    :param repo_path: Путь к репозиторию.
    :return: Словарь с состоянием файлов.
    """
    file_states = {}
    for root, _, files in os.walk(os.path.join(repo_path, "data")):
        for file in files:
            file_path = os.path.join(root, file)
            file_states[file_path] = count_lines_in_file(file_path)
    return file_states


def analyze_changes_between_states(old_state, new_state):
    """
    Анализирует изменения между двумя состояниями файлов.

    :param old_state: Состояние файлов в старом коммите.
    :param new_state: Состояние файлов в новом коммите.
    :return: Метрики изменений.
    """
    added = 0
    deleted = 0
    modified = 0

    all_files = set(old_state.keys()).union(set(new_state.keys()))
    for file_path in all_files:
        old_lines = old_state.get(file_path, 0)
        new_lines = new_state.get(file_path, 0)

        if old_lines == 0 and new_lines > 0:
            added += new_lines
        elif old_lines > 0 and new_lines == 0:
            deleted += old_lines
        elif old_lines != new_lines:
            modified += abs(new_lines - old_lines)

    return {
        "added_lines": added,
        "deleted_lines": deleted,
        "modified_lines": modified,
    }
