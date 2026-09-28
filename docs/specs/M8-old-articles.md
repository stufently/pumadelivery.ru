# Веха M8: 7 старых статей блога — исправить факты и довести до стандарта

- **Репозиторий:** `~/github/pumadelivery.ru` (статичный HTML, GitHub Pages, без сборки).
- **Дата постановки:** 2026-09-28.
- **BASE_SHA:** `6b5c47eb19e90d98522e8d108a0b83d801adbae4`
  (коммит «List all five courier cities in Lazada article»; следующий коммит
  постановщика добавляет эту спеку `docs/specs/M8-old-articles.md`, чекер
  `docs/specs/check_m8.py` и пакет фактов `docs/specs/facts-m8.md`).
- **Исполнитель:** Codex (`cx`) — выбор владельца («доведи старые статьи тоже»).

## 1. Где работать

- Клон `/home/deploy/exec-clones/pumadelivery-m8-20260928`, ветка `m8-old-articles`.
- **Живое дерево не трогать. `git push` запрещён** — постановщик заберёт через `git fetch`.
- Нужен только `python3` (stdlib) и `git`; сеть не нужна.

## 2. Задача и почему

19 новых статей уже доведены до стандарта (таблица правил, h2-вопрос с
прямым ответом, раздел «Частые ошибки», ссылка на первоисточник). 7 старых
статей (`OLD_ARTICLES` в `check_articles.py`) — нет, и фактчекинг постановщика
нашёл в них неверные и неподтверждённые утверждения (цены, проценты, устаревшие
правила, рискованные советы). Владелец выбрал: только проверяемое.

Статьи: `chto-nelzya-vvozit-v-tailand`, `receptury-lekarstva-turistu`,
`kak-zakazat-s-lazada-v-tailande`, `lazada-vs-shopee`,
`dostavka-alkogolya-v-tailande`, `perevozka-mezhdu-gorodami-tailanda`,
`tajskaya-bankovskaya-karta-2026`.

## 3. Что проверено вживую, а что предположение

- **Факты — только `docs/specs/facts-m8.md`** (фактчекинг 2026-09-28, по каждой
  статье таблица «утверждение — вердикт — что писать» и официальные URL с
  цитатами) и уже действующие пакеты `facts-delivery-demand.md`, `facts-m6-m7.md`.
  В `facts-m8.md` помечено, где первоисточник вторичный (безвиз 30 дней).
- Структура статей (проверено чтением): `<div class="content">`, разделы
  `<header class="major"><h2>…</h2></header>`, «Частые вопросы» с FAQ, CTA.
  FAQ `FAQPage` в JSON-LD дословно совпадает с видимым (`check_m5.py`).
- `.table-wrapper` и `table` уже стилизованы в `assets/css/main.min.css`.
- Чекер `check_m8.py` на BASE даёт 98 нарушений (ожидаемо до работы).

## 4. Что сделать (каждая из 7 статей)

1. **Исправить факты по `facts-m8.md`:** НЕВЕРНО → заменить на указанное;
   НЕ ПОДТВЕРЖДАЕТСЯ → убрать цифру/название или переформулировать без
   процентов и сумм; ОПАСНО → удалить совет. Если утверждение стоит и в FAQ —
   менять одинаково в JSON-LD и в видимом FAQ (дословно).
2. **Таблица** по теме статьи: `<div class="table-wrapper"><table><thead>…</thead><tbody>…</tbody></table></div>`,
   ≥4 строк в `<tbody>`, только проверенные факты.
3. **h2-вопрос** (оканчивается «?»), под ним прямой ответ 40–60 слов.
4. **Раздел «Частые ошибки …»** (`h2` содержит «ошибк»): 4–6 пунктов списком.
5. **Ссылка на первоисточник** из `facts-m8.md` (дословный URL, `&` → `&amp;`).
6. **Объём:** ≥ BASE+150 слов (`BASE_WORDS` в чекере) — удалённые цифры
   компенсировать полезным проверяемым содержанием, не водой.
7. Тон — продающий, как в статьях блога; каждая новая секция заканчивается тем,
   чем помогаем мы (курьеры в 5 городах, передача через пилотов/стюардесс).
8. `Article.dateModified` в JSON-LD — `2026-09-28` (уже стоит; не менять).

## 5. Не трогать

Всё, кроме 7 статей выше: другие статьи, главная, города, CSS, `sitemap.xml`,
`llms.txt`, чекеры и пакеты фактов.

## 6. Разрешения

Коммиты в клоне — да (тема ≤50 символов, imperative, без подписей и
Co-Authored-By). Разрешённые пути от BASE_SHA: 7 статей выше и закоммиченные
постановщиком `docs/specs/M8-old-articles.md`, `docs/specs/check_m8.py`,
`docs/specs/facts-m8.md`.

## 6a. Авторевью

Не вызывать (`review_run.sh` не запускать): дифф текстовый; ревью координатор
проводит вручную (Grok по видимому тексту).

## 7. Критерии приёмки

- **AC-001 — факты исправлены, стандарт выполнен.** Команда: `bash -c 'python3 docs/specs/check_m8.py'`
- **AC-002 — прежние чекеры зелёные.** Команда: `bash -c 'python3 docs/specs/check_articles.py --group all && python3 docs/specs/check_m3.py && python3 docs/specs/check_m4.py && python3 docs/specs/check_m5.py && python3 docs/specs/check_m6.py --group ru-th && python3 docs/specs/check_m6.py --group th-ru'`
- **AC-003 — чекеры и пакеты фактов не изменены.** Команда: `bash -c 'd=$(git diff --name-only 6b5c47eb19e90d98522e8d108a0b83d801adbae4..HEAD -- docs/specs/check_articles.py docs/specs/check_m3.py docs/specs/check_m4.py docs/specs/check_m5.py docs/specs/check_m6.py docs/specs/facts-delivery-demand.md docs/specs/facts-m6-m7.md) || exit 1; e=$(git log --format=%h 6b5c47eb19e90d98522e8d108a0b83d801adbae4..HEAD -- docs/specs/check_m8.py docs/specs/facts-m8.md | wc -l) || exit 1; test -z "$d" && test "$e" -eq 1'`
- **AC-004 — изменения только в разрешённых путях.** Команда: `bash -c 'd=$(git diff --name-only 6b5c47eb19e90d98522e8d108a0b83d801adbae4..HEAD) || exit 1; test -n "$d" || exit 1; bad=$(printf "%s\n" "$d" | grep -vxE "blog/(chto-nelzya-vvozit-v-tailand|receptury-lekarstva-turistu|kak-zakazat-s-lazada-v-tailande|lazada-vs-shopee|dostavka-alkogolya-v-tailande|perevozka-mezhdu-gorodami-tailanda|tajskaya-bankovskaya-karta-2026)\.html|docs/specs/M8-old-articles\.md|docs/specs/check_m8\.py|docs/specs/facts-m8\.md"); echo "outside: $bad"; test -z "$bad"'`
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

Невыполнимо (чекер противоречит спеке, нужного факта нет в пакетах, запрет
чекера задевает верное утверждение) — остановись, `report-blocked.md` в корне
клона с командой, выводом и `file:line`. Выдумывать факты и цены, менять
чекеры/спеку/пакеты фактов, глушить коды возврата, пушить — запрещено.

## 10. Стыки

После приёмки постановщик ревьюит текст, публикует, отправляет URL в IndexNow,
Яндекс (переобход) и Bing.
