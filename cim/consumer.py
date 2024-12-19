import pandas as pd
import numpy as np


def load_table_as_numpy(filepath, **kwargs):
    """
    Загружает таблицу из файла и возвращает её в виде массива NumPy.

    Функция определяет тип файла по его расширению и использует соответствующую
    функцию pandas для чтения файла в DataFrame, который затем преобразуется в массив NumPy.

    Поддерживаемые расширения файлов:
    - CSV (.csv)
    - TSV (.tsv)
    - Excel (.xlsx, .xls)
    - XML (.xml)
    - JSON (.json)
    - Текст (.txt) - предполагается, что это таблица

    Параметры:
    filepath (str): Путь к файлу, который нужно загрузить.
    **kwargs: Дополнительные аргументы, передаваемые функции чтения pandas.

    Возвращает:
    numpy.ndarray: Данные таблицы в виде массива NumPy. Если расширение файла не поддерживается,
                   возвращается пустой массив NumPy.
    """
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
