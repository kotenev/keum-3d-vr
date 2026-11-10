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