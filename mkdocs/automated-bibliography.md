# Автоматическая сверка библиографии

## Что реализовано

`concept_engine/reconcile_sources.py` сопоставляет DOI-статьи с Crossref и книжные поисковые записи с Open Library. Результат — JSON-очередь **кандидатов**, а не автоматическое доказательство или подтверждение цитирования. Для каждой записи сохраняются исходные реквизиты, найденные варианты, оценки сходства названия и автора, совпадение года и статус ручной проверки.

## Запуск

```bash
python3 concept_engine/validate_bibliography.py
python3 -m unittest discover -s concept_engine -p 'test_*.py' -v
python3 concept_engine/reconcile_sources.py --output build/bibliography/reconciliation.json
python3 concept_engine/reconcile_sources.py --online --output build/bibliography/reconciliation-online.json
python3 concept_engine/reconcile_sources.py --online --limit 10
python3 concept_engine/audit_bibliography.py
```

Без `--online` программа не обращается к внешним сервисам. Онлайн-режим использует ограничение частоты запросов, повторные попытки и тайм-ауты. Сетевые ошибки записываются в отчёт и не интерпретируются как отсутствие книги или статьи.

Workflow `.github/workflows/bibliography-online.yml` запускается вручную через GitHub Actions или по понедельникам (UTC) **после слияния workflow в default branch**. Отчёт доступен в Actions → Artifacts в течение 90 дней. Рабочий workflow `concepts.yml` также создаёт офлайн-очередь при PR.

## Что алгоритм не делает

- Не проверяет страницу или главу внутри книги, если полный текст недоступен.
- Не извлекает защищённые авторским правом полные тексты.
- Не делает выводов о физической истинности метафизических гипотез.
- Не переписывает `data/references.json` и `data/catalog.json` по результатам поиска.
- Не считает высокое сходство названия достаточным для точной атрибуции.
- Не считает поисковую ссылку WorldCat подтверждением ISBN, издания или конкретной страницы.

## Протокол работы редактора

1. Скачать `reconciliation-online.json` из GitHub Actions.
2. Сначала просмотреть `ambiguous_candidate_manual_review`, `no_candidate_or_lookup_failed`, затем `high_confidence_candidate_not_verified`.
3. Для каждой позиции проверить автора, точное издание, год, DOI/ISBN и текст первоисточника.
4. Указать страницу, цитату, контекст и источник изображения для конкретной концепции.
5. Только после проверки обновлять машиночитаемый реестр отдельным PR.

## Ограничения качества

Crossref и Open Library неполны для редких эзотерических изданий. Совпадение названия не гарантирует совпадения издания, автора или содержания. В каталоге KEUM тематические ссылки на физику и биологию служат сравнением, а не доказательством Keylontic, Merkaba, Hova и аналогичных утверждений.
