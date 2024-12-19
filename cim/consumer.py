import pandas as pd
import numpy as np


def load_table_as_numpy(filepath, **kwargs):
    # Определение типа файла по расширению
    file_extension = filepath.split(".")[-1].lower()

    if file_extension in ["csv", "tsv"]:
        # CSV и TSV файлы
        delimiter = "," if file_extension == "csv" else "\t"
        df = pd.read_csv(filepath, delimiter=delimiter, **kwargs)

    elif file_extension in ["xlsx", "xls"]:
        # Excel файлы
        df = pd.read_excel(filepath, **kwargs)

    elif file_extension == "xml":
        # XML файлы
        df = pd.read_xml(filepath, **kwargs)

    elif file_extension == "json":
        # JSON файлы
        df = pd.read_json(filepath, **kwargs)

    elif file_extension in ["txt"]:
        # Текстовые файлы (предполагаем таблицу)
        df = pd.read_csv(filepath, delimiter=None, **kwargs)

    else:
        print(f"Unsupported file extension: {file_extension}; file {filepath} ignored")
        return np.empty((0, 0))

    return df.to_numpy()
