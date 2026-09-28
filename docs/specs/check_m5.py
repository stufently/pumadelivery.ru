#!/usr/bin/env python3
"""Проверка вехи M5 (правки по повторному ревью) pumadelivery.ru.

Запуск из корня репо: python3 docs/specs/check_m5.py
FAIL <правило>: <файл>: <деталь> на каждое нарушение, rc=1 если есть хоть одно.
Только stdlib.
"""
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_articles import Page, norm  # noqa: E402

ALC = "blog/dostavka-alkogolya-v-tailande.html"
CAN = "blog/chto-nelzya-vvozit-v-tailand.html"
CITIES_ALC = ["pattaya.html", "phuket.html", "samui.html", "phangan.html"]
TAT_ALC = "https://www.tatnews.org/2026/05/alcohol-sales-and-consumption-rules-updated-in-thailand-what-tourists-need-to-know/"
TAT_CAN = "https://www.tatnews.org/2025/06/cannabis-flower-now-strictly-regulated-in-thailand-important-notice-for-tourists/"
ALL = sorted(glob.glob("*.html") + glob.glob("blog/*.html"))
fails = []


def fail(rule, f, detail):
    fails.append(f"FAIL {rule}: {f}: {detail}")


def load(f):
    raw = open(f, encoding="utf-8").read()
    p = Page()
    p.feed(raw)
    return raw, norm(" ".join(p.text)), p


def faq(raw):
    out = []
    for blob in re.findall(r'<script type="application/ld\+json">(.*?)</script>', raw, re.S):
        j = json.loads(blob)
        for n in (j.get("@graph", [j]) if isinstance(j, dict) else j):
            if n.get("@type") == "FAQPage":
                out += n.get("mainEntity", [])
    return out


def meta(raw, attr, name):
    m = re.search(rf'<meta {attr}="{re.escape(name)}" content="([^"]*)"', raw)
    return m.group(1) if m else ""


# R-FAQ: вопрос и ответ каждой записи FAQPage видны на странице дословно
for f in ALL:
    raw, vis, _ = load(f)
    for q in faq(raw):
        name = norm(q.get("name", ""))
        ans = norm((q.get("acceptedAnswer") or {}).get("text", ""))
        if name not in vis:
            fail("R-FAQ", f, f"вопрос не виден дословно: {name[:70]!r}")
        if ans not in vis:
            fail("R-FAQ", f, f"ответ не виден дословно: {ans[:70]!r}")

# R-ALC: старые часы продажи алкоголя нигде на сайте
OLD_HOURS = [r"11:00\s*[–-]\s*14:00", r"17:00\s*[–-]\s*24:00", r"«дневной разрыв»"]
for f in ALL:
    raw = open(f, encoding="utf-8").read()
    for rx in OLD_HOURS:
        if re.search(rx, raw):
            fail("R-ALC", f, f"устаревшие часы продажи алкоголя: /{rx}/")
NEW_HOURS = r"11:00\s*(–|-|до)\s*24:00"
for f in [ALC] + CITIES_ALC:
    raw, vis, _ = load(f)
    if not re.search(NEW_HOURS, vis):
        fail("R-ALC", f, "в видимом тексте нет часов продажи 11:00–24:00")
    for q in faq(raw):
        t = (q.get("acceptedAnswer") or {}).get("text", "")
        if "алкогол" in (q.get("name", "") + t).lower() and "11:00" in t and not re.search(NEW_HOURS, t):
            fail("R-ALC", f, f"FAQ про алкоголь без 11:00–24:00: {t[:70]!r}")
raw, vis, p = load(ALC)
if "29 мая 2026" not in vis:
    fail("R-ALC", ALC, "нет даты изменения «29 мая 2026»")
if TAT_ALC not in p.hrefs:
    fail("R-ALC", ALC, "нет ссылки на разъяснение TAT об изменении часов")
if re.search(r"пилотн", raw):
    fail("R-ALC", ALC, "упомянут «пилотный проект» — он завершён, правило общее с 29.05.2026")
for rx in (r"3\s*литр", r"после прилёта можно купить"):
    if re.search(rx, raw):
        fail("R-DUTY", ALC, f"дьюти-фри на прилёте закрыт, а текст обещает покупку: /{rx}/")
if not re.search(r"1\s*литр", vis):
    fail("R-DUTY", ALC, "пропала норма беспошлинного ввоза 1 литр")
for tag, val in (("description", meta(raw, "name", "description")),
                 ("og:description", meta(raw, "property", "og:description"))):
    if re.search(r"11:00\s*[–-]\s*14:00|дневн\w* (разрыв|перерыв)", val):
        fail("R-ALC", ALC, f"{tag} описывает отменённый дневной перерыв")

# R-CAN: каннабис — контролируемая трава с 23.06.2025, не «категория 5»
raw, vis, p = load(CAN)
for rx in (r"Категори[яи] 5[^.<]{0,40}марихуан", r"марихуан[^.<]{0,60}Категори[яи] 5",
           r"снова отнесена к запрещённым наркотикам", r"Категори[яи] 5[^.<]{0,60}кратом"):
    if re.search(rx, raw):
        fail("R-CAN", CAN, f"неверная классификация: /{rx}/")
for need in ("23 июня 2025", "рецепт"):
    if need not in vis:
        fail("R-CAN", CAN, f"в видимом тексте нет {need!r}")
if TAT_CAN not in p.hrefs:
    fail("R-CAN", CAN, "нет ссылки на разъяснение TAT о каннабисе")

# R-AUTHOR: якорь подписи автора существует
raw = open("about.html", encoding="utf-8").read()
if not re.search(r'<[a-z0-9]+[^>]*\sid="dmitry"', raw):
    fail("R-AUTHOR", "about.html", 'нет элемента с id="dmitry" — ссылка подписи ведёт в никуда')

# R-MOBILE: шапка статей на телефоне не занимает 80% экрана
css = open("assets/css/main.css", encoding="utf-8").read()
m = [x.start() for x in re.finditer(r"@media screen and \(max-width: 736px\)", css)]
tail = css[m[-1]:] if m else ""
for sel in (r"body\.is-article\s+#header\s*\{[^}]*height:\s*auto", r"body\.is-article\s+#header:after\s*\{[^}]*height:\s*auto"):
    if not re.search(sel, tail):
        fail("R-MOBILE", "assets/css/main.css", f"в блоке max-width:736px нет правила /{sel}/")
for f in sorted(glob.glob("blog/*.html")):
    if f == "blog/index.html":
        continue
    raw = open(f, encoding="utf-8").read()
    if not re.search(r'<body class="[^"]*\bis-article\b', raw):
        fail("R-MOBILE", f, "у <body> нет класса is-article")
for f in [x for x in ALL if not x.startswith("blog/") or x == "blog/index.html"]:
    if re.search(r'<body class="[^"]*\bis-article\b', open(f, encoding="utf-8").read()):
        fail("R-MOBILE", f, "класс is-article только у статей блога")

for line in fails:
    print(line, file=sys.stderr)
if fails:
    print(f"FAIL: {len(fails)} нарушений", file=sys.stderr)
    sys.exit(1)
print("OK check_m5")
