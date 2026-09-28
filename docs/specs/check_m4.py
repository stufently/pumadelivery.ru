#!/usr/bin/env python3
"""Проверка вехи M4: блок «Седжаро (Sejaro)» в статье о лекарствах из России.

Запуск из корня репо: python3 docs/specs/check_m4.py
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_articles import Page, norm  # noqa: E402

F = "blog/lekarstva-iz-rossii-v-tailand.html"
raw = open(F, encoding="utf-8").read()
p = Page()
p.feed(raw)
text = norm(" ".join(p.text))
fails = []


def fail(rule, detail):
    fails.append(f"FAIL {rule}: {F}: {detail}")


h2 = [norm(re.sub(r"<[^>]+>", "", m)) for m in re.findall(r"<h2[^>]*>(.*?)</h2>", raw, re.S)]
if not any("Седжаро" in h and "Sejaro" in h for h in h2):
    fail("R-H2", f"нет h2 с «Седжаро» и «Sejaro»: {h2}")
for need in ("Седжаро", "Sejaro", "тирзепатид", "30 °C", "30 дней", "пилот"):
    if need not in text:
        fail("R-TEXT", f"в видимом тексте нет {need!r}")
if not re.search(r"(\+2|2)\s*(…|\.\.\.|–|-|до)\s*\+?8\s*°C", text):
    fail("R-TEXT", "нет условия хранения 2–8 °C")
if not re.search(r"(четыре|4)\s+(недельн|укол|доз)", text):
    fail("R-TEXT", "нет факта «4 недельные дозы в ручке»")
if re.search(r"похуд|снижени[ея] веса|сбросить", text, re.I):
    fail("R-MED", "медицинские обещания о весе запрещены")
if "Sejaro" not in " ".join(p.metas.get("description", [])) and "Седжаро" not in " ".join(p.metas.get("description", [])):
    fail("R-DESC", "description не упоминает Седжаро")

faq = []
for blob in re.findall(r'<script type="application/ld\+json">(.*?)</script>', raw, re.S):
    for n in json.loads(blob).get("@graph", []):
        if n.get("@type") == "FAQPage":
            faq = n.get("mainEntity", [])
if not any("Седжаро" in q.get("name", "") and "Sejaro" in q.get("name", "") for q in faq):
    fail("R-FAQ", "нет вопроса FAQ с «Седжаро» и «Sejaro»")

for line in fails:
    print(line, file=sys.stderr)
if fails:
    print(f"FAIL: {len(fails)} нарушений", file=sys.stderr)
    sys.exit(1)
print("OK check_m4")
