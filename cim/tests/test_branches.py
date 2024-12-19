import pytest
import tempfile
import shutil
from unittest import mock
from cim.branches import compare_branches


@mock.patch("cim.branches.clone_and_prepare_repo")
@mock.patch("cim.branches.analyze_two_commits_with_cache")
@mock.patch("cim.branches.subprocess.run")
@mock.patch("shutil.rmtree")
def test_compare_branches(mock_rmtree, mock_run, mock_analyze, mock_clone):
    repo_path = tempfile.mkdtemp()
    branch1 = "branch1"
    branch2 = "branch2"
    output_dir = tempfile.mkdtemp()
    temp_repo = "/tmp/repo"
    mock_clone.return_value = temp_repo
    mock_run.side_effect = [
        mock.Mock(stdout="commit1"),
        mock.Mock(stdout="commit2"),
        mock.Mock(stdout="commit1"),
        mock.Mock(stdout="commit2"),
    ]

    try:
        compare_branches(repo_path, branch1, branch2, output_dir)

        mock_clone.assert_called_once_with(repo_path)
        assert mock_run.call_count == 4
        mock_run.assert_any_call(
            ["git", "checkout", branch1], cwd=temp_repo, check=True
        )
        mock_run.assert_any_call(
            ["git", "rev-parse", "HEAD"], cwd=temp_repo, capture_output=True, text=True
        )
        mock_run.assert_any_call(
            ["git", "checkout", branch2], cwd=temp_repo, check=True
        )
        mock_run.assert_any_call(
            ["git", "rev-parse", "HEAD"], cwd=temp_repo, capture_output=True, text=True
        )
    finally:
        shutil.rmtree(repo_path)
        shutil.rmtree(output_dir)
