# Веха M5: правки по повторному SEO/GEO-ревью pumadelivery.ru

- **Репозиторий:** `~/github/pumadelivery.ru` (статичный HTML, GitHub Pages, без сборки).
- **Дата постановки:** 2026-09-28.
- **BASE_SHA:** `63c97c1af408846edee89f31ad35109a890ffa48`
  (коммит «Add Sejaro section to medicine article»; следующий коммит постановщика
  добавляет эту спеку `docs/specs/M5-review-fixes.md` и чекер `docs/specs/check_m5.py`).
- **Исполнитель:** Codex (`cx`) — выбор владельца («сделай ревью сайта ещё раз
  кодексом»). Тестов исполнитель не пишет, проверка — готовый чекер постановщика.

## 1. Где работать

- Клон `/home/deploy/exec-clones/pumadelivery-m5-20260928`, ветка `m5-review-fixes`.
- **Живое дерево не трогать. `git push` запрещён** — постановщик заберёт через `git fetch`.
- Команды критериев — из корня клона; нужен только `python3` (stdlib) и `git`.

## 2. Задача и почему

Повторное ревью (Codex + агенты SEO/GEO) нашло на живом сайте устаревшие
правовые факты, которые вводят клиента в заблуждение, и расхождение разметки
FAQ с видимым текстом (нарушение правил Google о структурированных данных).

## 3. Что проверено вживую, а что предположение

Проверено постановщиком 2026-09-28 чтением файлов и первоисточников:

- **Алкоголь.** TAT, 29.05.2026 (`https://www.tatnews.org/2026/05/alcohol-sales-and-consumption-rules-updated-in-thailand-what-tourists-need-to-know/`):
  с 29 мая 2026 алкоголь в целом продают с 11:00 до 24:00; интервал
  14:00–17:00 стал обычным разрешённым временем (до этого был запрещён, в конце
  2025 ввели шестимесячный пробный режим). Вне этих часов продажа ограничена;
  в аэропортах, отелях, лицензированных заведениях могут действовать свои условия.
  Возраст — 20 лет; запреты в храмах, госучреждениях, на АЗС, в парках, в
  общественном транспорте; запреты в дни выборов и крупных религиозных праздников
  остаются.
- **Дьюти-фри.** Правительство Таиланда (`https://thailand.prd.go.th/en/content/category/detail/id/2078/iid/304245`):
  магазины дьюти-фри в зоне прилёта международных аэропортов приостановлены.
  Норма беспошлинного ввоза алкоголя — 1 литр (тайская таможня) — остаётся.
- **Каннабис.** TAT, 06.2025 (`https://www.tatnews.org/2025/06/cannabis-flower-now-strictly-regulated-in-thailand-important-notice-for-tourists/`):
  с 23 июня 2025 цветки каннабиса — контролируемое вещество (приказ Минздрава
  по закону о тайской традиционной медицине), продажа — по медицинскому
  рецепту; в список наркотиков каннабис с 2022 не возвращён. «Категория 5 с
  2025 года» — неверно.
- **Кратом** исключён из списка наркотиков категории 5 с 24 августа 2021
  (Narcotics Act No. 8 B.E. 2564) — «Категория 5 (…кратом)» неверно.
- **Места в коде:** часы 11:00–14:00/17:00–24:00 — `blog/dostavka-alkogolya-v-tailande.html`
  (meta/og description, FAQ JSON-LD, разделы «Базовые часы продажи», «Дьюти-фри»,
  «Что меняется в 2026 году», «Доставка алкоголя курьером», видимый FAQ),
  `pattaya.html`, `phuket.html`, `samui.html`, `phangan.html` (FAQ JSON-LD и
  видимый FAQ), `blog/index.html:167` («дневной разрыв»). Каннабис —
  `blog/chto-nelzya-vvozit-v-tailand.html:55,95,125`.
- **FAQ.** Ответы (а на части страниц и вопросы) `FAQPage` в JSON-LD не
  совпадают дословно с видимым FAQ на 13 страницах: `index.html`, 5 страниц
  городов, `blog/chto-nelzya-vvozit-v-tailand.html`, `blog/dostavka-alkogolya-v-tailande.html`,
  `blog/kak-zakazat-s-lazada-v-tailande.html`, `blog/lazada-vs-shopee.html`,
  `blog/perevozka-mezhdu-gorodami-tailanda.html`, `blog/receptury-lekarstva-turistu.html`,
  `blog/tajskaya-bankovskaya-karta-2026.html`. Видимые ответы — укороченные.
- **Автор.** Все статьи ссылаются на `/about.html#dmitry`; в JSON-LD `about.html`
  есть `@id …#dmitry`, но HTML-элемента с `id="dmitry"` нет (абзацы о Дмитрии —
  в `section#story`).
- **Мобильная шапка.** `assets/css/main.css:3005–3011`: в `@media screen and (max-width: 736px)`
  `#header { height: 80vh }` и `#header:after { height: 80vh }` — на телефоне
  шапка статьи занимает 80% экрана. У всех страниц `<body class="is-preload">`.
- Чекер `check_m5.py` на BASE даёт 230 нарушений (ожидаемо до работы).
- Предположений нет.

## 4. Что сделать

1. **FAQ всех страниц:** каждый вопрос (`name`) и ответ (`acceptedAnswer.text`)
   `FAQPage` должен дословно стоять в видимом блоке «Частые вопросы» той же
   страницы. Делай видимый FAQ полным (как в JSON-LD), а не урезай разметку;
   формат видимой записи как сейчас: `<p><strong>Вопрос</strong><br>Ответ</p>`.
2. **Алкоголь** (`blog/dostavka-alkogolya-v-tailande.html`): переписать под факты
   §3 — часы 11:00–24:00 с 29 мая 2026 со ссылкой на разъяснение TAT (URL из §3,
   дословно), история: до этого действовал запрет 14:00–17:00, в конце 2025 —
   пробный режим, теперь правило общее. Без слова «пилотный». Раздел «Дьюти-фри»:
   магазины в зоне прилёта приостановлены, купить заранее можно только при
   вылете; норма ввоза — 1 литр. Раздел «Что меняется в 2026 году» — про
   фактическое изменение. Вопрос FAQ «Почему алкоголь не продают днём с 14 до 17?»
   заменить на актуальный. meta/og description — без дневного перерыва (110–170
   символов). Часы работы баров 2:00/4:00, праздники, возраст, места — не трогать.
   Раздел «Доставка алкоголя курьером» и FAQ: возим в часы легальной продажи 11:00–24:00.
3. **Города** `pattaya/phuket/samui/phangan.html`: часы алкоголя → 11:00–24:00
   (JSON-LD и видимый FAQ одинаково).
4. **`blog/index.html`**: карточка статьи об алкоголе — без «дневного разрыва»,
   про общие часы 11:00–24:00.
5. **Каннабис/кратом** (`blog/chto-nelzya-vvozit-v-tailand.html`): каннабис — с
   23 июня 2025 цветки контролируемые, только по медицинскому рецепту, ввоз
   запрещён; ссылка на разъяснение TAT (URL из §3). Не называть «категорией 5»
   и не приписывать сроки наказания за каннабис. Кратом из перечня категории 5
   убрать. Остальные категории не трогать.
6. **`about.html`**: элемент с `id="dmitry"` на блоке о Дмитрии (например на
   `section#story` не выйдет — у неё уже id; поставь на `<h2>Как всё началось</h2>`
   или обёртку первого абзаца о Дмитрии). Ничего больше в `about.html` не менять.
7. **Мобильная шапка статей:** у `<body>` всех `blog/*.html`, кроме
   `blog/index.html`, класс `is-preload is-article`; в конец блока
   `@media screen and (max-width: 736px)` в `assets/css/main.css` —
   `body.is-article #header { height: auto; }` и
   `body.is-article #header:after { height: auto; }` (допустимы доп. свойства,
   например `min-height`/`padding`, чтобы заголовок статьи оставался читаемым).
   На десктопе и у остальных страниц ничего не меняется.
8. Тон — продающий, как в остальных статьях; не выдумывать фактов сверх §3.

## 5. Не трогать

`docs/specs/*` (кроме добавления `report.json` вне git), `sitemap.xml`,
`llms.txt`, `robots.txt`, изображения, JS, блок «Седжаро (Sejaro)» в
`blog/lekarstva-iz-rossii-v-tailand.html` (там только класс `<body>`).

## 6. Разрешения

Коммиты в клоне — да (тема ≤50 символов, imperative, без подписей и
Co-Authored-By). Разрешённые пути от BASE_SHA: `index.html`, `bangkok.html`,
`pattaya.html`, `phuket.html`, `samui.html`, `phangan.html`, `about.html`,
`blog/*.html`, `assets/css/main.css` и закоммиченные постановщиком
`docs/specs/M5-review-fixes.md`, `docs/specs/check_m5.py`.

## 6a. Авторевью

Не вызывать (`review_run.sh` не запускать): дифф текстовый и большой, ревью
проводит координатор вручную после сдачи.

## 7. Критерии приёмки

- **AC-001 — правки ревью на месте.** Команда: `bash -c 'python3 docs/specs/check_m5.py'`
- **AC-002 — прежние чекеры зелёные.** Команда: `bash -c 'python3 docs/specs/check_articles.py --group all && python3 docs/specs/check_m3.py && python3 docs/specs/check_m4.py'`
- **AC-003 — чекеры и спеки не изменены.** Команда: `bash -c 'd=$(git diff --name-only 63c97c1af408846edee89f31ad35109a890ffa48..HEAD -- docs/specs/check_articles.py docs/specs/check_m3.py docs/specs/check_m4.py docs/specs/facts-delivery-demand.md) || exit 1; test -z "$d"'`
- **AC-004 — изменения только в разрешённых путях.** Команда: `bash -c 'd=$(git diff --name-only 63c97c1af408846edee89f31ad35109a890ffa48..HEAD) || exit 1; test -n "$d" || exit 1; bad=$(printf "%s\n" "$d" | grep -vxE "index\.html|(bangkok|pattaya|phuket|samui|phangan)\.html|about\.html|blog/[a-z0-9-]+\.html|assets/css/main\.css|docs/specs/M5-review-fixes\.md|docs/specs/check_m5\.py"); echo "outside: $bad"; test -z "$bad"'`
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

Невыполнимо (чекер противоречит спеке, AC-002 конфликтует с AC-001) — остановись,
`report-blocked.md` в корне клона с командой, выводом и `file:line`. Менять
чекеры/спеку, выдумывать факты, глушить коды возврата (`|| true`, `set +e`),
пушить — запрещено.

## 10. Стыки

После приёмки постановщик публикует, переотправляет изменённые URL в IndexNow,
делает контрольный прогон SEO-чеклиста. Внешние упоминания бренда, реквизиты
ИП, юридический статус отзывов — решения владельца, вне вехи.
