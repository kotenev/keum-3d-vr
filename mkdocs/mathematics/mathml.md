# TeX и MathML: представление формул

В документации основной исходный формат — **LaTeX** внутри Markdown, отображаемый MathJax. Для машинного обмена математическими выражениями предусмотрен **Presentation MathML**. Эти два формата представляют одну математическую семантику разными способами.

## Пример 1. Лапласиан графа

LaTeX:

```tex
L = D - A
```

$$L=D-A.$$

Нативный MathML:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block">
  <mi>L</mi><mo>=</mo><mi>D</mi><mo>−</mo><mi>A</mi>
</math>

## Пример 2. Динамика Курамото

$$
\dot{\theta}_i=\omega_i+
\frac{K}{\max(1,d_i)}
\sum_{j=1}^{N}A_{ij}\sin(\theta_j-\theta_i).
$$

Нативный MathML для базового дифференциального соотношения:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block">
  <mover><msub><mi>θ</mi><mi>i</mi></msub><mo>˙</mo></mover>
  <mo>=</mo>
  <msub><mi>ω</mi><mi>i</mi></msub>
  <mo>+</mo>
  <msub><mi>F</mi><mi>i</mi></msub>
  <mo>(</mo><mi>θ</mi><mo>)</mo>
</math>

Здесь $F_i(\theta)$ — функция взаимодействия фаз, определённая полной формулой выше.

## Пример 3. Проекция

$$x=Pq,\qquad P\in\mathbb R^{3\times15}.$$

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block">
  <mi>x</mi><mo>=</mo><mi>P</mi><mi>q</mi>
</math>

## Технические замечания

- MathJax 3 отображает LaTeX, а также может обрабатывать MathML-вход; настройка сайта использует `tex-mml-chtml.js`.
- Примеры MathML выше — **нативная разметка**, которая не требует преобразования TeX в браузере.
- Не следует утверждать, что весь сайт экспортируется в MathML: автоматический пакетный конвертер TeX→MathML в текущей сборке отсутствует.
- Для строгой семантики в будущем можно использовать Content MathML или OpenMath, но они требуют отдельного сопоставления символов и операторов.

См. [MathML Core](https://www.w3.org/TR/mathml-core/) и [MathJax](https://docs.mathjax.org/).
