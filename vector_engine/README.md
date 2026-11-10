# KEUM Vector Engine

Детерминированный процедурный SVG-генератор для восьми семейств геометрии из корпуса Kathara/Eckasha. Все элементы — настоящие SVG-примитивы (линии, окружности, контуры, текст), а не растровые картинки. **Не является научной моделью физических полей.**

## Запуск

```bash
python3 vector_engine/generator.py --preset all --output vector_engine/examples
python3 vector_engine/generator.py --preset merkaba --theme dark --size 1600 --complexity 3 --output merkaba.svg
python3 serve.py
```

В браузере: `http://localhost:8000/vector_engine/`.

Параметры: `--preset` (kathara, merkaba, lotus, reuche, crystal, clock, axiotonal, cosmology, all), `--theme` (manuscript/dark), `--size`, `--complexity` (1–3), `--no-labels`, `--output`.

## Архитектура

Функции геометрии используют полярные координаты `p(r,θ)=(r cos θ,r sin θ)`, конечные графы, окружности и параметрические кривые. Результаты проверяются XML-парсером. Для новых схем добавьте функцию `draw(svg,complexity)` и зарегистрируйте её в `DRAW`.

## Ограничения

Это процедурные **интерпретации**, а не точные векторные трассировки исходных страниц. Модель 15D отображена условно. Привязка каждой из 412 сущностей к графическим примитивам пока не реализована. SVG можно редактировать в Inkscape, Illustrator и импортировать в Blender.