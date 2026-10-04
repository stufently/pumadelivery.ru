#!/usr/bin/env python3
"""Проверка вехи M10: статья «Посылка из Таиланда в Россию: почта Таиланда и EMS».

Запуск из корня репо: python3 docs/specs/check_m10.py
Базовые правила статьи — из check_articles.py (группа th-ru подменяется на M10,
дата — 2026-10-04, список внешних доменов расширен, правило «соседняя статья
той же вехи» заменено на ссылки на обе статьи M9); сверху — правила M10.
FAIL <правило>: <файл>: <деталь>, rc=1 если есть хоть одно. Только stdlib.
"""
import html
import io
import os
import re
import sys
from contextlib import redirect_stderr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_articles as ca  # noqa: E402

SLUG = "posylka-iz-tailanda-v-rossiyu"
DATE = "2026-10-04"
REQUIRED = ["Thailand Post", "EMS", "ePacket", "535", "2 020", "1 580", "22 330", "200 евро", "31 кг",
            "4 октября 2026", "Почт", "track.thailandpost.co.th"]
M9_SIBLINGS = ["/blog/pochta-rossii-i-ems-v-tailand.html", "/blog/mestnye-sluzhby-dostavki-v-tailande.html"]
EXTRA_EXT = [
    "https://www.thailandpost.co.th/", "https://file.thailandpost.com/", "https://international.thailandpost.com/",
    "https://track.thailandpost.co.th/", "https://dpostinter.thailandpost.com/", "https://www.pochta.ru/", "https://global.cdek.ru/",
    "https://www.dhl.com/", "https://dhlexpress.ee/", "https://www.fedex.com/", "https://www.ups.com/",
]
# строки большой таблицы: вес → EMS World, авиапосылка, ePacket, Small Packet (facts-m10.md §B)
RATES = {
    "0,5 кг": ["1 840", "1 580", "535", "460"],
    "1 кг": ["2 020", "1 580", "1 045", "890"],
    "2 кг": ["2 420", "2 010", "2 070", "1 770"],
    "5 кг": ["4 730", "3 600", "—", "—"],
    "10 кг": ["8 210", "6 600", "—", "—"],
    "20 кг": ["16 150", "12 600", "—", "—"],
    "30 кг": ["22 330", "—", "—", "—"],
}
FORBID = [
    r"без\s+ограничени",
    r"cdek-th",
    r"(DHL|FedEx|UPS)[^.<]{0,60}(?<!не )(принима|доставля|работа)ет",
]
MIN_WORDS = 1600
fails = []


def fail(rule, f, detail):
    fails.append(f"FAIL {rule}: {f}: {detail}")


# 1) базовые правила статьи из check_articles.py
ca.GROUPS["th-ru"] = {SLUG: REQUIRED}
ca.DATE = DATE
ca.FORBIDDEN = [x for x in ca.FORBIDDEN if "₽" not in x]
ca.EXT_ALLOWED_PREFIXES = ca.EXT_ALLOWED_PREFIXES + EXTRA_EXT
argv, sys.argv = sys.argv, [sys.argv[0], "--group", "th-ru"]
buf = io.StringIO()
with redirect_stderr(buf):
    rc = ca.main()
sys.argv = argv
if rc:
    fails += [line for line in buf.getvalue().splitlines()
              if line.startswith("FAIL R-") and "соседнюю новую статью" not in line]

# 2) правила M10
f = f"blog/{SLUG}.html"
if os.path.isfile(f):
    raw = open(f, encoding="utf-8").read()
    p = ca.Page()
    p.feed(raw)
    vis = ca.norm(" ".join(p.text))
    words = len(re.findall(r"[A-Za-zА-Яа-яЁё0-9]+", vis))
    if words < MIN_WORDS:
        fail("R10-WORDS", f, f"слов {words} < {MIN_WORDS}")
    h1 = [ca.norm(re.sub(r"<[^>]+>", "", h)) for h in re.findall(r"<h1[^>]*>(.*?)</h1>", raw, re.S)]
    if not any("дёшево" in h.lower() for h in h1):
        fail("R10-H1", f, f"h1 без «дёшево»: {h1}")
    tables = re.findall(r'<div class="table-wrapper">\s*<table>(.*?)</table>\s*</div>', raw, re.S)
    big = [t for t in tables if "<thead>" in t and len(re.findall(r"<tr>", t.split("<tbody>")[-1])) >= 6]
    if len(tables) < 2 or not big:
        fail("R10-TABLE", f, "нужно ≥2 таблиц в .table-wrapper, из них одна с <thead> и ≥6 строками")
    h2 = [ca.norm(re.sub(r"<[^>]+>", "", h)) for h in re.findall(r"<h2[^>]*>(.*?)</h2>", raw, re.S)]
    if sum(h.endswith("?") for h in h2) < 2:
        fail("R10-QH2", f, "нужно ≥2 h2-вопросов")
    if not any("ошибк" in h.lower() for h in h2):
        fail("R10-MISTAKES", f, "нет раздела h2 о частых ошибках")
    if not any(h.startswith(("https://www.thailandpost.co.th/", "https://international.thailandpost.com/"))
               for h in p.hrefs):
        fail("R10-SOURCE", f, "нет ссылки на сайт Thailand Post")
    if not any(h.startswith("https://customs.gov.ru/") for h in p.hrefs):
        fail("R10-SOURCE", f, "нет ссылки на customs.gov.ru")
    for s in M9_SIBLINGS:
        if s not in p.hrefs:
            fail("R10-LINKS", f, f"нет ссылки на {s}")
    if "https://t.me/kolesnikov1988" not in p.hrefs or "пилот" not in vis:
        fail("R10-SELL", f, "нет продажи срочной передачи через пилотов и ссылки на Telegram")
    rows = {}
    for t in big:
        for tr in re.findall(r"<tr>(.*?)</tr>", t.split("<tbody>")[-1], re.S):
            cells = [ca.norm(html.unescape(re.sub(r"<[^>]+>", "", c))).replace("\u00a0", " ")
                     for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S)]
            if cells:
                rows[cells[0]] = cells[1:]
    for w, exp in RATES.items():
        if rows.get(w) != exp:
            fail("R10-RATES", f, f"строка {w!r}: {rows.get(w)} != {exp}")
    # срок «N–M дней» допустим только в предложении про Европу
    for sent in re.split(r"(?<=[.!?])\s+", vis):
        if re.search(r"\d+\s*[–-]\s*\d+\s*(рабочих\s+)?(дн|недел)", sent) and "Европ" not in sent:
            fail("R10-FACT", f, f"срок без привязки к Европе: {sent[:90]!r}")
    for rx in FORBID:
        m = re.search(rx, raw)
        if m:
            fail("R10-FACT", f, f"не подтверждено facts-m10.md: {m.group(0)!r}")

# 3) интеграция в сайт
url = f"https://pumadelivery.ru/blog/{SLUG}.html"
blog = open("blog/index.html", encoding="utf-8").read()
sm = open("sitemap.xml", encoding="utf-8").read()
llms = open("llms.txt", encoding="utf-8").read()
if f'href="/blog/{SLUG}.html"' not in blog:
    fail("R10-INDEX", "blog/index.html", f"нет карточки {SLUG}")
if f"<loc>{url}</loc><lastmod>{DATE}</lastmod>" not in sm:
    fail("R10-SITEMAP", "sitemap.xml", f"нет {url} с lastmod {DATE}")
if url not in llms:
    fail("R10-LLMS", "llms.txt", f"нет {url}")
inbound = [fn for fn in os.listdir("blog") if fn.endswith(".html") and fn not in ("index.html", f"{SLUG}.html")
           and f'href="/blog/{SLUG}.html"' in open(f"blog/{fn}", encoding="utf-8").read()]
if len(inbound) < 3:
    fail("R10-INBOUND", f, f"входящих ссылок из статей {len(inbound)} < 3")
if "blog/pochta-rossii-i-ems-v-tailand.html" not in [f"blog/{x}" for x in inbound]:
    fail("R10-INBOUND", f, "нет входящей ссылки из pochta-rossii-i-ems-v-tailand.html")

for line in fails:
    print(line, file=sys.stderr)
if fails:
    print(f"FAIL: {len(fails)} нарушений", file=sys.stderr)
    sys.exit(1)
print("OK check_m10")
