import os
import shutil
import subprocess
from cim.state import analyze_changes_between_states, collect_file_states
from cim.utils import (
    clone_and_prepare_repo,
    pull_dvc_cache,
    save_metrics_to_file,
)


def analyze_two_commits_with_cache(
    repo_path: str, old_commit: str, new_commit: str, output_dir: str
):
    """
    Анализирует изменения между двумя коммитами и записывает
    результаты в output_dir.
    Работает с временным клоном репозитория.
    """
    temp_repo = clone_and_prepare_repo(repo_path)
    try:
        os.makedirs(output_dir, exist_ok=True)
        print(f"Analyzing commit: {new_commit} (compare with {old_commit})")

        try:
            subprocess.run(
                ["git", "checkout", old_commit],
                cwd=temp_repo,
                check=True,
            )
            pull_dvc_cache(temp_repo)
            old_state = collect_file_states(temp_repo)

            subprocess.run(
                ["git", "checkout", new_commit],
                cwd=temp_repo,
                check=True,
            )
            pull_dvc_cache(temp_repo)
            new_state = collect_file_states(temp_repo)

            metrics = analyze_changes_between_states(old_state, new_state)
            save_metrics_to_file(new_commit, metrics, output_dir)

        except Exception as e:
            print(f"Error analyzing commit {new_commit}: {e}")

    finally:
        shutil.rmtree(temp_repo)
