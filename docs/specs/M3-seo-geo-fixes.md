# Веха M3: правки по SEO/GEO-аудиту pumadelivery.ru

- **Репозиторий:** `~/github/pumadelivery.ru` (GitHub Pages, статичный HTML, без сборки).
- **Дата постановки:** 2026-09-28.
- **BASE_SHA:** `94ed0833d09c5a45e28ba0d3d60bc4fd6b54f4cc`
  (коммит «Fix three review findings in articles»; следующий за ним коммит
  постановщика добавляет эту спеку и чекер `docs/specs/check_m3.py`).
- **Исполнитель:** Codex (`cx`) — выбор владельца («исправь все находки аудита
  кодексом»). Тестов исполнитель не пишет, проверка — готовый чекер постановщика.
- **Ревью:** дифф вехи больше лимита обёртки ревью (100 КБ), поэтому
  перекрёстное ревью проводит координатор вручную после сдачи. `review_run.sh`
  в этой вехе НЕ вызывать.

## 1. Где работать

- Клон: `/home/deploy/exec-clones/pumadelivery-m3-20260928`, ветка `m3-seo-geo-fixes`.
- **Живое дерево `~/github/pumadelivery.ru` не трогать.**
- **`git push` в `origin` ЗАПРЕЩЁН.** Работу заберёт постановщик через `git fetch`.
- Команды критериев — из корня клона; нужен только `python3` (stdlib) и `git`.
  Docker, сеть и установка пакетов не нужны.

## 2. Задача и почему

Аудит живого сайта 2026-09-28: механических SEO-ошибок нет (35/35 URL — 200,
canonical, title/description, robots, sitemap, soft-404 — чисто), ИИ-краулеры
допущены, `llms.txt` полный. Остались смысловые дыры в разметке и
перелинковке, которые мешают поисковикам и ИИ-ассистентам собрать сущность
бренда и связать статьи с услугой:

1. `LocalBusiness #business` и `Organization #org` на главной не связаны.
2. Нет отдельной услуги «передачи Россия ⇄ Таиланд через пилотов» в разметке —
   19 новых статей не на что сослаться.
3. На 5 страницах городов `Service` без `@id`, а `provider` — вложенная копия
   бизнеса вместо ссылки на `#business`; нет `BreadcrumbList`.
4. `reviews.html`: `reviewBody` в JSON-LD расходится с видимым текстом
   (точки перед «»», опечатка «сывороктами» / «сывороткой» → правильно
   «сыворотками»).
5. Подпись автора в статьях — просто текст, без ссылки на страницу автора
   (E-E-A-T); у 7 старых статей подписи нет вовсе.
6. 7 старых статей: нет `BreadcrumbList` и ни одной ссылки на 19 новых
   статей (новые страницы без входящих ссылок из старого контента).
7. У одной новой статьи вступление 87 слов (для цитирования ИИ — 40–80).

## 3. Что проверено вживую, а что предположение

Проверено постановщиком 2026-09-28 (чтением файлов и прогоном чекера):

- `index.html`: JSON-LD `@graph` с `Organization` (`@id` `https://pumadelivery.ru/#org`),
  `LocalBusiness` (`@id` `https://pumadelivery.ru/#business`, есть `areaServed`,
  `address` только с `addressCountry: TH`, `founder`), `FAQPage`.
- `bangkok.html` (и так же `pattaya`, `phuket`, `samui`, `phangan`): `@graph` с
  `Service` (`name`, `description`, `provider: {"@type":"LocalBusiness","name":…,"url":…}`,
  `areaServed: City`, `serviceType`) и `FAQPage`; `@id` у Service нет.
- `about.html`: `Person` `@id` `https://pumadelivery.ru/about.html#dmitry` — существует.
- `reviews.html`: один JSON-LD-объект `LocalBusiness #business` с
  `aggregateRating` и массивом `review` из 10 `Review`; видимые отзывы — абзацы
  вида `<p>«…»</p>`. Первый отзыв: JSON «сывороктами», видимый «сывороткой».
- 19 новых статей (`docs/specs/check_articles.py`, `GROUPS`): в `section#header`
  строка `<p>Дмитрий Колесников · обновлено 28.09.2026</p>`; `Article` без `about`.
  Вступление — первый `<p>` в `div.content`.
- 7 старых статей (`OLD_ARTICLES` в том же файле): `Article` + `FAQPage`,
  `datePublished`/`dateModified` 2026-05-20, подписи автора в шапке нет.
- `python3 docs/specs/check_m3.py` на BASE_SHA падает: R-ABOUT ×19, R-BIZ,
  R-BYLINE ×26, R-CITY ×10, R-CITY-BC ×5, R-INTRO ×1, R-OLD-BC ×7,
  R-OLD-DATE ×14, R-OLD-LINKS ×7, R-REVIEWS ×11, R-SERVICE-RT.
  `python3 docs/specs/check_articles.py --group all` на BASE_SHA — `OK`.

Предположений в спеке нет. Физический адрес бизнеса, телефон, карточки в
Яндекс Бизнесе / Google Business — **не выдумывать и не добавлять** (решает
владелец).

## 4. Что сделать

### 4.1 `index.html` — JSON-LD

- В узел `@id: https://pumadelivery.ru/#business` добавить
  `"parentOrganization": {"@id": "https://pumadelivery.ru/#org"}`.
- В тот же `@graph` добавить узел:
  `"@type": "Service"`, `"@id": "https://pumadelivery.ru/#service-russia-thailand"`,
  `"name": "Передачи Россия — Таиланд через пилотов и стюардесс"`, `description`
  (1–2 предложения: небольшие личные посылки, документы, лекарства в обе стороны
  через пилотов и стюардесс, курьер по Таиланду), `"provider": {"@id": "https://pumadelivery.ru/#business"}`,
  `"areaServed": [{"@type": "Country", "name": "Россия"}, {"@type": "Country", "name": "Таиланд"}]`,
  `"serviceType": "Передача посылок и документов"`,
  `"url": "https://pumadelivery.ru/#russia"` (секция «Передачи Россия–Таиланд»
  в `index.html` — `<section id="russia">`, проверено).

### 4.2 Страницы городов (`bangkok`, `pattaya`, `phuket`, `samui`, `phangan`)

- У `Service` добавить `"@id": "https://pumadelivery.ru/<город>.html#service"`;
  `provider` заменить на ровно `{"@id": "https://pumadelivery.ru/#business"}`.
- В `@graph` добавить `BreadcrumbList`: 1 — `https://pumadelivery.ru/` («Главная»),
  2 — `https://pumadelivery.ru/<город>.html` (название из `h1`).

### 4.3 `reviews.html`

- Каждый `reviewBody` — дословно текст соответствующего видимого отзыва внутри
  «…» (та же пунктуация; сравнение после схлопывания пробелов).
- Исправить опечатку в обоих местах: «с дорогими сыворотками».
- Рейтинг, авторов, даты, число отзывов — не менять.

### 4.4 Все 26 статей блога (19 новых + 7 старых)

- В `section#header` подпись автора ссылкой: `<a href="/about.html#dmitry">Дмитрий Колесников</a>`.
  У новых статей заменить текст имени в существующей строке; у старых —
  добавить строку `<p><a href="/about.html#dmitry">Дмитрий Колесников</a> · обновлено 28.09.2026</p>`
  после существующего подзаголовка.

### 4.5 19 новых статей

- `Article` в JSON-LD: добавить `"about": {"@id": "https://pumadelivery.ru/#service-russia-thailand"}`.
- Первый `<p>` в `div.content` — 40–85 слов (сейчас вне диапазона только
  `blog/tajskie-lekarstva-v-rossiyu.html`; сократи, не теряя смысла).

### 4.6 7 старых статей

- `BreadcrumbList` в `@graph`: Главная → Блог (`https://pumadelivery.ru/blog/`) →
  статья (её canonical).
- В тексте — 1–3 уместные контекстные ссылки на новые статьи (в существующий
  абзац или новый короткий абзац по теме): `receptury-lekarstva-turistu` →
  `lekarstva-iz-rossii-v-tailand`, `tajskie-lekarstva-v-rossiyu`;
  `chto-nelzya-vvozit-v-tailand` → `lekarstva-iz-rossii-v-tailand`,
  `russkie-produkty-v-tailand`; `kak-zakazat-s-lazada-v-tailande` и
  `lazada-vs-shopee` → `vykup-lazada-shopee-s-dostavkoj-v-rossiyu`;
  `dostavka-alkogolya-v-tailande` → `chaj-med-specii-iz-rossii-v-tailand` или
  `russkie-produkty-v-tailand`; `perevozka-mezhdu-gorodami-tailanda` →
  `lichnye-veshchi-iz-rossii-v-tailand`, `dokumenty-iz-rossii-v-tailand`;
  `tajskaya-bankovskaya-karta-2026` → `dokumenty-iz-rossii-v-tailand`.
- `Article.dateModified` → `2026-09-28`; в `sitemap.xml` `lastmod` этих 7 URL →
  `2026-09-28` (остальные строки sitemap не менять).
- Текст старых статей в остальном не переписывать.

## 5. Не трогать

- `about.html`, `blog/index.html`, `llms.txt`, `robots.txt`, `CNAME`, `assets/`,
  `images/`, файлы верификации.
- `docs/specs/check_m3.py`, `docs/specs/check_articles.py`,
  `docs/specs/facts-delivery-demand.md`, эту и прочие спеки — не менять
  (sha256 проверяет AC-003).
- Видимый текст новых статей — только п. 4.4 и 4.5. Цифр, адресов, телефонов,
  цен не добавлять. `.github/` не создавать.

## 6. Разрешения

Коммиты в клоне — да (тема ≤50 символов, imperative, без подписей и
Co-Authored-By). Разрешённые пути от BASE_SHA: `index.html`, пять страниц
городов, `reviews.html`, `sitemap.xml`, 26 статей `blog/<slug>.html` и
закоммиченные постановщиком `docs/specs/M3-seo-geo-fixes.md`, `docs/specs/check_m3.py`.

## 7. Критерии приёмки

Каждая команда возвращает 0 ТОЛЬКО когда критерий выполнен.

- **AC-001 — все правки аудита на месте.** Команда: `bash -c 'python3 docs/specs/check_m3.py'`
- **AC-002 — статьи по-прежнему проходят чекер статей.** Команда: `bash -c 'python3 docs/specs/check_articles.py --group all'`
- **AC-003 — чекеры и пакет фактов не изменены.** Команда: `bash -c 'test -z "$(git diff --name-only 94ed0833d09c5a45e28ba0d3d60bc4fd6b54f4cc HEAD -- docs/specs/check_articles.py docs/specs/facts-delivery-demand.md)" && test "$(git log --format=%H -- docs/specs/check_m3.py | wc -l)" = 1'`
- **AC-004 — изменения только в разрешённых путях.** Команда: `bash -c 'd=$(git diff --name-only 94ed0833d09c5a45e28ba0d3d60bc4fd6b54f4cc..HEAD) || exit 1; test -n "$d" || exit 1; bad=$(printf "%s\n" "$d" | grep -vxE "index\.html|(bangkok|pattaya|phuket|samui|phangan)\.html|reviews\.html|sitemap\.xml|blog/[a-z0-9-]+\.html|docs/specs/M3-seo-geo-fixes\.md|docs/specs/check_m3\.py" | grep -vx "blog/index.html"); inx=$(printf "%s\n" "$d" | grep -x "blog/index.html"); echo "outside: $bad $inx"; test -z "$bad$inx"'`
- **AC-005 — рабочее дерево чистое.** Команда: `bash -c 'test -z "$(git status --porcelain --untracked-files=all -- . ":(exclude)report.json" ":(exclude)report-blocked.md" ":(exclude)docs/specs/__pycache__")"'`

Критериев: 5. Работу доказывает AC-001 (до работы красный). AC-002…AC-005 —
охранные, зелёные на свежем клоне (проверено постановщиком) и обязаны
остаться зелёными.

## 8. Контракт отчёта

`report.json` в КОРНЕ клона, untracked. Ровно 5 записей: AC-001…AC-005.
`blocked` — когда среда не даёт выполнить критерий: `"rc": null` и дословная
ошибка в `note`. Обходить несовместимость запрещено.

```json
{"criteria": [{"id": "AC-001", "status": "pass|fail|blocked",
               "command": "<команда ИЗ ЭТОЙ СПЕКИ, посимвольно>", "rc": 0, "note": "…"}]}
```

## 9. Контракт на невыполнимое

Если требование невыполнимо (чекер противоречит спеке, структура файла не
такая, как в §3) — **остановись и доложи**: `report-blocked.md` в корне клона
с командой, выводом и `file:line`. Менять чекеры и спеку, выдумывать факты,
глушить коды возврата (`|| true`, `; true`, `set +e`), пушить — запрещено.

## 10. Стыки

После приёмки постановщик публикует, переотправляет изменённые URL в
IndexNow и Яндекс, делает контрольный прогон SEO-чеклиста. Карточки в
Яндекс Бизнесе / Google Business и адрес — решение владельца, вне вехи.
