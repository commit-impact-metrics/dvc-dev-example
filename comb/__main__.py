import os
import sys
import json

def main(team_id, cd_id, input_file):
    print(f"Команда: {team_id}, Параметры бизнес-задачи: {cd_id}, Входной файл: {input_file}")

    # Пути к файлам
    team_file = os.path.join("comb", "teams", f"{team_id}.json")
    cd_file = os.path.join("comb", "cds", f"{cd_id}.json")

    # Проверяем, существуют ли файлы
    if not os.path.exists(team_file):
        print(f"Команда не найдена: {team_file}")
        return
    if not os.path.exists(cd_file):
        print(f"Параметры бизнес-задачи не найдены: {cd_file}")
        return
    if not os.path.exists(input_file):
        print(f"Входной файл не найден: {input_file}")
        return

    # Читаем файлы
    with open(team_file, 'r') as f:
        team_data = json.load(f)

    with open(cd_file, 'r') as f:
        cd_data = json.load(f)

    with open(input_file, 'r') as f:
        input_data = json.load(f)

    # Пример обработки данных
    metrics = {
        "criticality": {"weight": 0.35},
        "complexity": {"weight": 0.15},
        "error_sensitivity": {"weight": 0.2},
        "integration_complexity": {"weight": 0.2},
        "urgency": {"weight": 0.2},
        "team_experience": {"weight": 0.1},
        "past_errors": {"weight": 0.1}
    }

    # Объединяем данные
    user_input = {**cd_data, **team_data}

    # Расчёт риска
    total_risk = sum(metrics[key]["weight"] * user_input[key] for key in metrics)

    # Нормализация риска (0-1)
    max_risk = 5  # Предположим, максимальный риск равен 5
    normalized_risk = total_risk / max_risk

    # Классификация риска
    if total_risk < 2:
        risk_level = "Низкий"
    elif 2 <= total_risk < 3.5:
        risk_level = "Средний"
    elif 3.5 <= total_risk < 4.5:
        risk_level = "Высокий"
    else:
        risk_level = "Критический"

    print(f"Бизнес риск: {risk_level}")
    normalized_risk = normalized_risk/1.3
    print(f"Нормализованный: {normalized_risk:.2f}")

    # Анализ входного файла
    print("\nСредние значения оценки изменения данных по процессам:")
    stage_averages = {}
    for stage, stage_data in input_data.items():
        # Выбираем только ключи с числовыми значениями
        numeric_keys = [value for key, value in stage_data.items() if isinstance(value, (int, float))]
        if numeric_keys:
            avg_value = sum(numeric_keys) / len(numeric_keys)
            stage_averages[stage] = avg_value
            print(f"Процесс: {stage}, Среднее значение: {avg_value:.2f}")

    # Расчёт уровня риска по всей ветке и по максимальной оценке среди этапов
    if stage_averages:
        average_of_stages = sum(stage_averages.values()) / len(stage_averages)
        weakest_stage_value = max(stage_averages.values())

        branch_risk = average_of_stages
        weakest_stage_risk = weakest_stage_value

        print(f"\nСреднее значение риска: {branch_risk:.2f}")
        print(f"Максимальный уровень риска для отдельного процесса: {weakest_stage_risk:.2f}")

    combined_risk = (normalized_risk * branch_risk)

    # Классификация комбинированного риска
    if combined_risk < 0.1:
        combined_risk_level = "Низкий"
    elif 0.1 <= combined_risk < 0.3:
        combined_risk_level = "Средний"
    elif 0.3 <= combined_risk < 0.7:
        combined_risk_level = "Высокий"
    else:
        combined_risk_level = "Критический"

    # Выводим результаты
    print(f"\nКомбинированный уровень риска: {combined_risk_level}")
    print(f"Комбинированный нормализованный риск: {combined_risk:.2f}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python comb <teamId> <cdId> <inputFile>")
        sys.exit(1)
    
    team_id, cd_id, input_file = sys.argv[1], sys.argv[2], sys.argv[3]
    main(team_id, cd_id, input_file)
