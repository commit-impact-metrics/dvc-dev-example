import os
import shutil
import subprocess
import tempfile

import numpy as np

from cim.utils import (
    clone_and_prepare_repo,
    pull_dvc_cache,
    save_metrics_to_file,
    read_dvc_yaml,
    get_file_diff_stats,
)
from cim.analysis import calculate_risk
from cim.consumer import load_table_as_numpy


def process_file_changes(file: str, temp_old_dir, temp_new_dir):
    old_file_path = os.path.join(temp_old_dir, file)
    new_file_path = os.path.join(temp_new_dir, file)

    if not os.path.exists(old_file_path) and not os.path.exists(new_file_path):
        return None

    old_data = (
        load_table_as_numpy(old_file_path)
        if os.path.exists(old_file_path)
        else np.empty((0, 0))
    )
    new_data = (
        load_table_as_numpy(new_file_path)
        if os.path.exists(new_file_path)
        else np.empty((0, 0))
    )

    try:
        risk = calculate_risk(old_data, new_data)
    except Exception as e:
        print(f"Error calculating risk for {file}: {str(e)}")
        return 0
    return risk


def save_commit_files(repo_path, commit, temp_dir, dvc_yaml):
    """
    Сохраняет файлы для заданного коммита в временную папку.

    :param repo_path: Путь к репозиторию.
    :param commit: Хэш коммита.
    :param temp_dir: Временная папка для сохранения файлов.
    :return: Список сохраненных файлов.
    """

    subprocess.run(
        ["git", "checkout", commit],
        cwd=repo_path,
        check=True,
    ).stdout
    pull_dvc_cache(repo_path)

    files = {}
    for stage in dvc_yaml["stages"]:
        stage_files = (
            dvc_yaml["stages"][stage]["deps"] + dvc_yaml["stages"][stage]["outs"]
        )
        files[stage] = []
        for file in stage_files:
            try:
                full_path = os.path.join(repo_path, file)
                print(full_path)
                if os.path.isfile(full_path):
                    shutil.copy2(full_path, os.path.join(temp_dir, file))
                    files[stage].append(file)

                elif os.path.isdir(full_path):
                    shutil.copytree(full_path, os.path.join(temp_dir, file))
                    files[stage].extend(
                        [os.path.join(file, f) for f in os.listdir(full_path)]
                    )

            except Exception as e:
                print(f"{commit} -- {file}: {str(e)}")
    return files


def analyze_two_commits_with_cache(
    repo_path: str, old_commit: str, new_commit: str, output_dir: str
):
    """
    Анализирует изменения между двумя коммитами и записывает
    результаты в output_dir.
    Работает с временным клоном репозитория.
    """
    temp_repo = clone_and_prepare_repo(repo_path)
    temp_old_files = tempfile.mkdtemp()
    temp_new_files = tempfile.mkdtemp()
    try:
        os.makedirs(output_dir, exist_ok=True)
        print(f"Analyzing commit: {new_commit} (compare with {old_commit})")

        try:
            dvc_yaml = read_dvc_yaml(temp_repo)

            old_files = save_commit_files(
                temp_repo, old_commit, temp_old_files, dvc_yaml
            )
            print(f"Old commit files: {old_files}")
            new_files = save_commit_files(
                temp_repo, new_commit, temp_new_files, dvc_yaml
            )
            print(f"New commit files: {new_files}")

            all_metrics = {}

            for stage in dvc_yaml["stages"]:
                stage_files = set()
                stage_files.update(old_files[stage])
                stage_files.update(new_files[stage])

                print(f"Processing stage: {stage} files: {stage_files}")
                all_metrics[stage] = {}
                for file in stage_files:
                    all_metrics[stage][file] = process_file_changes(
                        file=file,
                        temp_old_dir=temp_old_files,
                        temp_new_dir=temp_new_files,
                    )

                print(
                    f'Processing stage: {stage} files: {dvc_yaml["stages"][stage]["deps_py"]}'
                )
                for file in dvc_yaml["stages"][stage]["deps_py"]:
                    all_metrics[stage][file] = get_file_diff_stats(
                        file, old_commit, new_commit
                    )

            save_metrics_to_file(new_commit, all_metrics, output_dir)

        except Exception as e:
            print(f"Error analyzing commit {new_commit}: {str(e)}")

    finally:
        shutil.rmtree(temp_repo)
        shutil.rmtree(temp_old_files)
        shutil.rmtree(temp_new_files)
