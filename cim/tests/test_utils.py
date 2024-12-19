import os
import subprocess

from unittest import mock

from cim.utils import (
    clone_and_prepare_repo,
    pull_dvc_cache,
    save_metrics_to_file,
    get_git_commits,
    count_lines_in_file,
    read_dvc_yaml,
    get_file_diff_stats,
)


@mock.patch("cim.utils.subprocess.run")
@mock.patch("cim.utils.tempfile.mkdtemp", return_value="/tmp/repo")
def test_clone_and_prepare_repo(mock_mkdtemp, mock_run):
    repo_path = "https://github.com/user/repo.git"
    branch = "main"
    result = clone_and_prepare_repo(repo_path, branch)
    assert result == "/tmp/repo"
    mock_run.assert_any_call(["git", "clone", repo_path, "/tmp/repo"], check=True)
    mock_run.assert_any_call(["git", "checkout", branch], cwd="/tmp/repo", check=True)


@mock.patch("cim.utils.subprocess.run")
def test_pull_dvc_cache(mock_run):
    repo_dir = "/path/to/repo"
    pull_dvc_cache(repo_dir)
    mock_run.assert_called_once_with(["dvc", "pull"], cwd=repo_dir, check=True)


@mock.patch("cim.utils.os.makedirs")
@mock.patch("cim.utils.open", new_callable=mock.mock_open)
def test_save_metrics_to_file(mock_open, mock_makedirs):
    commit = "abc123"
    metrics = {"accuracy": 0.95}
    output_dir = "/path/to/output"
    save_metrics_to_file(commit, metrics, output_dir)
    mock_makedirs.assert_called_once_with(output_dir, exist_ok=True)
    mock_open.assert_called_once_with(os.path.join(output_dir, f"{commit}.json"), "w")
    mock_open().write.assert_has_calls(
        [
            mock.call("{"),
            mock.call("\n    "),
            mock.call('"accuracy"'),
            mock.call(": "),
            mock.call("0.95"),
            mock.call("\n"),
            mock.call("}"),
        ]
    )


@mock.patch("cim.utils.subprocess.run")
def test_get_git_commits(mock_run):
    repo_path = "/path/to/repo"
    n = 5
    mock_run.return_value = mock.Mock(
        returncode=0, stdout="commit1\ncommit2\ncommit3\ncommit4\ncommit5\n"
    )
    result = get_git_commits(repo_path, n)
    assert result == ["commit1", "commit2", "commit3", "commit4", "commit5"]
    mock_run.assert_called_once_with(
        ["git", "log", "--format=%H", f"-n{n}"],
        cwd=repo_path,
        capture_output=True,
        text=True,
    )


@mock.patch(
    "cim.utils.open", new_callable=mock.mock_open, read_data="line1\nline2\nline3\n"
)
def test_count_lines_in_file(mock_open):
    file_path = "/path/to/file"
    result = count_lines_in_file(file_path)
    assert result == 3
    mock_open.assert_called_once_with(file_path, "r")


@mock.patch(
    "cim.utils.open",
    new_callable=mock.mock_open,
    read_data="stages:\n  stage1:\n    deps:\n      - data.csv\n      - script.py\n",
)
def test_read_dvc_yaml(mock_open):
    repo_dir = "/path/to/repo"
    result = read_dvc_yaml(repo_dir)
    expected = {"stages": {"stage1": {"deps": ["data.csv"], "deps_py": ["script.py"]}}}
    assert result == expected
    mock_open.assert_called_once_with(os.path.join(repo_dir, "dvc.yaml"), "r")


@mock.patch("cim.utils.subprocess.run")
def test_get_file_diff_stats(mock_run):
    file_path = "file.txt"
    commit1 = "abc123"
    commit2 = "def456"
    mock_run.return_value = mock.Mock(returncode=0, stdout="10\t5\tfile.txt")
    result = get_file_diff_stats(file_path, commit1, commit2)
    expected = {"added": 10, "deleted": 5, "file": file_path}
    assert result == expected
    mock_run.assert_called_once_with(
        ["git", "diff", "--numstat", commit1, commit2, "--", file_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
    )
