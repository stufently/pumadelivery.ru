#!/usr/bin/env python3
"""Проверка вех M6/M7: расширение 19 статей проверяемым содержанием.

Запуск из корня репо: python3 docs/specs/check_m6.py --group ru-th|th-ru
M6 = ru-th (+ reviews.html без aggregateRating), M7 = th-ru.
FAIL <правило>: <файл>: <деталь> на каждое нарушение, rc=1 если есть хоть одно.
Только stdlib.
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_articles import GROUPS, Page, norm  # noqa: E402

# число слов видимого текста на 2026-09-28 (до расширения)
BASE_WORDS = {
    "lekarstva-iz-rossii-v-tailand": 1187, "dokumenty-iz-rossii-v-tailand": 1048,
    "russkie-produkty-v-tailand": 1105, "russkie-sladosti-v-tailand": 1081,
    "chaj-med-specii-iz-rossii-v-tailand": 1053, "knigi-iz-rossii-v-tailand": 1058,
    "zakazy-wildberries-ozon-v-tailand": 1025, "lichnye-veshchi-iz-rossii-v-tailand": 997,
    "zapchasti-iz-rossii-v-tailand": 943, "tajskie-lekarstva-v-rossiyu": 932,
    "tajskaya-kosmetika-v-rossiyu": 942, "tajskie-balzamy-i-ingalyatory-v-rossiyu": 913,
    "frukty-iz-tailanda-v-rossiyu": 1022, "iphone-i-elektronika-iz-tailanda-v-rossiyu": 929,
    "tajskij-chaj-kofe-sousy-v-rossiyu": 985, "kokosovoe-maslo-i-zubnye-pasty-iz-tailanda": 932,
    "vitaminy-i-bady-iz-tailanda-v-rossiyu": 920, "odezhda-i-ekipirovka-muay-tai-iz-tailanda": 925,
    "vykup-lazada-shopee-s-dostavkoj-v-rossiyu": 973,
}
MIN_TOTAL, MIN_GAIN = 1300, 300
OFFICIAL = ("https://customs.gov.ru/", "https://en.fda.moph.go.th/", "https://info.pochta.ru/",
            "https://eec.eaeunion.org/", "https://www.customs.go.th/", "https://www.iata.org/")
fails = []


def fail(rule, f, detail):
    fails.append(f"FAIL {rule}: {f}: {detail}")


ap = argparse.ArgumentParser()
ap.add_argument("--group", choices=["ru-th", "th-ru"], required=True)
group = ap.parse_args().group

for slug in GROUPS[group]:
    f = f"blog/{slug}.html"
    raw = open(f, encoding="utf-8").read()
    p = Page()
    p.feed(raw)
    words = len(re.findall(r"[A-Za-zА-Яа-яЁё0-9]+", norm(" ".join(p.text))))
    need = max(MIN_TOTAL, BASE_WORDS[slug] + MIN_GAIN)
    if words < need:
        fail("R-WORDS", f, f"слов {words} < {need}")

    tables = re.findall(r'<div class="table-wrapper">\s*<table>(.*?)</table>\s*</div>', raw, re.S)
    ok = [t for t in tables if "<thead>" in t and len(re.findall(r"<tr>", t.split("<tbody>")[-1])) >= 4]
    if not ok:
        fail("R-TABLE", f, 'нет <div class="table-wrapper"><table> с <thead> и ≥4 строками в <tbody>')

    h2 = [norm(re.sub(r"<[^>]+>", "", h)) for h in re.findall(r"<h2[^>]*>(.*?)</h2>", raw, re.S)]
    if not any(h.endswith("?") for h in h2):
        fail("R-QH2", f, "нет ни одного h2-вопроса")
    if not any("ошибк" in h.lower() for h in h2):
        fail("R-MISTAKES", f, "нет раздела h2 о частых ошибках")

    body = raw.split('<section id="footer"')[0]
    ext = set(re.findall(r'href="(https://[^"]+)"', body))
    if not [h for h in ext if h.startswith(OFFICIAL)]:
        fail("R-SOURCE", f, "нет ссылки на официальный первоисточник из списка")

if group == "ru-th":
    raw = open("reviews.html", encoding="utf-8").read()
    for blob in re.findall(r'<script type="application/ld\+json">(.*?)</script>', raw, re.S):
        if "aggregateRating" in json.dumps(json.loads(blob)):
            fail("R-RATING", "reviews.html", "aggregateRating в разметке (самоотзывы — Google не покажет)")

for line in fails:
    print(line, file=sys.stderr)
if fails:
    print(f"FAIL: {len(fails)} нарушений", file=sys.stderr)
    sys.exit(1)
print(f"OK check_m6 {group}")
