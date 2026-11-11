# KEUM · интерактивный 3D/VR-атлас Kathara–Eckasha

**Что это:** исследовательский симулятор семи слоёв, построенный на основе 49 изображений и каталога из 412 понятий. Это **не научная теория о реальной Вселенной**.

## Запуск

1. Установите Python 3 (если ещё не установлен).
2. Из каталога проекта выполните `python3 serve.py`.
3. Откройте `http://localhost:8000` в Chrome, Edge или Firefox.
4. Для WebXR используйте поддерживаемую VR-гарнитуру и браузер; кнопка `ENTER VR` появится, если WebXR доступен. Для удалённого доступа нужен HTTPS.

**Важно:** библиотеки Three.js загружаются из `cdn.jsdelivr.net`, поэтому при первом запуске нужен интернет. В офлайн-среде замените import map в `index.html` на локальные файлы Three.js и addons.

## Управление

- Левая кнопка мыши — вращение камеры, колесо — приближение, правая кнопка — перемещение.
- Выпадающий список — выбор композиции, чекбоксы — слои.
- Ползунки — скорость, визуальная связь, дыхание и условная проекция 15D→3D.
- Поиск — 412 понятий, нажатие на термин показывает описание.
- Нажатие на узел сцены показывает связанную концепцию.
- Пауза, сброс камеры, координатные оси.

## Структура

- `index.html` — интерфейс
- `src.js` — процедурная 3D-сцена и взаимодействия
- `data/catalog.json` — 412 терминов
- `docs/MATHEMATICAL_MODEL.md` — математическая постановка и границы
- `docs/TRACEABILITY.md` — прослеживаемость изображений к слоям
- `serve.py` — локальный сервер

## Лицензии и источники

Текстовый каталог подготовлен из рабочего реестра пользователя. Визуализация процедурная, оригинальные сканы в проект не включены. Three.js имеет лицензию MIT. Авторские термины Keylontic Science используются исключительно для исследования и сравнительной систематизации.

## Version 2 — shared graph engine

- Open `/vector_engine/editor.html` for an interactive drag-and-edit graph studio with SVG, JSON, and glTF export.
- Run `python3 vector_engine/graph_engine.py --preset all --output vector_engine/graph_exports` to regenerate 12 graph families.
- The 3D viewer accepts `?graph=kathara` (built-in) or `?graph=custom` after opening a graph in the editor.
- Technical specification: `docs/GRAPH_ENGINE_V2.md`.
- Run tests with `python3 -m unittest discover -s vector_engine -p 'test_*.py'`.

## Документация MkDocs

Подробный математический и архитектурный справочник расположен в [`mkdocs/`](mkdocs/index.md). Конфигурация — [`mkdocs.yml`](mkdocs.yml).

```bash
python3 -m pip install -r requirements-docs.txt
mkdocs serve
# или проверить сборку:
mkdocs build --strict
```

После настройки GitHub Pages на ветку `gh-pages` сайт можно открыть по адресу https://kotenev.github.io/keum-3d-vr/ . Формулы написаны в LaTeX, а отдельная глава содержит нативные примеры MathML. Документация отличает реализованные алгоритмы от математических спецификаций и эзотерических утверждений.


## KEUM 3.1 — индивидуальные конструкции и проверка точности

Добавлены [19 специализированных геометрических представлений](mkdocs/implementation/source-aware-models.md), [количественные метрики](concept_engine/fidelity.py) (RMSE, Chamfer, топология), [реестр происхождения](concept_engine/provenance.py) всех 412 понятий и автоматические тесты. Исходные изображения пока не размечены метрологически; специализированная геометрия является интерпретацией, а не точной копией.

```bash
python3 -m unittest discover -s concept_engine -p 'test_*.py'
python3 concept_engine/export_all.py --output vector_engine/graph_exports
python3 concept_engine/provenance.py --output build/provenance_412.json
```


## KEUM 3.2 — реконструкция 49 исходных схем

Добавлен [OpenCV-пайплайн](reconstruction/pipeline.py) извлечения линий, окружностей и контуров, [интерфейс ручной проверки](reconstruction/review.html), [QA-отчёт 49 изображений](reconstruction/results/QA_REPORT.md) и [манифест с SHA-256](reconstruction/results/manifest.json). Обработаны 49 оригинальных JPG; полученные SVG являются **непроверенными кандидатами**, а не геометрически точными реконструкциями.

```bash
python3 -m pip install -r reconstruction/requirements.txt
python3 -m unittest discover -s reconstruction -p 'test_*.py'
python3 reconstruction/pipeline.py --sources /path/to/49/images --output build/reconstruction
```

Подробности: [MkDocs — реконструкция 49 изображений](mkdocs/implementation/image-reconstruction.md).


## KEUM 3.3 — ручная проверка 49 схем и привязка 412 понятий

Запустите `python3 serve.py` и откройте [инструмент разметки](reconstruction/manual_workbench.html) по адресу `http://localhost:8000/reconstruction/manual_workbench.html`. Загрузите локально оригинальный JPG и соответствующий `candidates.json`, поставьте контрольные точки и экспортируйте JSON проверки.

- [Связи всех 412 понятий с исходными изображениями](reconstruction/results/concept_image_links_412.json) — **77 конкретных подсказок**, **335 неразрешённых**, **0 подтверждённых**.
- [Валидатор ручных проверок](reconstruction/validate_reviews.py) — контроль источника, геометрических точек, статуса, RMSE/Chamfer.
- [MkDocs — методика](mkdocs/implementation/image-reconstruction.md).

Оригинальные 49 изображения и полный набор кандидатов OpenCV остаются локальными материалами и не размещены публично. Отметки `verified` могут появляться только после реальной экспертной проверки.
