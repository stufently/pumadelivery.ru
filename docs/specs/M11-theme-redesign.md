# Веха M11: новая тема сайта с нуля (mobile-first) и три страницы услуг из текста главной

- **Репозиторий:** `~/github/pumadelivery.ru` (статичный HTML, GitHub Pages из ветки `main`, без сборки).
- **Дата постановки:** 2026-10-10.
- **BASE_SHA:** `d507257f074c5a9e9978619a786daf68195f7200`
  (коммит «Add Telegram CTA to hero and floating button»; следующий коммит постановщика
  добавляет эту спеку, чекеры `docs/specs/check_theme.py`, `docs/specs/layout/*` и `.gitignore`).
- **Исполнитель:** Codex (`cx`).

## 1. Где работать

- Клон `/home/deploy/exec-clones/pumadelivery-theme-20261010`, новая ветка `m11-theme-redesign`.
- **Живое дерево `~/github/pumadelivery.ru` не трогать. push в origin запрещён** — работу
  заберёт постановщик через `git fetch` из клона.
- Docker — только под своим пользователем (`-u 1002:1002`, это делает `docs/specs/layout/run.sh`).

### Что кладёт постановщик ДО запуска

| Путь в клоне | Что | Версионируется |
|---|---|---|
| `docs/specs/layout/node_modules/` | `npm ci` по `package-lock.json` (playwright 1.64.0, lighthouse 13.5.0) | нет, в `.gitignore` |
| образ `mcr.microsoft.com/playwright:v1.64.0-noble` | Chromium 1248, Node 24 | — (на хосте) |

`tmp/` в корне клона — в `.gitignore`, туда пишутся скриншоты «после».

## 2. Задача и почему

Владелец (TG, 10.10.2026, скриншот мобильной главной): «вся вёрстка плывёт, сделай новую
тему с нуля…, проверь что всё хорошо с вёрсткой на мобиле и на десктопе, если надо вынеси
тексты в отдельные статьи для лучшего SEO».

Сейчас сайт — шаблон HTML5 UP (jQuery, `section#header` на 100vh с фото человека в шарфе).
Замер постановщика на проде (`tg-claude-userbot/tmp/pumadelivery-redesign/before/`, 10.10.2026):

- **Hero на телефоне — 1350 px из 844**: фото головы обрезано, h1 бледный, кнопки «Написать в
  Telegram» в первом экране НЕТ (она ниже первого экрана на 390×844).
- **Картинки `.image.fit` растянуты по высоте атрибута**: `pic01/02/03` рендерятся 358×1000 на
  390 px — «гигантская картинка на весь экран» сразу под hero; на главной 6 фото по ~1000 px.
- **Вес картинок**: `pic01.webp` 352 КБ, `pic03.webp` 219 КБ (сайт отдаёт их на всех страницах).
- **Плавающая `.tg-float`** (105×48) лежит поверх контента в первом экране (картинки) и поверх
  копирайта внизу страницы; у `body` нет отступа под неё.
- **Прелоадер шаблона** (`body.is-preload` + `body:after` оверлей со спиннером): первые ~1–2 с
  страница затемнена; на мобиле шаблон оборачивает body в `#wrapper` со своим скроллом (jQuery).
- Внешний шрифт Raleway через `@import` Google Fonts в `main.min.css`; `bundle.min.js` 100 КБ
  (jQuery + плагины ради скролла).
- Главная на 390 px — 14 300 px высоты (~17 экранов), статья — 34 000 px.
- Lighthouse mobile (локальный сервер, сторонние хосты заблокированы, медиана 3 прогонов):
  `index.html` perf 73 / a11y 93; `bangkok.html` 79 / 93; `blog/index.html` 84 / 92;
  `blog/posylka-iz-tailanda-v-rossiyu.html` 81 / 93. LCP главной 6,5 с.

Что делаем: **новая собственная тема** для всех 39 страниц (8 корневых, `blog/index.html`,
30 статей) — без jQuery и прелоадера, mobile-first, и **три страницы услуг** из длинных секций
главной (поиск поставщиков, поручения, постоплата/гарант) — у каждой свой поисковый запрос.

Что при этом СЛОМАЕТСЯ и обязано быть починено в этой же вехе: все 9 прежних чекеров
(`check_articles.py`, `check_m3…m10.py`) завязаны на строку подключения CSS, `bundle.min.js`,
FAQ = JSON-LD, таблицы `<div class="table-wrapper"><table>` — они обязаны остаться зелёными (AC-004).

## 3. Что проверено вживую, а что предположение

Проверено постановщиком 10.10.2026 (команды и вывод — в этом репо и в клоне):

- Деплой: GitHub Pages из ветки `main` (`CNAME` = `pumadelivery.ru`, `.nojekyll`, каталога
  `.github/workflows` нет) — любой push в `main` публикует сайт. Сборки нет.
- Страницы на BASE: `index, about, reviews, bangkok, pattaya, phuket, samui, phangan` + `blog/index.html`
  + 30 статей `blog/*.html`; `googled7273fa657395235.html`, `yandex_0f75ccd0b67f0ac1.html` — верификации (не трогать).
- Все 9 прежних чекеров на BASE дают rc=0 (`python3 docs/specs/check_articles.py --group all` и т. д.).
- `check_articles.py` (строки 20–23, 227–231) требует в статьях ДОСЛОВНО строку CSS
  `<link rel="preload" as="style" href="/assets/css/main.min.css" onload="this.onload=null;this.rel='stylesheet'"><noscript><link rel="stylesheet" href="/assets/css/main.min.css"></noscript>`
  и `<script defer src="/assets/js/bundle.min.js"></script>`, а других внешних `<script src>`,
  кроме gtag, в статьях быть не должно. Значит, **имена файлов `assets/css/main.min.css` и
  `assets/js/bundle.min.js` сохраняются**, меняется их содержимое.
- `check_articles.py` R-IMG: в каждой статье ≥1 `<img>` с `alt`, `width`, `height`,
  `loading="lazy"` и существующим файлом — картинку в статьях оставить (можно уменьшенную копию).
- `check_m6.py:66` режет тело статьи по `<section id="footer"` — если подвал статьи меняет разметку,
  проверь, что `check_m6.py` остаётся зелёным.
- Счётчики (на всех 38 страницах BASE, `check_articles.py` R-COUNTERS): GA4 `G-HHLE9R0EYW`
  (`gtag/js?id=G-HHLE9R0EYW`, `gtag('config','G-HHLE9R0EYW')`) и Яндекс Метрика `108157978`
  (`ym(108157978, "init"`, `<noscript>` с `mc.yandex.ru/watch/108157978`). Блоки переносить как есть.
- `https://geo.hqdthai.ru/v1/contact.js?v=20260907` (на 8 корневых страницах) — ванильный JS
  без jQuery, переписывает ссылки `t.me/kolesnikov1988` и `t.me/stufently` (добавляет текст
  сообщения). Оставить подключение; Telegram-ссылки — обычные `<a href="https://t.me/kolesnikov1988">`.
- Главная: секции `#about, #delivery, #russia, #wholesale, #errands, #guarantor, #cities, #faq,
  #contacts`; FAQ — 9 вопросов, видимый текст = JSON-LD `FAQPage` дословно (`check_m5.py`).
  Секции `#wholesale` (≈95 слов), `#errands` (≈80 слов), `#guarantor` (≈85 слов) — каждая
  самостоятельная услуга без своей страницы.
- Чекеры вехи прогнаны постановщиком: `check_theme.py` на BASE — 32 нарушения (нет страниц
  услуг, hero, бюджетов CSS/JS; все счётчики, head и тексты старых страниц — зелёные); тест
  перестройки FAQ главной в `<details><summary>` — R-TEXT зелёный, удаление абзаца — красный.
  `check_layout.mjs` на эталонной адаптивной странице — 0 нарушений; без отступа под
  плавающую кнопку — `R-FLOAT-OVERLAP`, со всегда скрытой кнопкой — `R-FLOAT-HIDDEN`.
- **Дизайн-скил.** У Codex на этом хосте плагина/скила фронтенд-дизайна нет (`~/.codex/skills`:
  `playwright`, `playwright-interactive`, `imagegen` и служебные; плагины `github`, `superpowers`,
  `codex-security`; удалённый `sites` — хостинг OpenAI, для нас НЕ годится). Есть Claude-плагин
  `frontend-design` (официальный маркетплейс) — его SKILL.md читается как файл, см. §4.
- Предположение: Lighthouse на локальном сервере с заблокированными сторонними хостами
  (GA, Метрика, geo.hqdthai.ru, шрифты Google) — прокси для реального PSI; на проде счётчики
  добавят своё.

## 4. Что сделать

### 4.0. Дизайн-скил — обязательно

1. ДО первой строчки CSS прочитай целиком
   `/home/deploy/.claude/plugins/marketplaces/claude-plugins-official/plugins/frontend-design/skills/frontend-design/SKILL.md`
   (скил `frontend-design` из Claude-плагина; у Codex своего нет) и следуй ему: собственное
   визуальное направление под тему «русскоязычный курьер в Таиланде», не шаблонные дефолты.
2. Визуальную проверку по ходу работы делай своим скилом `$playwright` (или
   `$playwright-interactive`) и командой из AC-002 — смотри PNG в `tmp/after/` глазами,
   а не только код возврата.
3. Решения запиши в `docs/specs/M11-design-notes.md` (до 60 строк): направление, палитра
   (контраст текста ≥ 4.5:1), шрифты, сетка и брейкпоинты, поведение кнопки Telegram, что
   именно взято из `frontend-design`. Первая строка файла — `# M11 design notes (frontend-design)`.

### 4.1. Тема (все 39 страниц)

- `assets/css/main.min.css` — новый CSS с нуля (≤ 40 КБ, без `@import`, без Google Fonts;
  системный стек шрифтов или свой woff2 в `assets/fonts/` с `font-display: swap`).
  Mobile-first: база под 360 px, расширение `min-width` медиазапросами; боковые поля ≥ 16 px;
  ни один блок, таблица или длинный URL не даёт горизонтального скролла (таблицы —
  прокрутка внутри `.table-wrapper`, `overflow-x: auto`).
- `assets/js/bundle.min.js` — ванильный JS ≤ 20 КБ (или почти пустой файл): без jQuery,
  без прелоадера, без `#wrapper`-скролла. Сайт обязан работать и без JS.
- **Hero** (`index.html`, 5 городов, 3 страницы услуг): элемент с атрибутом `data-hero`,
  внутри — единственный `h1`, подзаголовок и `<a data-cta="telegram" href="https://t.me/kolesnikov1988">Написать в Telegram</a>`;
  низ hero, h1 и кнопка — в пределах первого экрана на 360×800, 390×844, 768×1024, 1440×900.
  Без фото человека; картинка в hero необязательна.
- **Картинки**: каждый видимый `<img>` не шире вьюпорта и не выше 60 % его высоты; каждый
  файл, который отдаётся странице, ≤ 200 КБ. Новые уменьшенные копии — только в
  `images/theme/` (WebP, `srcset`/`sizes` по желанию); файлы `images/*` и `images/og/*` не
  менять и не удалять (на них ссылаются og:image и поисковики). У `<img>` — `width`/`height`.
- **Кнопка Telegram** `.tg-float` (ровно одна `<a class="tg-float" href="https://t.me/kolesnikov1988">`
  на каждой странице, высота ≤ 64 px): на телефоне видна в середине длинной страницы; не
  перекрывает ни текст, ни ссылки, ни картинки в первом экране и в самом низу страницы.
  Рабочая схема: скрывать, пока в кадре hero-кнопка (`IntersectionObserver`), и держать
  `padding-bottom` у `body`/подвала под её высоту.
- Сохранить на КАЖДОЙ странице без изменений: `<title>`, `meta description`, `canonical`,
  `og:*`, `twitter:*`, `robots`, `yandex-verification`, все блоки JSON-LD, `<html lang="ru">`,
  счётчики GA4 и Метрики, `contact.js` там, где он был, URL файла.
- Сохранить весь видимый текст каждой страницы (абзацы, пункты списков, заголовки, ячейки
  таблиц, FAQ) — разметку вокруг можно менять. Навигация/шапка/подвал — новые, но в подвале
  остаются контакты (Telegram `@kolesnikov1988`, `@stufently`, VK, почта).
- Шапка на всех страницах: логотип-текст «Puma Delivery» ссылкой на `/`, ссылки на 5 городов
  (на мобиле — компактно, без перекрытия контента), блог.

### 4.2. Главная: три секции → три страницы услуг

| Секция главной | Новая страница | h1 (предложение) |
|---|---|---|
| `#wholesale` «Поиск товаров и оптовых поставщиков» | `uslugi/poisk-postavshchikov-v-tailande.html` | Поиск товаров и оптовых поставщиков в Таиланде |
| `#errands` «Поручения и закупки» | `uslugi/porucheniya-i-zakupki-v-tailande.html` | Поручения и закупки в Таиланде |
| `#guarantor` «Постоплата и гарант» | `uslugi/postoplata-i-garant.html` | Постоплата и сделка через гаранта |

- На новой странице — ВСЕ абзацы и заголовок секции дословно (см. R-TEXT чекера), hero по §4.1,
  блок «Как заказать» с Telegram-кнопкой, ссылки на главную `href="/"`, ≥ 2 страницы городов,
  ≥ 1 подходящую статью блога. **Новых фактов не добавлять**: никаких цен, сроков, процентов,
  лет — чекер R-FACTS сверяет каждое число на странице с текстом главной на BASE.
- Head новой страницы: уникальный `title` 30–70 символов, одно `meta description` 110–170,
  `canonical` и `og:url` = `https://pumadelivery.ru/uslugi/<файл>`, `og:title`,
  `og:description`, `og:type`, `og:image` (существующий файл из `images/og/`), счётчики,
  JSON-LD `@graph`: `Service` с `provider` `{"@id": "https://pumadelivery.ru/#business"}` и
  `BreadcrumbList` «Главная → <услуга>».
- На главной вместо секции — короткая карточка: заголовок, 1–2 предложения (не копия абзацев
  ≥ 12 слов) и ссылка `href="/uslugi/<файл>"`. Остальные секции главной (о нас, доставка,
  Россия–Таиланд со всеми ссылками на статьи, города, FAQ, контакты) — на месте, текст дословно.
- `sitemap.xml`: три новые `<url>` (формат соседних, `lastmod` — дата работы); старые записи не удалять.
- `llms.txt`: три строки со ссылками в разделе «Города и услуги».

## 5. Не трогать

`docs/specs/check_*.py`, `docs/specs/facts-*.md`, прежние спеки `docs/specs/M1…M10-*`,
чекеры этой вехи `docs/specs/check_theme.py` и `docs/specs/layout/*` (кроме `node_modules/`),
`docs/CHANGELOG.md` (запишет постановщик), `CNAME`, `.nojekyll`, `robots.txt`,
`googled7273fa657395235.html`, `yandex_0f75ccd0b67f0ac1.html`, `c0afba6d576141c4eefefffef8346192.txt`,
`favicon-120x120.png`, `images/*` и `images/og/*` (только добавлять в `images/theme/`),
`imagesold/`, `LICENSE.txt`, `README*`, head-разметку SEO и JSON-LD любой существующей страницы.
Исключение: эта спека приехала коммитом постановщика — её не править.

## 6. Разрешения

Коммиты в клоне — да (тема ≤ 50 символов, imperative, без подписей и Co-Authored-By).
Разрешённые пути от BASE_SHA: 8 корневых страниц, `blog/*.html`, три файла `uslugi/*.html`
из §4.2, всё под `assets/` (в том числе удаление старых `assets/sass/`, `assets/webfonts/`,
`assets/css/main.css`, `assets/css/fontawesome-all.min.css`, `assets/css/images/`,
`assets/js/*.js`, кроме `bundle.min.js`, если на них больше никто не ссылается), новые файлы
`images/theme/*`, `sitemap.xml`, `llms.txt`, `docs/specs/M11-design-notes.md` и файлы коммита
постановщика (`docs/specs/M11-theme-redesign.md`, `docs/specs/check_theme.py`,
`docs/specs/layout/*`, `.gitignore`). Docker — только через `docs/specs/layout/run.sh`.
`npm install`/обновление `package-lock.json` — запрещено.

## 6a. Авторевью

Не вызывать (`review_run.sh` не запускать): ревью координатор проводит вручную.

## 7. Критерии приёмки

Команды запускаются из корня клона.

- **AC-001 — статические правила темы и страниц услуг.** Команда: `bash -c 'python3 docs/specs/check_theme.py'`
- **AC-002 — вёрстка в браузере на 360, 390, 768 и 1440, скриншоты после.** Команда: `bash -c 'bash docs/specs/layout/run.sh check_layout.mjs --shots /site/tmp/after --require-hero index.html,bangkok.html,pattaya.html,phuket.html,samui.html,phangan.html,uslugi/poisk-postavshchikov-v-tailande.html,uslugi/porucheniya-i-zakupki-v-tailande.html,uslugi/postoplata-i-garant.html && test -s tmp/after/index-390-first.png && test -s tmp/after/index-1440-first.png'`
- **AC-003 — Lighthouse mobile: производительность от 90, доступность от 95.** Команда: `bash -c 'bash docs/specs/layout/run.sh lighthouse.mjs --pages index.html,bangkok.html,blog/index.html,blog/posylka-iz-tailanda-v-rossiyu.html,uslugi/poisk-postavshchikov-v-tailande.html --min-perf 90 --min-a11y 95 --runs 3'`
- **AC-004 — прежние чекеры зелёные.** Команда: `bash -c 'python3 docs/specs/check_articles.py --group all && python3 docs/specs/check_m3.py && python3 docs/specs/check_m4.py && python3 docs/specs/check_m5.py && python3 docs/specs/check_m6.py --group ru-th && python3 docs/specs/check_m6.py --group th-ru && python3 docs/specs/check_m8.py && python3 docs/specs/check_m9.py && python3 docs/specs/check_m10.py'`
- **AC-005 — заметки дизайна по скилу на месте.** Команда: `bash -c 'test "$(head -1 docs/specs/M11-design-notes.md)" = "# M11 design notes (frontend-design)" && test "$(wc -l < docs/specs/M11-design-notes.md)" -le 60'`
- **AC-006 — чекеры и пакеты фактов не изменены.** Команда: `bash -c 'test "$(git log --format=%H d507257f074c5a9e9978619a786daf68195f7200..HEAD -- docs/specs/M11-theme-redesign.md docs/specs/check_theme.py docs/specs/layout .gitignore | wc -l)" -eq 1 && test -z "$(git diff --name-only d507257f074c5a9e9978619a786daf68195f7200 HEAD -- docs/specs/check_articles.py docs/specs/check_m3.py docs/specs/check_m4.py docs/specs/check_m5.py docs/specs/check_m6.py docs/specs/check_m8.py docs/specs/check_m9.py docs/specs/check_m10.py docs/specs/facts-delivery-demand.md docs/specs/facts-m10.md docs/specs/facts-m6-m7.md docs/specs/facts-m8.md docs/specs/facts-m9.md)"'`
- **AC-007 — изменения только в разрешённых путях.** Команда: `bash -c 'd=$(git diff --name-only d507257f074c5a9e9978619a786daf68195f7200 HEAD) || exit 1; test -n "$d" || exit 1; bad=$(printf "%s\n" "$d" | grep -vxE "(index|about|reviews|bangkok|pattaya|phuket|samui|phangan)\.html|blog/[a-z0-9-]+\.html|uslugi/(poisk-postavshchikov-v-tailande|porucheniya-i-zakupki-v-tailande|postoplata-i-garant)\.html|assets/.+|images/theme/[A-Za-z0-9._-]+|sitemap\.xml|llms\.txt|\.gitignore|docs/specs/(M11-theme-redesign\.md|M11-design-notes\.md|check_theme\.py)|docs/specs/layout/(check_layout\.mjs|lighthouse\.mjs|serve\.mjs|run\.sh|package\.json|package-lock\.json)"); echo "outside: $bad"; test -z "$bad"'`
- **AC-008 — рабочее дерево чистое.** Команда: `bash -c 'test -z "$(git status --porcelain --untracked-files=all -- . ":(exclude)report.json" ":(exclude)report-blocked.md")"'`

Работу доказывают AC-001…AC-003 и AC-005 (на BASE красные); AC-004, AC-006…AC-008 — охранные.

## 8. Контракт отчёта

`report.json` в корне клона, untracked, ровно 8 записей AC-001…AC-008.
`blocked` — когда среда не даёт выполнить критерий (нет Docker, образа, сети к npm-кэшу):
`"rc": null`, дословная ошибка в `note`. Обходить несовместимость запрещено.

```json
{"criteria": [{"id": "AC-001", "status": "pass|fail|blocked",
               "command": "<команда ИЗ ЭТОЙ СПЕКИ, посимвольно>", "rc": 0, "note": "…"}]}
```

## 9. Контракт на невыполнимое

Невыполнимо (чекер противоречит спеке или прежнему чекеру, порог Lighthouse недостижим на
пустой странице, правило hero несовместимо с длинным h1 города на 360 px и т. п.) —
остановись, `report-blocked.md` в корне клона: команда, вывод, `file:line`, что пробовал.
Менять чекеры, пороги, списки страниц и спеку, глушить коды возврата (`|| true`, `set +e`),
выдумывать факты, `git push` — запрещено.

## 10. Стыки

После приёмки постановщик: смотрит скриншоты `tmp/after/` глазами (390 и 1440), гоняет
мутации чекеров противоположным исполнителем, пишет `docs/CHANGELOG.md`, публикует (push в
`main` = деплой Pages), проверяет прод тем же `check_layout.mjs --base-url https://pumadelivery.ru`,
отправляет новые URL в IndexNow/Яндекс/Bing. Расширение страниц услуг фактами (цены, кейсы) —
отдельная веха после пакета фактов от владельца: сейчас в них ≈ 80–100 слов перенесённого текста.
