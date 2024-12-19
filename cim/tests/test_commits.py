import os
import tempfile
import shutil
from unittest import mock
import numpy as np
from cim.commits import (
    process_file_changes,
    save_commit_files,
    analyze_two_commits_with_cache,
)


@mock.patch("cim.commits.load_table_as_numpy")
@mock.patch("cim.commits.calculate_risk")
def test_process_file_changes(mock_calculate_risk, mock_load_table_as_numpy):
    mock_load_table_as_numpy.side_effect = [
        np.array([[1, 2], [3, 4]]),
        np.array([[1, 2], [3, 5]]),
    ]
    mock_calculate_risk.return_value = 0.5

    temp_old_dir = tempfile.mkdtemp()
    temp_new_dir = tempfile.mkdtemp()
    try:
        old_file = os.path.join(temp_old_dir, "file.csv")
        new_file = os.path.join(temp_new_dir, "file.csv")
        with open(old_file, "w") as f:
            f.write("1,2\n3,4")
        with open(new_file, "w") as f:
            f.write("1,2\n3,5")

        risk = process_file_changes("file.csv", temp_old_dir, temp_new_dir)
        assert risk == 0.5
    finally:
        shutil.rmtree(temp_old_dir)
        shutil.rmtree(temp_new_dir)


@mock.patch("cim.commits.pull_dvc_cache")
@mock.patch("cim.commits.shutil.copy2")
@mock.patch("cim.commits.shutil.copytree")
@mock.patch("cim.commits.subprocess.run")
def test_save_commit_files(mock_run, mock_copytree, mock_copy2, mock_pull_dvc_cache):
    mock_run.return_value = mock.Mock(stdout="")
    mock_pull_dvc_cache.return_value = None
    mock_copy2.return_value = None
    mock_copytree.return_value = None

    repo_path = tempfile.mkdtemp()
    temp_dir = tempfile.mkdtemp()
    try:
        dvc_yaml = {
            "stages": {
                "stage1": {
                    "deps": ["file1.csv"],
                    "outs": ["dir1"],
                }
            }
        }
        os.makedirs(os.path.join(repo_path, "dir1"))
        with open(os.path.join(repo_path, "file1.csv"), "w") as f:
            f.write("data")

        files = save_commit_files(repo_path, "commit", temp_dir, dvc_yaml)
        assert "stage1" in files
        assert "file1.csv" in files["stage1"]
    finally:
        shutil.rmtree(repo_path)
        shutil.rmtree(temp_dir)


@mock.patch("cim.commits.clone_and_prepare_repo")
@mock.patch("cim.commits.save_commit_files")
@mock.patch("cim.commits.read_dvc_yaml")
@mock.patch("cim.commits.process_file_changes")
@mock.patch("cim.commits.get_file_diff_stats")
@mock.patch("cim.commits.save_metrics_to_file")
def test_analyze_two_commits_with_cache(
    mock_save_metrics_to_file,
    mock_get_file_diff_stats,
    mock_process_file_changes,
    mock_read_dvc_yaml,
    mock_save_commit_files,
    mock_clone_and_prepare_repo,
):
    mock_clone_and_prepare_repo.return_value = tempfile.mkdtemp()
    mock_read_dvc_yaml.return_value = {
        "stages": {
            "stage1": {
                "deps": ["file1.csv"],
                "outs": ["file2.csv"],
                "deps_py": ["script.py"],
            }
        }
    }
    mock_save_commit_files.side_effect = [
        {"stage1": ["file1.csv", "file2.csv", "script.py"]},
        {"stage1": ["file1.csv", "file2.csv", "script.py"]},
    ]
    mock_process_file_changes.return_value = 0.5
    mock_get_file_diff_stats.return_value = {"added": 10, "deleted": 5, "file": "script.py"}

    repo_path = tempfile.mkdtemp()
    output_dir = tempfile.mkdtemp()
    try:
        analyze_two_commits_with_cache(repo_path, "commit1", "commit2", output_dir)
        mock_save_metrics_to_file.assert_called_once()
    finally:
        shutil.rmtree(repo_path)
        shutil.rmtree(output_dir)
