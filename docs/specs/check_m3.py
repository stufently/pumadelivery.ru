#!/usr/bin/env python3
"""Проверка вехи M3 (правки по SEO/GEO-аудиту) pumadelivery.ru.

Запуск из корня репо: python3 docs/specs/check_m3.py
FAIL <правило>: <файл>: <деталь> на каждое нарушение, rc=1 если есть хоть одно.
Только stdlib.
"""
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_articles import GROUPS, OLD_ARTICLES, Page, norm  # noqa: E402

SITE = "https://pumadelivery.ru"
ORG = SITE + "/#org"
BIZ = SITE + "/#business"
SRV_RT = SITE + "/#service-russia-thailand"
CITIES = ["bangkok", "pattaya", "phuket", "samui", "phangan"]
NEW = [s for g in GROUPS.values() for s in g]
DATE = "2026-09-28"
BYLINE = '<a href="/about.html#dmitry">Дмитрий Колесников</a>'
fails = []


def fail(rule, f, detail):
    fails.append(f"FAIL {rule}: {f}: {detail}")


def graph(f):
    raw = open(f, encoding="utf-8").read()
    nodes = []
    for blob in re.findall(r'<script type="application/ld\+json">(.*?)</script>', raw, re.S):
        try:
            j = json.loads(blob)
        except json.JSONDecodeError as e:
            fail("R-JSON", f, f"невалидный JSON-LD: {e}")
            continue
        nodes += j.get("@graph", [j]) if isinstance(j, dict) else j
    return raw, nodes


def of_type(nodes, t):
    return [n for n in nodes if n.get("@type") == t or (isinstance(n.get("@type"), list) and t in n["@type"])]


def text_of(raw):
    p = Page()
    p.feed(raw)
    return norm(" ".join(p.text))


def header(raw):
    m = re.search(r'<section id="header">(.*?)</section>', raw, re.S)
    return m.group(1) if m else ""


def breadcrumb(nodes):
    bc = of_type(nodes, "BreadcrumbList")
    if not bc:
        return None
    return [(i.get("position"), i.get("item")) for i in bc[0].get("itemListElement", [])]


# R-JSON: все HTML сайта разбираются
for f in sorted(glob.glob("*.html") + glob.glob("blog/*.html")):
    graph(f)

# главная: связь бизнеса с организацией и услуга передач
raw, nodes = graph("index.html")
biz = [n for n in nodes if n.get("@id") == BIZ]
if not biz:
    fail("R-BIZ", "index.html", "нет узла #business")
elif (biz[0].get("parentOrganization") or {}).get("@id") != ORG:
    fail("R-BIZ", "index.html", "у #business нет parentOrganization {@id: #org}")
srv = [n for n in nodes if n.get("@id") == SRV_RT]
if not srv:
    fail("R-SERVICE-RT", "index.html", "нет Service #service-russia-thailand")
else:
    s = srv[0]
    if s.get("@type") != "Service":
        fail("R-SERVICE-RT", "index.html", "@type не Service")
    if s.get("provider") != {"@id": BIZ}:
        fail("R-SERVICE-RT", "index.html", f"provider {s.get('provider')}")
    if not norm(s.get("name", "")) or "пилот" not in json.dumps(s, ensure_ascii=False).lower():
        fail("R-SERVICE-RT", "index.html", "нет name или упоминания пилотов в description")
    areas = json.dumps(s.get("areaServed", ""), ensure_ascii=False)
    if "Росси" not in areas or "Таиланд" not in areas:
        fail("R-SERVICE-RT", "index.html", f"areaServed без России и Таиланда: {areas}")

# города
for c in CITIES:
    f = f"{c}.html"
    raw, nodes = graph(f)
    url = f"{SITE}/{c}.html"
    svc = of_type(nodes, "Service")
    if len(svc) != 1:
        fail("R-CITY", f, f"Service узлов {len(svc)} (нужен ровно 1)")
    else:
        if svc[0].get("@id") != url + "#service":
            fail("R-CITY", f, f"Service @id {svc[0].get('@id')} != {url}#service")
        if svc[0].get("provider") != {"@id": BIZ}:
            fail("R-CITY", f, f"provider {svc[0].get('provider')} != {{@id: #business}}")
    if breadcrumb(nodes) != [(1, SITE + "/"), (2, url)]:
        fail("R-CITY-BC", f, f"BreadcrumbList {breadcrumb(nodes)}")

# отзывы: reviewBody дословно виден
raw, nodes = graph("reviews.html")
vis = text_of(raw)
reviews = [n for n in nodes if n.get("@type") == "Review"]
for n in nodes:
    reviews += [r for r in n.get("review", []) if isinstance(r, dict)]
if len(reviews) < 10:
    fail("R-REVIEWS", "reviews.html", f"Review найдено {len(reviews)} < 10")
for r in reviews:
    body = norm(r.get("reviewBody", ""))
    if not body or body not in vis:
        fail("R-REVIEWS", "reviews.html", f"reviewBody не виден дословно: {body[:60]!r}")
if re.search(r"сыворо(ктами|ткой) в отеле", raw):
    fail("R-REVIEWS", "reviews.html", "опечатка «сывороктами/сывороткой» не исправлена (нужно «сыворотками»)")

# статьи: подпись автора ссылкой
for slug in NEW + OLD_ARTICLES:
    f = f"blog/{slug}.html"
    raw, nodes = graph(f)
    if BYLINE not in header(raw):
        fail("R-BYLINE", f, "в section#header нет ссылки автора на /about.html#dmitry")

# новые статьи: about → услуга; вступление 40–85 слов
for slug in NEW:
    f = f"blog/{slug}.html"
    raw, nodes = graph(f)
    art = of_type(nodes, "Article")
    if not art or art[0].get("about") != {"@id": SRV_RT}:
        fail("R-ABOUT", f, "Article.about != {@id: #service-russia-thailand}")
    m = re.search(r'<div class="content">\s*<p>(.*?)</p>', raw, re.S)
    words = len(re.findall(r"[A-Za-zА-Яа-яЁё0-9]+", re.sub(r"<[^>]+>", " ", m.group(1)))) if m else 0
    if not (40 <= words <= 85):
        fail("R-INTRO", f, f"первый абзац div.content: {words} слов вне 40..85")

# старые статьи: хлебные крошки, ссылка на новую статью, дата
sm = open("sitemap.xml", encoding="utf-8").read()
new_links = {f"/blog/{s}.html" for s in NEW}
for slug in OLD_ARTICLES:
    f = f"blog/{slug}.html"
    url = f"{SITE}/blog/{slug}.html"
    raw, nodes = graph(f)
    if breadcrumb(nodes) != [(1, SITE + "/"), (2, SITE + "/blog/"), (3, url)]:
        fail("R-OLD-BC", f, f"BreadcrumbList {breadcrumb(nodes)}")
    p = Page()
    p.feed(raw)
    if not new_links & set(p.hrefs):
        fail("R-OLD-LINKS", f, "нет ссылки ни на одну новую статью")
    art = of_type(nodes, "Article")
    if not art or art[0].get("dateModified") != DATE:
        fail("R-OLD-DATE", f, f"Article.dateModified != {DATE}")
    if f"<loc>{url}</loc><lastmod>{DATE}</lastmod>" not in sm:
        fail("R-OLD-DATE", "sitemap.xml", f"lastmod {url} != {DATE}")

for line in fails:
    print(line, file=sys.stderr)
if fails:
    print(f"FAIL: {len(fails)} нарушений", file=sys.stderr)
    sys.exit(1)
print("OK check_m3")
