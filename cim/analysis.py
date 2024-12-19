import numpy as np


def calculate_risk(old_data, new_data, weights=None):
    """
    Рассчитывает уровень риска на основе изменения показателей данных.

    Parameters:
    - old_data (numpy.ndarray): исходные данные
    - new_data (numpy.ndarray): новые данные
    - weights (dict): веса для каждого компонента ("rows", "columns", "duplicates", "nulls").
                      Если None, используются примерные веса.

    Returns:
    - Q (float): значение метрики риска.
    """
    # Базовые параметры
    R_0, C_0 = old_data.shape
    R_t, C_t = new_data.shape

    # Инициализация количества дубликатов
    D_0 = 0
    D_t = 0

    # Проверка дубликатов по числовым столбцам
    for col_idx in range(C_0):
        # Если тип столбца числовой
        if np.issubdtype(old_data[:, col_idx].dtype, np.number):
            unique_old = np.unique(old_data[:, col_idx])
            unique_new = np.unique(new_data[:, col_idx])

            # Добавляем разницу дубликатов
            D_0 += len(old_data[:, col_idx]) - len(unique_old)
            D_t += len(new_data[:, col_idx]) - len(unique_new)

    # Количество пустых значений (работает только с числовыми столбцами)
    N_0 = 0
    N_t = 0
    for col_idx in range(C_0):
        if np.issubdtype(old_data[:, col_idx].dtype, np.number):
            N_0 += np.isnan(old_data[:, col_idx]).sum()
            N_t += np.isnan(new_data[:, col_idx]).sum()

    # Изменения (в относительных величинах)
    delta_R = (R_t - R_0) / R_0 if R_0 > 0 else 0
    delta_C = (C_t - C_0) / C_0 if C_0 > 0 else 0
    delta_D = (D_t - D_0) / R_0 if R_0 > 0 else 0
    delta_N = (N_t - N_0) / (R_0 * C_0) if R_0 * C_0 > 0 else 0

    # Установка весов
    if weights is None:
        weights = {"rows": 0.2, "columns": 0.2, "duplicates": 0.4, "nulls": 0.2}

    # Рассчет метрики Q
    Q = (
        weights["rows"] * abs(delta_R)
        + weights["columns"] * abs(delta_C)
        + weights["duplicates"] * abs(delta_D)
        + weights["nulls"] * abs(delta_N)
    )

    return Q
