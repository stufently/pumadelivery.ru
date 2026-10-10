#!/usr/bin/env python3
"""Static checks for milestone M11 (new theme + home sections moved to /uslugi/).

Usage: python3 docs/specs/check_theme.py [--base <sha>]
Compares the working tree with BASE (git show BASE:<file>). stdlib only.
Exit 0 = all rules pass, 1 = violations (printed as "RULE file: detail").
"""
import argparse
import html
import json
import os
import re
import subprocess
import sys
from html.parser import HTMLParser

BASE_DEFAULT = "d507257f074c5a9e9978619a786daf68195f7200"  # replaced in the spec commit
SITE = "https://pumadelivery.ru"
TG = "https://t.me/kolesnikov1988"
CITY_PAGES = ["bangkok.html", "pattaya.html", "phuket.html", "samui.html", "phangan.html"]
# section id on the BASE home page -> new page that must hold its text
MOVED = {
    "wholesale": "uslugi/poisk-postavshchikov-v-tailande.html",
    "errands": "uslugi/porucheniya-i-zakupki-v-tailande.html",
    "guarantor": "uslugi/postoplata-i-garant.html",
}
NEW_PAGES = list(MOVED.values())
CSS_MAX = 40 * 1024
JS_MAX = 20 * 1024
COUNTER_MARKS = [
    'https://www.googletagmanager.com/gtag/js?id=G-HHLE9R0EYW',
    "gtag('config','G-HHLE9R0EYW')",
    'ym(108157978, "init"',
    'https://mc.yandex.ru/watch/108157978',
]
HOME_CONTACTS = [TG, "https://t.me/stufently", "https://vk.com/pumainthailand",
                 "mailto:pumainthailand.com@gmail.com"]

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
errors = []


def fail(rule, f, msg):
    errors.append(f"{rule} {f}: {msg}")


def git(*a):
    return subprocess.run(["git", "-C", ROOT, *a], check=True, capture_output=True, text=True).stdout


def base_file(base, f):
    return git("show", f"{base}:{f}")


def read(f):
    with open(os.path.join(ROOT, f), encoding="utf-8") as fh:
        return fh.read()


def norm(s):
    s = html.unescape(s).replace("\xa0", " ")
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"\s+([,.;:!?)»…])", r"\1", s)
    s = re.sub(r"([(«])\s+", r"\1", s)
    return s


class Text(HTMLParser):
    """Visible body text (spaces at tag edges) + text of p/li/h1-h3 blocks with their section id."""
    SKIP = {"script", "style", "noscript", "template"}
    BLOCKS = {"p", "li", "h1", "h2", "h3", "h4", "td", "th", "dt", "dd", "figcaption", "blockquote", "summary"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self.blocks = [], []
        self.skip = 0
        self.in_body = False
        self.open = []          # stack of [tag, [texts]]
        self.section = []       # stack of section ids

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "body":
            self.in_body = True
        if tag in self.SKIP:
            self.skip += 1
        if tag == "section":
            self.section.append(a.get("id") or "")
        if tag in self.BLOCKS:
            self.open.append([tag, [], self.section[-1] if self.section else ""])
        self.parts.append(" ")
        for o in self.open:
            o[1].append(" ")

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.skip:
            self.skip -= 1
        if tag == "section" and self.section:
            self.section.pop()
        if tag in self.BLOCKS:
            for i in range(len(self.open) - 1, -1, -1):
                if self.open[i][0] == tag:
                    t, txt, sec = self.open.pop(i)
                    self.blocks.append((sec, norm("".join(txt))))
                    break
        self.parts.append(" ")
        for o in self.open:
            o[1].append(" ")

    def handle_data(self, d):
        if self.skip or not self.in_body:
            return
        self.parts.append(d)
        for o in self.open:
            o[1].append(d)

    @property
    def text(self):
        return norm("".join(self.parts))


def parse_text(raw):
    p = Text()
    p.feed(raw)
    return p


class Head(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title, self.metas, self.links, self.jsonld = None, {}, {}, []
        self._t = None
        self.lang = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang")
        if tag == "title" and self.title is None:
            self._t = []
        if tag == "meta":
            k = a.get("name") or a.get("property")
            if k and k != "viewport":
                self.metas.setdefault(k, []).append(norm(a.get("content") or ""))
        if tag == "link" and a.get("rel") == "canonical":
            self.links.setdefault("canonical", []).append(a.get("href"))
        if tag == "script" and a.get("type") == "application/ld+json":
            self._t = ["__ld__"]

    def handle_endtag(self, tag):
        if tag == "title" and self._t is not None and self._t[:1] != ["__ld__"]:
            self.title = norm("".join(self._t))
            self._t = None
        if tag == "script" and self._t and self._t[0] == "__ld__":
            self.jsonld.append("".join(self._t[1:]))
            self._t = None

    def handle_data(self, d):
        if self._t is not None:
            self._t.append(d)


def parse_head(raw):
    h = Head()
    h.feed(raw)
    try:
        h.jsonld_parsed = [json.loads(x) for x in h.jsonld]
    except json.JSONDecodeError as e:
        h.jsonld_parsed = None
        h.jsonld_error = str(e)
    return h


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=BASE_DEFAULT)
    base = ap.parse_args().base

    base_pages = [f for f in git("ls-tree", "-r", "--name-only", base).split("\n")
                  if re.fullmatch(r"(blog/)?[a-z0-9-]+\.html", f) and not f.startswith(("google", "yandex_"))]
    if len(base_pages) < 30:
        fail("R-BASE", base, f"на BASE найдено {len(base_pages)} страниц — не тот BASE?")

    # R-PAGES + R-HEAD: every old page exists, SEO head unchanged
    for f in base_pages:
        if not os.path.exists(os.path.join(ROOT, f)):
            fail("R-PAGES", f, "страница с BASE удалена (старый URL должен отдавать 200)")
            continue
        old, new = parse_head(base_file(base, f)), parse_head(read(f))
        if old.lang != new.lang:
            fail("R-HEAD", f, f"html lang {new.lang!r} != {old.lang!r}")
        if old.title != new.title:
            fail("R-HEAD", f, f"title изменён: {new.title!r}")
        if old.links != new.links:
            fail("R-HEAD", f, f"canonical изменён: {new.links}")
        for k in sorted(set(old.metas) | set(new.metas)):
            if k.startswith(("og:", "twitter:")) or k in ("description", "robots", "yandex-verification", "author"):
                if old.metas.get(k) != new.metas.get(k):
                    fail("R-HEAD", f, f"meta {k}: {new.metas.get(k)} != {old.metas.get(k)}")
        if new.jsonld_parsed is None:
            fail("R-HEAD", f, f"невалидный JSON-LD: {new.jsonld_error}")
        elif old.jsonld_parsed != new.jsonld_parsed:
            fail("R-HEAD", f, "JSON-LD изменён")

    all_pages = base_pages + NEW_PAGES
    for f in all_pages:
        if not os.path.exists(os.path.join(ROOT, f)):
            if f in NEW_PAGES:
                fail("R-NEW", f, "нет файла")
            continue
        raw = read(f)
        # R-COUNTERS
        for m in COUNTER_MARKS:
            if m not in raw:
                fail("R-COUNTERS", f, f"нет {m!r}")
        # R-FLOAT: one floating Telegram link on every page
        floats = re.findall(r'<a\b[^>]*class="[^"]*\btg-float\b[^"]*"[^>]*>', raw)
        if len(floats) != 1 or f'href="{TG}"' not in floats[0]:
            fail("R-FLOAT", f, f"ожидалась ровно одна <a class=tg-float href={TG}>, найдено {len(floats)}")
        # R-ASSETS: no external fonts/styles
        if re.search(r"fonts\.(googleapis|gstatic)\.com", raw):
            fail("R-ASSETS", f, "внешние шрифты Google Fonts")
        if f in base_pages and "geo.hqdthai.ru/v1/contact.js" in base_file(base, f) \
                and "geo.hqdthai.ru/v1/contact.js" not in raw:
            fail("R-CONTACTJS", f, "пропал скрипт geo.hqdthai.ru/v1/contact.js")

    # R-HERO markup on home and city pages (runtime size is checked by check_layout.mjs)
    for f in ["index.html"] + CITY_PAGES + NEW_PAGES:
        if not os.path.exists(os.path.join(ROOT, f)):
            continue
        raw = read(f)
        m = re.search(r"<(\w+)\b[^>]*\bdata-hero\b[^>]*>", raw)
        if not m:
            fail("R-HERO", f, "нет элемента с data-hero")
        elif not re.search(r'<a\b[^>]*href="%s"[^>]*data-cta="telegram"|<a\b[^>]*data-cta="telegram"[^>]*href="%s"'
                           % (re.escape(TG), re.escape(TG)), raw):
            fail("R-HERO", f, f'нет <a data-cta="telegram" href="{TG}">')
        if len(re.findall(r"<h1\b", raw)) != 1:
            fail("R-H1", f, "должен быть ровно один h1")

    # R-CSS / R-JS budgets
    css = read("assets/css/main.min.css")
    if len(css.encode()) > CSS_MAX:
        fail("R-CSS", "assets/css/main.min.css", f"{len(css.encode())} B > {CSS_MAX}")
    if "@import" in css:
        fail("R-CSS", "assets/css/main.min.css", "@import в CSS")
    js_size = os.path.getsize(os.path.join(ROOT, "assets/js/bundle.min.js"))
    if js_size > JS_MAX:
        fail("R-JS", "assets/js/bundle.min.js", f"{js_size} B > {JS_MAX}")

    # R-TEXT: every text block of every BASE page survives on the same page;
    # blocks of the moved home sections live on their /uslugi/ page only.
    new_texts = {p: parse_text(read(p)).text for p in NEW_PAGES if os.path.exists(os.path.join(ROOT, p))}
    home = parse_text(read("index.html")).text
    old = None
    for f in base_pages:
        if not os.path.exists(os.path.join(ROOT, f)):
            continue
        ob = parse_text(base_file(base, f))
        if f == "index.html":
            old = ob
        cur = home if f == "index.html" else parse_text(read(f)).text
        for sec, blk in ob.blocks:
            if not blk or (len(blk.split()) < 3 and not re.search(r"\d", blk)):
                continue
            if f == "index.html" and sec in MOVED:
                target = MOVED[sec]
                if blk not in new_texts.get(target, ""):
                    fail("R-TEXT", target, f"нет текста из секции #{sec}: {blk[:70]!r}")
                if len(blk.split()) >= 12 and blk in home:
                    fail("R-MOVED", "index.html", f"абзац секции #{sec} остался на главной: {blk[:60]!r}")
            elif blk not in cur:
                fail("R-TEXT", f, f"пропал текст (#{sec}): {blk[:70]!r}")

    # R-NEW: SEO of the new pages
    titles, descs = {}, {}
    home_raw = read("index.html")
    base_home_text = old.text
    for f in NEW_PAGES:
        if f not in new_texts:
            continue
        raw = read(f)
        h = parse_head(raw)
        url = f"{SITE}/{f}"
        if h.lang != "ru":
            fail("R-NEW", f, 'нет <html lang="ru">')
        t = h.title or ""
        if not 30 <= len(t) <= 70:
            fail("R-NEW", f, f"длина title {len(t)} вне 30..70")
        if t in titles:
            fail("R-NEW", f, f"title повторяется с {titles[t]}")
        titles[t] = f
        d = h.metas.get("description", [])
        if len(d) != 1 or not 110 <= len(d[0]) <= 170:
            fail("R-NEW", f, f"description {[len(x) for x in d]} (нужно ровно одно, 110..170)")
        elif d[0] in descs:
            fail("R-NEW", f, "description повторяется")
        else:
            descs[d[0]] = f
        if h.links.get("canonical") != [url]:
            fail("R-NEW", f, f"canonical {h.links.get('canonical')} != {url}")
        if h.metas.get("og:url") != [url]:
            fail("R-NEW", f, f"og:url {h.metas.get('og:url')}")
        for k in ("og:title", "og:description", "og:image", "og:type"):
            if len(h.metas.get(k, [])) != 1:
                fail("R-NEW", f, f"нет/несколько {k}")
        ogi = (h.metas.get("og:image") or [""])[0]
        if ogi.startswith(SITE + "/") and not os.path.exists(os.path.join(ROOT, ogi[len(SITE) + 1:])):
            fail("R-NEW", f, f"og:image не существует: {ogi}")
        types = set()

        def walk(n):
            if isinstance(n, dict):
                t_ = n.get("@type")
                types.update(t_ if isinstance(t_, list) else [t_])
                for v in n.values():
                    walk(v)
            elif isinstance(n, list):
                for v in n:
                    walk(v)
        if h.jsonld_parsed is None:
            fail("R-NEW", f, "невалидный JSON-LD")
        else:
            walk(h.jsonld_parsed)
            for need in ("Service", "BreadcrumbList"):
                if need not in types:
                    fail("R-NEW", f, f"нет {need} в JSON-LD")
            if '"https://pumadelivery.ru/#business"' not in raw and '"https://pumadelivery.ru/#org"' not in raw:
                fail("R-NEW", f, "Service не ссылается на #business/#org")
        cities = sum(1 for c in CITY_PAGES if f'href="/{c}"' in raw)
        if cities < 2:
            fail("R-NEW", f, "меньше 2 ссылок на страницы городов")
        if 'href="/"' not in raw:
            fail("R-NEW", f, 'нет ссылки на главную href="/"')
        if f'href="/{f}"' not in home_raw:
            fail("R-NEW", "index.html", f'нет ссылки на /{f}')
        # no invented numbers: every number in the new page text exists in the BASE home text
        for num in set(re.findall(r"\d+", new_texts[f])):
            if not re.search(r"(?<!\d)%s(?!\d)" % num, base_home_text):
                fail("R-FACTS", f, f"число {num} отсутствует в тексте главной на BASE (новые факты запрещены)")

    # R-SITEMAP / R-LLMS
    sm_old = set(re.findall(r"<loc>([^<]+)</loc>", base_file(base, "sitemap.xml")))
    sm_new = set(re.findall(r"<loc>([^<]+)</loc>", read("sitemap.xml")))
    for u in sorted(sm_old - sm_new):
        fail("R-SITEMAP", "sitemap.xml", f"пропал {u}")
    llms = read("llms.txt")
    for f in NEW_PAGES:
        if f"{SITE}/{f}" not in sm_new:
            fail("R-SITEMAP", "sitemap.xml", f"нет {SITE}/{f}")
        if f"{SITE}/{f}" not in llms:
            fail("R-LLMS", "llms.txt", f"нет {SITE}/{f}")

    # R-CONTACTS on the home page
    for c in HOME_CONTACTS:
        if f'href="{c}"' not in home_raw:
            fail("R-CONTACTS", "index.html", f"нет ссылки {c}")

    for e in errors:
        print(e)
    print(f"pages={len(all_pages)} violations={len(errors)}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
