#!/usr/bin/env python3
"""Проверка вехи M8: 7 старых статей блога — структура и исправление фактов.

Запуск из корня репо: python3 docs/specs/check_m8.py
FAIL <правило>: <файл>: <деталь> на каждое нарушение, rc=1 если есть хоть одно.
Только stdlib. Факты — docs/specs/facts-m8.md.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_articles import OLD_ARTICLES, Page, norm  # noqa: E402

BASE_WORDS = {
    "chto-nelzya-vvozit-v-tailand": 1166, "receptury-lekarstva-turistu": 1233,
    "kak-zakazat-s-lazada-v-tailande": 1219, "lazada-vs-shopee": 1315,
    "dostavka-alkogolya-v-tailande": 1006, "perevozka-mezhdu-gorodami-tailanda": 1391,
    "tajskaya-bankovskaya-karta-2026": 1342,
}
MIN_GAIN = 150
SOURCES = {
    "chto-nelzya-vvozit-v-tailand": ("https://www.customs.go.th/", "https://en.fda.moph.go.th/", "https://www.tatnews.org/"),
    "dostavka-alkogolya-v-tailande": ("https://www.tatnews.org/", "https://www.customs.go.th/"),
    "receptury-lekarstva-turistu": ("https://en.fda.moph.go.th/",),
    "kak-zakazat-s-lazada-v-tailande": ("https://pages.lazada.co.th/", "https://help.shopee.co.th/"),
    "lazada-vs-shopee": ("https://pages.lazada.co.th/", "https://help.shopee.co.th/"),
    "tajskaya-bankovskaya-karta-2026": ("https://www.thailandprivilege.co.th/", "https://www.kasikornbank.com/", "https://london.thaiembassy.org/"),
    "perevozka-mezhdu-gorodami-tailanda": ("https://lomprayah.com/", "https://rrcticket.com/"),
}
LAZ = [r"JD Central", r"\d+\s*%", r"7\s*[–-]\s*14 дней", r"7\s*[–-]\s*10 дней", r"\bDTAC\b(?!.{0,3}True)"]
# ложные/неподтверждённые утверждения по facts-m8.md
FORBID = {
    "kak-zakazat-s-lazada-v-tailande": LAZ,
    "lazada-vs-shopee": LAZ + [r"в 2019 году"],
    "receptury-lekarstva-turistu": [r"\d+\s*%", r"Приём терапевта", r"психотропные и наркотические требуют разрешения"],
    "tajskaya-bankovskaya-karta-2026": [r"600\s*(тыс|000)", r"любой банк откроет", r"60 дней", r"KMA Tide", r"KBANK NEXT",
                                        r"5\s*[–-]\s*10 тысяч бат", r"\d+\s*%", r"Wio Bank", r"Ameriabank", r"Halyk", r"Kaspi",
                                        r"Binance", r"Bybit|ByBit"],
    "perevozka-mezhdu-gorodami-tailanda": [r"каждые 30 минут", r"Острова Самуи и Чумпхон", r"Sai Tai Mai", r"URT за 1 час"],
}
REQUIRE = {
    "kak-zakazat-s-lazada-v-tailande": ["KEX", "15 дней"],
    "lazada-vs-shopee": ["15 дней"],
    "receptury-lekarstva-turistu": ["IC-2", "Schedule", "30 дней"],
    "tajskaya-bankovskaya-karta-2026": ["650 000", "Bangkok Bank", "Kasikorn", "30 дней", "20 000"],
    "perevozka-mezhdu-gorodami-tailanda": ["Pinklao", "Lipa Noi", "KEX"],
}
# цены в батах в статьях, где ни одна цена не подтверждена (кроме разрешённых)
BAHT_FREE = ["kak-zakazat-s-lazada-v-tailande", "lazada-vs-shopee", "receptury-lekarstva-turistu",
             "perevozka-mezhdu-gorodami-tailanda", "tajskaya-bankovskaya-karta-2026"]
BAHT_OK = [r"650\s000", r"900\s000", r"500\s000"]
fails = []


def fail(rule, f, detail):
    fails.append(f"FAIL {rule}: {f}: {detail}")


for slug in OLD_ARTICLES:
    f = f"blog/{slug}.html"
    raw = open(f, encoding="utf-8").read()
    p = Page()
    p.feed(raw)
    vis = norm(" ".join(p.text))
    words = len(re.findall(r"[A-Za-zА-Яа-яЁё0-9]+", vis))
    if words < BASE_WORDS[slug] + MIN_GAIN:
        fail("R-WORDS", f, f"слов {words} < {BASE_WORDS[slug] + MIN_GAIN}")

    tables = re.findall(r'<div class="table-wrapper">\s*<table>(.*?)</table>\s*</div>', raw, re.S)
    if not [t for t in tables if "<thead>" in t and len(re.findall(r"<tr>", t.split("<tbody>")[-1])) >= 4]:
        fail("R-TABLE", f, 'нет <div class="table-wrapper"><table> с <thead> и ≥4 строками в <tbody>')
    h2 = [norm(re.sub(r"<[^>]+>", "", h)) for h in re.findall(r"<h2[^>]*>(.*?)</h2>", raw, re.S)]
    if not any(h.endswith("?") for h in h2):
        fail("R-QH2", f, "нет ни одного h2-вопроса")
    if not any("ошибк" in h.lower() for h in h2):
        fail("R-MISTAKES", f, "нет раздела h2 о частых ошибках")
    body = raw.split('<section id="footer"')[0]
    if not [h for h in re.findall(r'href="(https://[^"]+)"', body) if h.startswith(SOURCES[slug])]:
        fail("R-SOURCE", f, f"нет ссылки на первоисточник {SOURCES[slug]}")

    for rx in FORBID.get(slug, []):
        m = re.search(rx, raw)
        if m:
            fail("R-FACT", f, f"неверное/неподтверждённое по facts-m8.md: /{rx}/ → {m.group(0)!r}")
    for need in REQUIRE.get(slug, []):
        if need not in vis:
            fail("R-FACT", f, f"в видимом тексте нет {need!r} (facts-m8.md)")
    if slug in BAHT_FREE:
        for m in re.finditer(r"(\d[\d\s]*)(?:[–-]\s*\d[\d\s]*)?\s*(тыс\S*\s*)?бат", vis):
            if not any(re.search(ok, m.group(0)) for ok in BAHT_OK):
                fail("R-BAHT", f, f"цена без подтверждения: {m.group(0)!r}")

for line in fails:
    print(line, file=sys.stderr)
if fails:
    print(f"FAIL: {len(fails)} нарушений", file=sys.stderr)
    sys.exit(1)
print("OK check_m8")
