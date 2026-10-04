# Веха M10: статья «Если нужно очень дёшево из Таиланда в Россию: почта Таиланда и EMS»

- **Репозиторий:** `~/github/pumadelivery.ru` (статичный HTML, GitHub Pages, без сборки).
- **Дата постановки:** 2026-10-04.
- **BASE_SHA:** `05e93df4e7424b8a21f0e7f9d1b83b97b1c2f64e`
  (коммит «Add cheap-delivery blocks and Kerry to titles»; два следующих коммита
  постановщика добавляют и правят по ревью эту спеку `docs/specs/M10-thailand-post-to-russia.md`,
  чекер `docs/specs/check_m10.py` и пакет фактов `docs/specs/facts-m10.md`).
- **Исполнитель:** Codex (`cx`).

## 1. Где работать

- Клон `/home/deploy/exec-clones/pumadelivery-m10-20261004`, ветка `m10-thailand-post-to-russia`.
- **Живое дерево не трогать. `git push` запрещён** — постановщик заберёт через `git fetch`.
- Нужен только `python3` (stdlib) и `git`; сеть не нужна.

## 2. Задача и почему

Владелец (2026-10-04): «не вижу статью про … EMS почта из России в Тай и
обратно»; заголовок — «что-то вроде: если надо очень дёшево». Статья про
Россию → Таиланд уже есть (`blog/pochta-rossii-i-ems-v-tailand.html`, M9);
нужна обратная: как очень дёшево отправить посылку из Таиланда в Россию почтой
Таиланда (ePacket, авиапосылка) и EMS World, с ценами 2026 года.

## 3. Что проверено вживую, а что предположение

- **Все цифры — только `docs/specs/facts-m10.md`** (тарифы — официальный
  калькулятор Thailand Post, перепроверены постановщиком 04.10.2026; строки
  ВТОРИЧНО/НЕ НАЙДЕНО соблюдать как написано).
- Шаблон статьи (проверено чтением): `blog/pochta-rossii-i-ems-v-tailand.html`
  — head (title, description, canonical, OG/Twitter, CSS-строка, JSON-LD
  `@graph` с Article, BreadcrumbList, FAQPage), `section#header`, `div.content`,
  подвал. Базовые требования — те же, что проверяет `check_articles.py`
  (title 30–70, description 110–170, h2 ≥5, FAQ 5–8 вопросов дословно видимых,
  ссылки на Telegram, `/blog/`, ≥2 города, старую статью блога, картинка с
  alt/width/height/lazy, баланс тегов, без дублей абзацев с другими статьями).
- `Article`: `datePublished` и `dateModified` = `2026-10-04`, author/publisher
  `@id` как в соседних статьях, `inLanguage` `ru-RU`; OG-картинка — `https://pumadelivery.ru/images/og/customs.jpg` (полный URL, как в соседних статьях).
- Предположение (Вордстат не снимался): ключи «посылка из Таиланда в Россию»,
  «отправить посылку из Тайланда в Россию», «почта Таиланда в Россию», «EMS из
  Таиланда», «сколько стоит посылка из Таиланда в Россию».
- Чекер `check_m10.py` на BASE даёт 6 нарушений (статьи ещё нет).

## 4. Что сделать

### Статья — `blog/posylka-iz-tailanda-v-rossiyu.html`

- **title:** `Дёшево из Таиланда в Россию: почта Таиланда и EMS, цены 2026`
  (= Article.headline, og:title, имя третьей крошки).
- **h1:** `Если нужно очень дёшево из Таиланда в Россию: почта и EMS`.
- Пиши «Таиланд»; допускается одно «из Тайланда» в тексте как пользовательское написание.
- Вступление 40–85 слов с прямым ответом: до 2 кг самый дешёвый — Small Packet
  без трека (460 бат за 0,5 кг), с треком — ePacket (535 бат за 0,5 кг); от 2 кг
  дешевле авиапосылка; EMS — быстрее и до 30 кг; срочное и ценное — к нам.
- Таблица цен — ровно по §B, в `<div class="table-wrapper"><table>` с `<thead>`;
  столбцы в порядке: «Вес | EMS World | Авиапосылка | ePacket | Small Packet»;
  в `<tbody>` 7 строк, первая ячейка дословно `0,5 кг`, `1 кг`, `2 кг`, `5 кг`,
  `10 кг`, `20 кг`, `30 кг`; цены — числом как в пакете (`1 840`, обычный пробел,
  без «бат» в ячейке); нет услуги или «не принимается» — ячейка `—` (длинное тире). Чекер сверяет
  каждую ячейку (R10-RATES). Подпись «цены в батах на 4 октября 2026 года,
  калькулятор Thailand Post» и ссылка на `https://www.thailandpost.co.th/`.
- Вторая таблица: сравнение ePacket / авиапосылка / EMS World / передача с пилотом
  (максимальный вес, габариты, отслеживание, компенсация, где получать в России)
  — для нас без цен.
- h2-вопросы (≥2): «Сколько стоит отправить посылку из Таиланда в Россию?»,
  «Сколько идёт посылка из Таиланда в Россию?», «Принимает ли почта Таиланда
  посылки в Россию?» — прямой ответ первым абзацем, формулировки строго по §A и §C.
  Любой диапазон дней/недель («4–9 дней») пиши ТОЛЬКО в предложении, где есть
  слово «Европа»/«Европы» (чекер ловит диапазон сроков без него во всём тексте,
  включая FAQ); для России — «срок не нормирован».
- Как отправить по шагам: отделение Thailand Post, паспорт, бланк (ป.256 / ป.180 /
  CN22-CN23 по §F), упаковка, что показать сотруднику, трек, отслеживание на
  `https://track.thailandpost.co.th/` и `https://www.pochta.ru/tracking`.
- Таможня в России: 200 евро и 31 кг, 15% / 2 евро за кг — со ссылкой на
  `customs.gov.ru` (URL из «Ссылок» пакета).
- Что не примут и что опасно слать почтой: §E + лекарства, фрукты — фразы-ссылки
  на `/blog/tajskie-lekarstva-v-rossiyu.html` и `/blog/frukty-iz-tailanda-v-rossiyu.html`.
- Альтернативы по §G: DHL/FedEx/UPS приостановлены (можно со ссылками на
  `https://www.dhl.com/`, `https://dhlexpress.ee/`, `https://www.fedex.com/`,
  `https://www.ups.com/`), CDEK Forward — только как в пакете.
- «Частые ошибки» (4–6 пунктов, h2 со словом «ошибки»).
- Когда почта не подходит: срочно, документы, лекарства, ценное — передача через
  пилотов и стюардесс, Telegram; наши курьеры в городах (≥2 ссылки на страницы городов).
- Ссылки на обе статьи M9: `/blog/pochta-rossii-i-ems-v-tailand.html` (обратное
  направление) и `/blog/mestnye-sluzhby-dostavki-v-tailande.html` (по Таиланду).
- Ссылка на ≥1 старую статью блога из `OLD_ARTICLES` чекера `check_articles.py`
  (например, `/blog/kak-zakazat-s-lazada-v-tailande.html` или `/blog/chto-nelzya-vvozit-v-tailand.html`).
- FAQ 6–8 вопросов (JSON-LD = видимый текст дословно).

### Интеграция

- Карточка в `blog/index.html` — в раздел «Из Таиланда в Россию», первой (формат соседних).
- `sitemap.xml`: строка с `<lastmod>2026-10-04</lastmod>` (формат соседних).
- `llms.txt`: строка со ссылкой и описанием рядом со статьями «Из Таиланда в Россию».
- Входящие ссылки: из ≥3 существующих статей блога по смыслу, обязательно из
  `blog/pochta-rossii-i-ems-v-tailand.html` (фраза про обратное направление), плюс,
  например, косметика, чай/кофе/соусы, муай-тай, выкуп Lazada/Shopee. Одна
  фраза-ссылка в подходящий абзац, не ломая FAQ, структуру и даты чужих статей.

## 5. Не трогать

`index.html` (главную постановщик обновит сам), страницы городов, `about.html`,
`reviews.html`, CSS/JS, картинки, `robots.txt`, чекеры и пакеты фактов,
`datePublished`/`dateModified` и `lastmod` существующих статей. Существующие
статьи — только добавить фразу-ссылку.

## 6. Разрешения

Коммиты в клоне — да (тема ≤50 символов, imperative, без подписей и
Co-Authored-By). Разрешённые пути от BASE_SHA: новая статья, существующие
`blog/*.html` (только фраза-ссылка), `blog/index.html`, `sitemap.xml`,
`llms.txt` и закоммиченные постановщиком `docs/specs/M10-thailand-post-to-russia.md`,
`docs/specs/check_m10.py`, `docs/specs/facts-m10.md`.

## 6a. Авторевью

Не вызывать (`review_run.sh` не запускать): ревью координатор проводит вручную.

## 7. Критерии приёмки

- **AC-001 — статья на месте и интегрирована.** Команда: `bash -c 'python3 docs/specs/check_m10.py'`
- **AC-002 — прежние чекеры зелёные.** Команда: `bash -c 'python3 docs/specs/check_articles.py --group all && python3 docs/specs/check_m3.py && python3 docs/specs/check_m4.py && python3 docs/specs/check_m5.py && python3 docs/specs/check_m6.py --group ru-th && python3 docs/specs/check_m6.py --group th-ru && python3 docs/specs/check_m8.py && python3 docs/specs/check_m9.py'`
- **AC-003 — чекеры и пакеты фактов не изменены.** Команда: `bash -c 'd=$(git diff --name-only 05e93df4e7424b8a21f0e7f9d1b83b97b1c2f64e..HEAD -- docs/specs/check_articles.py docs/specs/check_m3.py docs/specs/check_m4.py docs/specs/check_m5.py docs/specs/check_m6.py docs/specs/check_m8.py docs/specs/check_m9.py docs/specs/facts-m9.md) || exit 1; e=$(git log --format=%h 05e93df4e7424b8a21f0e7f9d1b83b97b1c2f64e..HEAD -- docs/specs/check_m10.py docs/specs/facts-m10.md | wc -l) || exit 1; test -z "$d" && test "$e" -eq 2'`
- **AC-004 — изменения только в разрешённых путях.** Команда: `bash -c 'd=$(git diff --name-only 05e93df4e7424b8a21f0e7f9d1b83b97b1c2f64e..HEAD) || exit 1; test -n "$d" || exit 1; bad=$(printf "%s\n" "$d" | grep -vxE "blog/[a-z0-9-]+\.html|sitemap\.xml|llms\.txt|docs/specs/M10-thailand-post-to-russia\.md|docs/specs/check_m10\.py|docs/specs/facts-m10\.md"); echo "outside: $bad"; test -z "$bad"'`
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

Невыполнимо (чекер противоречит спеке, нужного факта нет в пакете) —
остановись, `report-blocked.md` в корне клона с командой, выводом и `file:line`.
Выдумывать цены, сроки и истории клиентов, менять чекеры/спеку/пакеты фактов,
глушить коды возврата, пушить — запрещено.

## 10. Стыки

После приёмки постановщик ревьюит текст, добавляет ссылку на главную (блок
«Если нужно очень дёшево и не срочно» в «Передачи Россия–Таиланд»), публикует,
отправляет URL в IndexNow, Яндекс, Bing и карту в Google.
