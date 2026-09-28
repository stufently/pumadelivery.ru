#!/usr/bin/env python3
"""Проверка вехи M9: две новые статьи — Почта России/EMS в Таиланд и местные службы.

Запуск из корня репо: python3 docs/specs/check_m9.py
Базовые правила статьи — из check_articles.py (группа подменяется на M9,
рубли разрешены, список внешних доменов расширен); сверху — правила M9.
FAIL <правило>: <файл>: <деталь>, rc=1 если есть хоть одно. Только stdlib.
"""
import io
import os
import re
import sys
from contextlib import redirect_stderr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_articles as ca  # noqa: E402

POST = "pochta-rossii-i-ems-v-tailand"
LOCAL = "mestnye-sluzhby-dostavki-v-tailande"
M9 = {
    POST: ["Почта России", "EMS", "мелкий пакет", "2 341,18", "6 900,32", "1 708", "30 кг", "20 кг",
           "28 сентября 2026", "Thailand Post", "объявленн"],
    LOCAL: ["KEX", "Kerry", "Flash", "J&T", "Thailand Post", "EMS", "67 бат", "40 бат", "2,4%",
            "7-Eleven", "28 сентября 2026", "Самуи"],
}
EXTRA_EXT = [
    "https://www.pochta.ru/", "https://track.thailandpost.co.th/", "https://www.nationthailand.com/",
    "https://www.thailandpost.co.th/", "https://file.thailandpost.com/", "https://th.kex-express.com/",
    "https://www.flashexpress.co.th/", "https://www.jtexpress.co.th/", "https://spx.co.th/",
    "https://www.nimexpress.com/", "https://www.dhl.com/", "https://iel.co.th/",
    "https://www.lalamove.com/", "https://www.grab.com/",
]
OFFICIAL = {
    POST: ("https://www.pochta.ru/", "https://info.pochta.ru/"),
    LOCAL: ("https://www.thailandpost.co.th/", "https://th.kex-express.com/", "https://www.flashexpress.co.th/"),
}
# цифры, помеченные в facts-m9.md как НЕ НАЙДЕНО/противоречивые
FORBID = {
    POST: [r"31[,.]5\s*кг", r"EMS[^.<]{0,80}объявленн[^.<]{0,40}(можно|доступн)", r"\d+\s*[–-]\s*\d+\s*(недел|дней)[^.<]{0,30}(до Таиланда|в Таиланд)"],
    LOCAL: [r"J&(amp;)?T[^.<]{0,60}(20|50)\s*кг"],
}
MIN_WORDS = 1600
fails = []


def fail(rule, f, detail):
    fails.append(f"FAIL {rule}: {f}: {detail}")


# 1) базовые правила статьи из check_articles.py
ca.GROUPS["ru-th"] = M9
ca.FORBIDDEN = [x for x in ca.FORBIDDEN if "₽" not in x]
ca.EXT_ALLOWED_PREFIXES = ca.EXT_ALLOWED_PREFIXES + EXTRA_EXT
argv, sys.argv = sys.argv, [sys.argv[0], "--group", "ru-th"]
buf = io.StringIO()
with redirect_stderr(buf):
    rc = ca.main()
sys.argv = argv
if rc:
    fails += [line for line in buf.getvalue().splitlines() if line.startswith("FAIL R-")]

# 2) правила M9
for slug in M9:
    f = f"blog/{slug}.html"
    if not os.path.isfile(f):
        continue
    raw = open(f, encoding="utf-8").read()
    p = ca.Page()
    p.feed(raw)
    vis = ca.norm(" ".join(p.text))
    words = len(re.findall(r"[A-Za-zА-Яа-яЁё0-9]+", vis))
    if words < MIN_WORDS:
        fail("R9-WORDS", f, f"слов {words} < {MIN_WORDS}")
    tables = re.findall(r'<div class="table-wrapper">\s*<table>(.*?)</table>\s*</div>', raw, re.S)
    big = [t for t in tables if "<thead>" in t and len(re.findall(r"<tr>", t.split("<tbody>")[-1])) >= 6]
    if len(tables) < 2 or not big:
        fail("R9-TABLE", f, "нужно ≥2 таблиц в .table-wrapper, из них одна с <thead> и ≥6 строками")
    h2 = [ca.norm(re.sub(r"<[^>]+>", "", h)) for h in re.findall(r"<h2[^>]*>(.*?)</h2>", raw, re.S)]
    if sum(h.endswith("?") for h in h2) < 2:
        fail("R9-QH2", f, "нужно ≥2 h2-вопросов")
    if not any("ошибк" in h.lower() for h in h2):
        fail("R9-MISTAKES", f, "нет раздела h2 о частых ошибках")
    if not any(h.startswith(OFFICIAL[slug]) for h in p.hrefs):
        fail("R9-SOURCE", f, f"нет ссылки на {OFFICIAL[slug]}")
    if "https://t.me/kolesnikov1988" not in p.hrefs or "пилот" not in vis:
        fail("R9-SELL", f, "нет продажи срочной передачи через пилотов и ссылки на Telegram")
    for rx in FORBID[slug]:
        m = re.search(rx, raw)
        if m:
            fail("R9-FACT", f, f"не подтверждено facts-m9.md: {m.group(0)!r}")

# 3) интеграция в сайт
blog = open("blog/index.html", encoding="utf-8").read()
sm = open("sitemap.xml", encoding="utf-8").read()
llms = open("llms.txt", encoding="utf-8").read()
for slug in M9:
    url = f"https://pumadelivery.ru/blog/{slug}.html"
    if f'href="/blog/{slug}.html"' not in blog:
        fail("R9-INDEX", "blog/index.html", f"нет карточки {slug}")
    if f"<loc>{url}</loc><lastmod>2026-09-28</lastmod>" not in sm:
        fail("R9-SITEMAP", "sitemap.xml", f"нет {url} с lastmod 2026-09-28")
    if url not in llms:
        fail("R9-LLMS", "llms.txt", f"нет {url}")
    inbound = [fn for fn in os.listdir("blog") if fn.endswith(".html") and fn not in ("index.html", f"{slug}.html")
               and f'href="/blog/{slug}.html"' in open(f"blog/{fn}", encoding="utf-8").read()]
    if len(inbound) < 3:
        fail("R9-INBOUND", f"blog/{slug}.html", f"входящих ссылок из статей {len(inbound)} < 3")

for line in fails:
    print(line, file=sys.stderr)
if fails:
    print(f"FAIL: {len(fails)} нарушений", file=sys.stderr)
    sys.exit(1)
print("OK check_m9")
