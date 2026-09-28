#!/usr/bin/env python3
"""Проверка статей блога pumadelivery.ru для контент-вех M1/M2.

Запуск из корня репо: python3 docs/specs/check_articles.py --group ru-th|th-ru|all
Печатает FAIL <правило>: <файл>: <деталь> на каждое нарушение, rc=1 если есть
хоть одно; иначе OK и rc=0. Только stdlib.
"""
import argparse
import json
import os
import re
import sys
from html.parser import HTMLParser
from urllib.parse import urlparse

SITE = "https://pumadelivery.ru"
DATE = "2026-09-28"
AUTHOR_ID = "https://pumadelivery.ru/about.html#dmitry"
ORG_ID = "https://pumadelivery.ru/#org"
CSS_LINE = ('<link rel="preload" as="style" href="/assets/css/main.min.css" '
            'onload="this.onload=null;this.rel=\'stylesheet\'"><noscript>'
            '<link rel="stylesheet" href="/assets/css/main.min.css"></noscript>')
BUNDLE = '<script defer src="/assets/js/bundle.min.js"></script>'
CTA = "https://t.me/kolesnikov1988"
CITIES = ["/bangkok.html", "/pattaya.html", "/phuket.html", "/samui.html", "/phangan.html"]
OLD_ARTICLES = [
    "chto-nelzya-vvozit-v-tailand", "receptury-lekarstva-turistu",
    "kak-zakazat-s-lazada-v-tailande", "lazada-vs-shopee",
    "dostavka-alkogolya-v-tailande", "perevozka-mezhdu-gorodami-tailanda",
    "tajskaya-bankovskaya-karta-2026",
]
EXT_ALLOWED_PREFIXES = [
    "https://t.me/kolesnikov1988", "https://t.me/stufently",
    "https://vk.com/pumainthailand", "mailto:pumainthailand.com@gmail.com",
    "https://customs.gov.ru/", "https://en.fda.moph.go.th/",
    "https://info.pochta.ru/", "https://eec.eaeunion.org/",
    "https://www.customs.go.th/", "https://www.iata.org/",
]
FORBIDDEN = [
    r"гарантиру", r"100\s?%", r"без\s+таможн", r"в\s+обход", r"обойти\s+таможн",
    r"lorem", r"\bTODO\b", r"\\'", r"\d[\d\s]*(₽|руб)", r"Co-Authored",
    r"не\s+нужно\s+декларир", r"никто\s+не\s+провер",
]

GROUPS = {
    "ru-th": {
        "lekarstva-iz-rossii-v-tailand": ["30 дней", "Thai FDA", "кодеин", "fda.moph.go.th"],
        "dokumenty-iz-rossii-v-tailand": ["паспорт", "виз"],
        "russkie-produkty-v-tailand": ["10 кг", "сало", "икр", "гречк"],
        "russkie-sladosti-v-tailand": ["Птичье молоко", "пастил"],
        "chaj-med-specii-iz-rossii-v-tailand": ["мёд", "чай", "специ"],
        "knigi-iz-rossii-v-tailand": ["книг", "пропис"],
        "zakazy-wildberries-ozon-v-tailand": ["Wildberries", "Ozon"],
        "lichnye-veshchi-iz-rossii-v-tailand": ["личн", "переезд"],
        "zapchasti-iz-rossii-v-tailand": ["запчаст", "габарит"],
    },
    "th-ru": {
        "tajskie-lekarstva-v-rossiyu": ["наркотическ", "психотроп", "декларир", "customs.gov.ru"],
        "tajskaya-kosmetika-v-rossiyu": ["крем", "10 000 евро"],
        "tajskie-balzamy-i-ingalyatory-v-rossiyu": ["бальзам", "ингалятор"],
        "frukty-iz-tailanda-v-rossiyu": ["5 кг", "дуриан", "манго"],
        "iphone-i-elektronika-iz-tailanda-v-rossiyu": ["10 000 евро", "50 кг", "личного пользования", "батаре"],
        "tajskij-chaj-kofe-sousy-v-rossiyu": ["чай", "кофе", "карри"],
        "kokosovoe-maslo-i-zubnye-pasty-iz-tailanda": ["кокосов", "зубн"],
        "vitaminy-i-bady-iz-tailanda-v-rossiyu": ["витамин", "БАД"],
        "odezhda-i-ekipirovka-muay-tai-iz-tailanda": ["муай-тай", "одежд"],
        "vykup-lazada-shopee-s-dostavkoj-v-rossiyu": ["Lazada", "Shopee", "200 евро"],
    },
}
MIN_WORDS = 900
MIN_H2 = 5


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack_skip = 0
        self.in_title = False
        self.title = ""
        self.text = []
        self.metas = {}
        self.links = []
        self.hrefs = []
        self.imgs = []
        self.scripts_src = []
        self.jsonld = []
        self._jsonld_buf = None
        self.h1 = 0
        self.h2 = 0
        self.canon = []
        self.paras = []
        self._p = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "script":
            if a.get("type") == "application/ld+json":
                self._jsonld_buf = []
            if a.get("src"):
                self.scripts_src.append(a["src"])
            self.stack_skip += 1
        elif tag in ("style", "noscript"):
            self.stack_skip += 1
        elif tag == "title":
            self.in_title = True
        elif tag == "meta":
            k = a.get("name") or a.get("property")
            if k:
                self.metas.setdefault(k, []).append(a.get("content", ""))
        elif tag == "link":
            if a.get("rel") == "canonical":
                self.canon.append(a.get("href", ""))
            self.links.append(a)
        elif tag == "a":
            self.hrefs.append(a.get("href", ""))
        elif tag in ("p", "li"):
            self._p = []
        elif tag == "img":
            self.imgs.append(a)
        elif tag == "h1":
            self.h1 += 1
        elif tag == "h2":
            self.h2 += 1

    def handle_endtag(self, tag):
        if tag == "script":
            if self._jsonld_buf is not None:
                self.jsonld.append("".join(self._jsonld_buf))
                self._jsonld_buf = None
            self.stack_skip -= 1
        elif tag in ("style", "noscript"):
            self.stack_skip -= 1
        elif tag == "title":
            self.in_title = False
        elif tag in ("p", "li") and self._p is not None:
            self.paras.append(norm("".join(self._p)))
            self._p = None

    def handle_data(self, data):
        if self._jsonld_buf is not None:
            self._jsonld_buf.append(data)
            return
        if self.in_title:
            self.title += data
            return
        if self.stack_skip == 0:
            self.text.append(data)
            if self._p is not None:
                self._p.append(data)


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--group", choices=["ru-th", "th-ru", "all"], required=True)
    ap.add_argument("--root", default=".")
    args = ap.parse_args()
    root = args.root
    groups = ["ru-th", "th-ru"] if args.group == "all" else [args.group]
    fails = []

    def fail(rule, f, detail):
        fails.append(f"FAIL {rule}: {f}: {detail}")

    titles, descs, paras = {}, {}, {}
    # собрать title/description всех статей блога для уникальности
    blog_dir = os.path.join(root, "blog")
    for fn in sorted(os.listdir(blog_dir)):
        if fn.endswith(".html"):
            p = Page()
            p.feed(open(os.path.join(blog_dir, fn), encoding="utf-8").read())
            titles.setdefault(norm(p.title), []).append(fn)
            for para in p.paras:
                if len(para) >= 120:
                    paras.setdefault(para, set()).add(fn)
            for d in p.metas.get("description", []):
                descs.setdefault(norm(d), []).append(fn)

    checked = 0
    for g in groups:
        group_slugs = list(GROUPS[g])
        for slug, required in GROUPS[g].items():
            f = f"blog/{slug}.html"
            path = os.path.join(root, f)
            url = f"{SITE}/blog/{slug}.html"
            if not os.path.isfile(path):
                fail("R-EXISTS", f, "нет файла")
                continue
            checked += 1
            raw = open(path, encoding="utf-8").read()
            p = Page()
            p.feed(raw)
            text = norm(" ".join(p.text))

            if not raw.startswith("<!DOCTYPE HTML>"):
                fail("R-DOCTYPE", f, "файл не начинается с <!DOCTYPE HTML>")
            if '<html lang="ru">' not in raw:
                fail("R-LANG", f, 'нет <html lang="ru">')
            t = norm(p.title)
            if not (30 <= len(t) <= 70):
                fail("R-TITLE", f, f"длина title {len(t)} вне 30..70: {t!r}")
            if len(titles.get(t, [])) > 1:
                fail("R-TITLE-UNIQ", f, f"title повторяется в {titles[t]}")
            d = p.metas.get("description", [])
            if len(d) != 1 or not (110 <= len(norm(d[0])) <= 170):
                fail("R-DESC", f, f"description: {[len(norm(x)) for x in d]} (нужно ровно одно, 110..170)")
            elif len(descs.get(norm(d[0]), [])) > 1:
                fail("R-DESC-UNIQ", f, f"description повторяется в {descs[norm(d[0])]}")
            if p.canon != [url]:
                fail("R-CANONICAL", f, f"canonical {p.canon} != [{url}]")
            if p.metas.get("og:url") != [url]:
                fail("R-OG", f, f"og:url {p.metas.get('og:url')}")
            if p.metas.get("og:type") != ["article"]:
                fail("R-OG", f, "og:type не article")
            for k in ("og:title", "og:description", "og:image", "twitter:card"):
                if len(p.metas.get(k, [])) != 1 or not norm(p.metas[k][0]):
                    fail("R-OG", f, f"нет/несколько {k}")
            ogi = (p.metas.get("og:image") or [""])[0]
            if not (ogi.startswith(SITE + "/images/og/") and os.path.isfile(os.path.join(root, ogi[len(SITE) + 1:]))):
                fail("R-OG", f, f"og:image не существует: {ogi}")
            if CSS_LINE not in raw:
                fail("R-CSS", f, "нет строки подключения CSS в исправленном виде")
            if BUNDLE not in raw:
                fail("R-BUNDLE", f, "нет bundle.min.js")
            if [s for s in p.scripts_src if s != "/assets/js/bundle.min.js"]:
                fail("R-SCRIPTS", f, f"лишние внешние скрипты {p.scripts_src}")
            if p.h1 != 1:
                fail("R-H1", f, f"h1 = {p.h1}")
            if p.h2 < MIN_H2:
                fail("R-H2", f, f"h2 = {p.h2} < {MIN_H2}")
            words = len(re.findall(r"[A-Za-zА-Яа-яЁё0-9]+", text))
            if words < MIN_WORDS:
                fail("R-WORDS", f, f"слов {words} < {MIN_WORDS}")

            # JSON-LD
            graph = []
            for blob in p.jsonld:
                try:
                    j = json.loads(blob)
                except json.JSONDecodeError as e:
                    fail("R-JSONLD", f, f"невалидный JSON-LD: {e}")
                    continue
                graph += j.get("@graph", [j])
            by_type = {}
            for node in graph:
                by_type.setdefault(node.get("@type"), []).append(node)
            art = (by_type.get("Article") or [None])[0]
            if not art:
                fail("R-ARTICLE", f, "нет Article")
            else:
                if norm(art.get("headline", "")) != t:
                    fail("R-ARTICLE", f, "headline != title")
                if (art.get("author") or {}).get("@id") != AUTHOR_ID:
                    fail("R-ARTICLE", f, "author @id")
                if (art.get("publisher") or {}).get("@id") != ORG_ID:
                    fail("R-ARTICLE", f, "publisher @id")
                if art.get("datePublished") != DATE or art.get("dateModified") != DATE:
                    fail("R-ARTICLE", f, "даты не " + DATE)
                if art.get("mainEntityOfPage") != url:
                    fail("R-ARTICLE", f, "mainEntityOfPage")
                if art.get("inLanguage") != "ru-RU":
                    fail("R-ARTICLE", f, "inLanguage")
                img = art.get("image", "")
                if not (isinstance(img, str) and img.startswith(SITE + "/") and os.path.isfile(os.path.join(root, img[len(SITE) + 1:]))):
                    fail("R-ARTICLE", f, f"image {img!r}")
            bc = (by_type.get("BreadcrumbList") or [None])[0]
            if not bc:
                fail("R-BREADCRUMB", f, "нет BreadcrumbList")
            else:
                items = [(i.get("position"), i.get("item")) for i in bc.get("itemListElement", [])]
                if items != [(1, SITE + "/"), (2, SITE + "/blog/"), (3, url)]:
                    fail("R-BREADCRUMB", f, f"цепочка {items}")
            faq = (by_type.get("FAQPage") or [None])[0]
            if not faq:
                fail("R-FAQ", f, "нет FAQPage")
            else:
                qs = faq.get("mainEntity", [])
                if not (5 <= len(qs) <= 8):
                    fail("R-FAQ", f, f"вопросов {len(qs)} вне 5..8")
                for q in qs:
                    name = norm(q.get("name", ""))
                    ans = norm((q.get("acceptedAnswer") or {}).get("text", ""))
                    if not name or name not in text:
                        fail("R-FAQ-VISIBLE", f, f"вопрос не виден на странице: {name[:60]!r}")
                    if len(ans) < 80 or ans not in text:
                        fail("R-FAQ-VISIBLE", f, f"ответ (<80 симв. или не виден дословно): {ans[:60]!r}")

            # ссылки
            hrefs = [h for h in p.hrefs if h]
            if CTA not in hrefs:
                fail("R-CTA", f, f"нет ссылки {CTA}")
            if "/blog/" not in hrefs:
                fail("R-LINKS", f, "нет ссылки на /blog/")
            if len({h for h in hrefs if h in CITIES}) < 2:
                fail("R-LINKS", f, "меньше 2 ссылок на страницы городов")
            siblings = {f"/blog/{s}.html" for s in group_slugs if s != slug}
            if not siblings & set(hrefs):
                fail("R-LINKS", f, "нет ссылки на соседнюю новую статью той же вехи")
            if not {f"/blog/{s}.html" for s in OLD_ARTICLES} & set(hrefs):
                fail("R-LINKS", f, "нет ссылки на существующую статью блога")
            for h in hrefs:
                if h.startswith("/"):
                    target = h.split("#")[0]
                    fp = os.path.join(root, target.lstrip("/"))
                    if target.endswith("/"):
                        fp = os.path.join(fp, "index.html")
                    if not os.path.isfile(fp):
                        fail("R-LINK-BROKEN", f, f"битая внутренняя ссылка {h}")
                elif h.startswith("#"):
                    continue
                elif not any(h.startswith(x) for x in EXT_ALLOWED_PREFIXES):
                    fail("R-LINK-EXTERNAL", f, f"внешняя ссылка вне списка: {h}")
            for img in p.imgs:
                src = img.get("src", "")
                if not (img.get("alt") and img.get("width") and img.get("height") and img.get("loading") == "lazy"):
                    fail("R-IMG", f, f"img без alt/width/height/lazy: {src}")
                if not os.path.isfile(os.path.join(root, src.lstrip("/"))):
                    fail("R-IMG", f, f"нет файла {src}")
            if not p.imgs:
                fail("R-IMG", f, "нет картинки")

            # содержание
            low = text.lower()
            if "пилот" not in low:
                fail("R-SERVICE", f, "не описана передача через пилотов")
            for r in required:
                if r.lower() not in low and r not in raw:
                    fail("R-REQUIRED", f, f"нет обязательного {r!r}")
            for pat in FORBIDDEN:
                m = re.search(pat, raw, re.I)
                if m:
                    fail("R-FORBIDDEN", f, f"запрещённое {m.group(0)!r}")
            for tag in ("section", "div", "ul", "ol", "p", "header", "picture", "a", "h2", "h3"):
                o = len(re.findall(rf"<{tag}[\s>]", raw))
                c = raw.count(f"</{tag}>")
                if o != c:
                    fail("R-BALANCE", f, f"<{tag}> открыто {o}, закрыто {c}")
            for para, files in paras.items():
                if f"{slug}.html" in files and len(files) > 1:
                    fail("R-DUP", f, f"абзац повторяется в {sorted(files)}: {para[:60]!r}")
            if "Puma Delivery, с 2019" not in raw:
                fail("R-FOOTER", f, "нет подвала сайта")

    for line in fails:
        print(line, file=sys.stderr)
    if fails:
        print(f"FAIL: {len(fails)} нарушений", file=sys.stderr)
        return 1
    print(f"OK check_articles: {checked} статей")
    return 0


if __name__ == "__main__":
    sys.exit(main())
