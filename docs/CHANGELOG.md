# CHANGELOG pumadelivery.ru

## 2026-09-28

### Добавлено
- 19 статей о передачах через пилотов и стюардесс: 9 «Россия → Таиланд», 10 «Таиланд → Россия» (спеки `docs/specs/M1-*`, `M2-*`), карточки в блоге, `sitemap.xml`, `llms.txt`, ссылки с главной.
- Блок «Седжаро (Sejaro)» в `blog/lekarstva-iz-rossii-v-tailand.html` (M4).
- Статьи `blog/pochta-rossii-i-ems-v-tailand.html` (цены Почты России и EMS на 28.09.2026) и `blog/mestnye-sluzhby-dostavki-v-tailande.html` (Thailand Post, KEX, Flash, J&T и др.) (M9).
- Во все 26 статей: таблица правил, h2-вопрос с прямым ответом, «Частые ошибки», ссылка на официальный первоисточник (M6–M8).
- Чекеры `docs/specs/check_*.py` и пакеты фактов `docs/specs/facts-*.md`.

### Изменено
- SEO/GEO-аудит (M3): связи JSON-LD (`#business`→`#org`, Service, города), подпись автора ссылкой, `Article.about`, хлебные крошки, внутренние ссылки.
- FAQ на 13 страницах: видимый текст = JSON-LD дословно (M5); убран `aggregateRating` из `reviews.html` (M6).
- Мобильная шапка статей (`body.is-article`, `assets/css/main.min.css`).
- Tesco Lotus → Lotus's.

### Исправлено
- Сломанная загрузка CSS на всех страницах (экранированные кавычки в `onload`).
- Устаревшие факты: часы продажи алкоголя 11:00–24:00 с 29.05.2026, закрытые дьюти-фри на прилёте, каннабис (контролируемый с 23.06.2025), кратом; лимиты еды Thai FDA по группам; правила ввоза психотропных (IC-2); Thailand Privilege 650 000 бат, безвиз 30 дней, банки и DTV; маршруты Lomprayah/Raja Ferry; JD Central, KEX Express, возвраты LazMall/Shopee Mall (M5, M8).
- Удалены непроверенные цены и проценты и рискованные советы (посредники для банковских счетов) в старых статьях (M8).
- Якорь `about.html#dmitry` для подписи автора.
