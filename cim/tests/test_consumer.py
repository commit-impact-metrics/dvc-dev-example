import os
import pandas as pd
import numpy as np
from unittest import mock
from cim.consumer import load_table_as_numpy


@mock.patch("pandas.read_csv")
def test_load_table_as_numpy_csv(mock_read_csv):
    mock_read_csv.return_value = pd.DataFrame({"col1": [1, 3], "col2": [2, 4]})
    result = load_table_as_numpy("data.csv")
    expected = np.array([[1, 2], [3, 4]])
    np.testing.assert_array_equal(result, expected)
    mock_read_csv.assert_called_once_with("data.csv", delimiter=",", **{})


@mock.patch("pandas.read_excel")
def test_load_table_as_numpy_excel(mock_read_excel):
    mock_read_excel.return_value = pd.DataFrame({"col1": [1, 3], "col2": [2, 4]})
    result = load_table_as_numpy("data.xlsx")
    expected = np.array([[1, 2], [3, 4]])
    np.testing.assert_array_equal(result, expected)
    mock_read_excel.assert_called_once_with("data.xlsx", **{})


@mock.patch("pandas.read_xml")
def test_load_table_as_numpy_xml(mock_read_xml):
    mock_read_xml.return_value = pd.DataFrame({"col1": [1, 3], "col2": [2, 4]})
    result = load_table_as_numpy("data.xml")
    expected = np.array([[1, 2], [3, 4]])
    np.testing.assert_array_equal(result, expected)
    mock_read_xml.assert_called_once_with("data.xml", **{})


@mock.patch("pandas.read_json")
def test_load_table_as_numpy_json(mock_read_json):
    mock_read_json.return_value = pd.DataFrame({"col1": [1, 3], "col2": [2, 4]})
    result = load_table_as_numpy("data.json")
    expected = np.array([[1, 2], [3, 4]])
    np.testing.assert_array_equal(result, expected)
    mock_read_json.assert_called_once_with("data.json", **{})


@mock.patch("pandas.read_csv")
def test_load_table_as_numpy_txt(mock_read_csv):
    mock_read_csv.return_value = pd.DataFrame({"col1": [1, 3], "col2": [2, 4]})
    result = load_table_as_numpy("data.txt")
    expected = np.array([[1, 2], [3, 4]])
    np.testing.assert_array_equal(result, expected)
    mock_read_csv.assert_called_once_with("data.txt", delimiter=None, **{})


def test_load_table_as_numpy_unsupported():
    result = load_table_as_numpy("data.unsupported")
    expected = np.empty((0, 0))
    np.testing.assert_array_equal(result, expected)
