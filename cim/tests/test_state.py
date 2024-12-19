import os
from unittest import mock

from cim.state import collect_file_states, analyze_changes_between_states


@mock.patch("cim.state.os.walk")
@mock.patch("cim.state.count_lines_in_file")
def test_collect_file_states(mock_count_lines, mock_walk):
    repo_path = "/path/to/repo"
    mock_walk.return_value = [
        ("/path/to/repo/data", ("subdir",), ("file1.txt", "file2.txt")),
        ("/path/to/repo/data/subdir", (), ("file3.txt",)),
    ]
    mock_count_lines.side_effect = [10, 20, 30]

    result = collect_file_states(repo_path)
    expected = {
        "/path/to/repo/data/file1.txt": 10,
        "/path/to/repo/data/file2.txt": 20,
        "/path/to/repo/data/subdir/file3.txt": 30,
    }
    assert result == expected
    mock_walk.assert_called_once_with(os.path.join(repo_path, "data"))
    assert mock_count_lines.call_count == 3


def test_analyze_changes_between_states():
    old_state = {
        "/path/to/repo/data/file1.txt": 10,
        "/path/to/repo/data/file2.txt": 20,
    }
    new_state = {
        "/path/to/repo/data/file2.txt": 25,
        "/path/to/repo/data/file3.txt": 30,
    }

    result = analyze_changes_between_states(old_state, new_state)
    expected = {
        "added_lines": 30,
        "deleted_lines": 10,
        "modified_lines": 5,
    }
    assert result == expected
