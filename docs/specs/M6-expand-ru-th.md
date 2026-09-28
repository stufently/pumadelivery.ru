# Веха M6: расширение 9 статей «Россия → Таиланд» проверяемым содержанием

- **Репозиторий:** `~/github/pumadelivery.ru` (статичный HTML, GitHub Pages, без сборки).
- **Дата постановки:** 2026-09-28.
- **BASE_SHA:** `782bfc08bd9a854520e399eeb283d6f44b70097a`
  (коммит «Apply article header rule to min CSS»; следующий коммит постановщика
  добавляет эту спеку `docs/specs/M6-expand-ru-th.md`, спеку-близнеца
  `docs/specs/M7-expand-th-ru.md`, чекер `docs/specs/check_m6.py` и
  `docs/specs/facts-m6-m7.md`).
- **Исполнитель:** Codex (`cx`) — выбор владельца.

## 1. Где работать

- Клон `/home/deploy/exec-clones/pumadelivery-m6-20260928`, ветка `m6-expand-ru-th`.
- **Живое дерево не трогать. `git push` запрещён** — постановщик заберёт через `git fetch`.
- Нужен только `python3` (stdlib) и `git`; сеть не нужна.

## 2. Задача и почему

Ревью контента (2026-09-28): статьи 900–1200 слов, одинаковый скелет, внешних
первоисточников почти нет, таблиц нет, h2 без вопросов — слабая цитируемость в
ИИ-поиске и риск «шаблонного контента». Владелец выбрал расширять **только
проверяемым**: правила, лимиты, первоисточники, разбор ошибок — без цен, без
историй клиентов, без статистики. Дополнительно — убрать `aggregateRating` из
`reviews.html` (самоотзывы: Google звёзды не покажет, разметка лишняя).

Статьи (группа `ru-th` в `check_articles.py`): `lekarstva-iz-rossii-v-tailand`,
`dokumenty-iz-rossii-v-tailand`, `russkie-produkty-v-tailand`,
`russkie-sladosti-v-tailand`, `chaj-med-specii-iz-rossii-v-tailand`,
`knigi-iz-rossii-v-tailand`, `zakazy-wildberries-ozon-v-tailand`,
`lichnye-veshchi-iz-rossii-v-tailand`, `zapchasti-iz-rossii-v-tailand`.

## 3. Что проверено вживую, а что предположение

- Факты — только `docs/specs/facts-delivery-demand.md` и `docs/specs/facts-m6-m7.md`
  (проверены постановщиком; в них помечены предположения — их не использовать как факт).
- Структура статей (проверено чтением): `<div class="content">` с абзацами и
  `<header class="major"><h2>…</h2></header>`, в конце «Частые вопросы» и
  CTA-раздел; FAQ в JSON-LD `FAQPage` дословно совпадает с видимым (чекер M5).
- В CSS сайта (`assets/css/main.min.css`) уже есть стили `table` и
  `.table-wrapper` — вёрстка таблицы: `<div class="table-wrapper"><table><thead>…</thead><tbody>…</tbody></table></div>`.
- Число слов на BASE — в `check_m6.py` (`BASE_WORDS`); чекер на BASE даёт 44 нарушения.
- `reviews.html:32-38` — `aggregateRating` внутри JSON-LD.

## 4. Что сделать (каждая из 9 статей)

1. **Таблица** «коротко о правилах» по категории статьи: `<thead>` и ≥4 строк
   в `<tbody>`; колонки на выбор, например «Что» / «Правило» / «Как поможем»
   или «Вопрос» / «Ответ» / «Источник». Только факты из двух пакетов.
2. **Раздел-вопрос:** хотя бы один `h2`, оканчивающийся «?» (например «Сколько
   <товара> можно передать за один раз?»), первый абзац под ним — прямой ответ
   40–60 слов.
3. **Раздел «Частые ошибки …»** (`h2` содержит «ошибк»): 4–6 пунктов списком,
   специфичных для категории (упаковка, документы, количество, запреты,
   сроки хранения — что относится к товару), каждая ошибка + как избежать.
4. **Ссылка на первоисточник** из таблицы `facts-m6-m7.md` (дословный URL, `&`
   в атрибуте — `&amp;`), подходящий к категории.
5. **Объём:** ≥ max(1300, BASE+300) слов — за счёт пунктов 1–3 и полезных
   уточнений, не воды; абзацы не повторяются между статьями (чекер статей
   ловит дубли).
6. Тон — продающий, как сейчас: каждая новая секция заканчивается тем, чем
   помогаем мы (пилоты и стюардессы, забор, курьер).
7. Не удалять существующие обязательные фразы (`check_articles.py`), не
   ломать FAQ (если меняешь FAQ — JSON-LD и видимый текст дословно), блок
   «Седжаро (Sejaro)» в статье о лекарствах сохранить как есть.

И отдельно: **`reviews.html`** — удалить `aggregateRating` из JSON-LD; отзывы
(`review`) и видимый текст не трогать.

## 5. Не трогать

Всё, кроме 9 статей выше и `reviews.html`: другие статьи, главная, города,
CSS, `sitemap.xml`, `llms.txt`, чекеры и пакеты фактов.

## 6. Разрешения

Коммиты в клоне — да (тема ≤50 символов, imperative, без подписей и
Co-Authored-By). Разрешённые пути от BASE_SHA: 9 статей выше, `reviews.html` и
закоммиченные постановщиком `docs/specs/M6-expand-ru-th.md`,
`docs/specs/M7-expand-th-ru.md`, `docs/specs/check_m6.py`, `docs/specs/facts-m6-m7.md`.

## 6a. Авторевью

Не вызывать (`review_run.sh` не запускать): дифф текстовый и больше лимита
обёртки; ревью координатор проводит вручную (Grok по видимому тексту).

## 7. Критерии приёмки

- **AC-001 — статьи расширены, рейтинг убран.** Команда: `bash -c 'python3 docs/specs/check_m6.py --group ru-th'`
- **AC-002 — прежние чекеры зелёные.** Команда: `bash -c 'python3 docs/specs/check_articles.py --group all && python3 docs/specs/check_m3.py && python3 docs/specs/check_m4.py && python3 docs/specs/check_m5.py'`
- **AC-003 — чекеры и пакеты фактов не изменены.** Команда: `bash -c 'd=$(git diff --name-only 782bfc08bd9a854520e399eeb283d6f44b70097a..HEAD -- docs/specs/check_articles.py docs/specs/check_m3.py docs/specs/check_m4.py docs/specs/check_m5.py docs/specs/facts-delivery-demand.md) || exit 1; e=$(git log --format=%h 782bfc08bd9a854520e399eeb283d6f44b70097a..HEAD -- docs/specs/check_m6.py docs/specs/facts-m6-m7.md | wc -l) || exit 1; test -z "$d" && test "$e" -eq 1'`
- **AC-004 — изменения только в разрешённых путях.** Команда: `bash -c 'd=$(git diff --name-only 782bfc08bd9a854520e399eeb283d6f44b70097a..HEAD) || exit 1; test -n "$d" || exit 1; bad=$(printf "%s\n" "$d" | grep -vxE "blog/(lekarstva-iz-rossii-v-tailand|dokumenty-iz-rossii-v-tailand|russkie-produkty-v-tailand|russkie-sladosti-v-tailand|chaj-med-specii-iz-rossii-v-tailand|knigi-iz-rossii-v-tailand|zakazy-wildberries-ozon-v-tailand|lichnye-veshchi-iz-rossii-v-tailand|zapchasti-iz-rossii-v-tailand)\.html|reviews\.html|docs/specs/(M6-expand-ru-th|M7-expand-th-ru)\.md|docs/specs/check_m6\.py|docs/specs/facts-m6-m7\.md"); echo "outside: $bad"; test -z "$bad"'`
- **AC-005 — рабочее дерево чистое.** Команда: `bash -c 'test -z "$(git status --porcelain --untracked-files=all -- . ":(exclude)report.json" ":(exclude)report-blocked.md" ":(exclude)docs/specs/__pycache__")"'`

Работу доказывает AC-001 (до работы красный); AC-002…AC-005 — охранные.

## 8. Контракт отчёта

`report.json` в корне клона, untracked, ровно 5 записей AC-001…AC-005.
`blocked` — когда среда не даёт выполнить критерий: `"rc": null`, дословная ошибка в `note`.

```json
{"criteria": [{"id": "AC-001", "status": "pass|fail|blocked",
               "command": "<команда ИЗ ЭТОЙ СПЕКИ, посимвольно>", "rc": 0, "note": "…"}]}
```

## 9. Контракт на невыполнимое

Невыполнимо (чекер противоречит спеке, нужного факта нет в пакетах) —
остановись, `report-blocked.md` в корне клона с командой, выводом и
`file:line`. Выдумывать факты, цены, истории клиентов, менять чекеры/спеку,
глушить коды возврата, пушить — запрещено.

## 10. Стыки

Параллельно идёт веха M7 (группа `th-ru`, другие файлы). После приёмки
постановщик сливает обе, прогоняет все чекеры, ревьюит текст, публикует и
отправляет URL в IndexNow.
