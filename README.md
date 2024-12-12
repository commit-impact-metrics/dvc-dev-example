# Commit-impact-metrics

Источник: https://github.com/iterative/example-get-started.git

## Начало работы

```
python -m venv .venv
source .venv/bin/activate
pip install -r src/requirements.txt
```

пример использования
```
python -m cim 2-track-data
```
проведет сравнение текущей ветки с веткой 2-track-data. Результат запишет в output.

## TODO
1. Переопределить функции из cim/state, чтобы добавить более актуальные метрики сравнения;
2. Добавить конфиги;
3. Определить список поддерживаемых файлов. Неподдерживаемые игнорить при сравнении (.pkl сравнивать или нет? По какой метрике?)