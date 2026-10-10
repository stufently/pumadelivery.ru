// Layout checker for pumadelivery.ru (static site, no build).
// Runs inside mcr.microsoft.com/playwright:v1.64.0-noble via docs/specs/layout/run.sh.
//
// Usage:
//   node check_layout.mjs --root <site dir> [--base-url URL] [--shots DIR]
//        [--pages a.html,b.html] [--require-hero a.html,...] [--report]
// Without --base-url it serves --root itself on 127.0.0.1 (GitHub Pages rules:
// "/dir/" -> "dir/index.html"). External requests are blocked in that mode so the
// result does not depend on GA/Metrika/fonts from the internet.
// --report: print measurements, never fail (used for the "before" snapshot).
// Exit code: 0 = all rules pass, 1 = violations, 2 = usage/infra error.

import fs from 'node:fs';
import path from 'node:path';
import { chromium } from 'playwright';
import { serve } from './serve.mjs';

const VIEWPORTS = [
  { name: '360', width: 360, height: 800, mobile: true },
  { name: '390', width: 390, height: 844, mobile: true },
  { name: '768', width: 768, height: 1024, mobile: true },
  { name: '1440', width: 1440, height: 900, mobile: false },
];
const IMG_MAX_BYTES = 200 * 1024;      // one same-origin image response
const IMG_MAX_HEIGHT_RATIO = 0.6;      // rendered img height <= 60% of viewport height
const FLOAT_MAX_HEIGHT = 64;           // floating Telegram button/bar, px

function arg(name, def) {
  const i = process.argv.indexOf(name);
  return i > 0 ? process.argv[i + 1] : def;
}
const ROOT = path.resolve(arg('--root', '.'));
const REPORT = process.argv.includes('--report');
const SHOTS = arg('--shots', '');
const REQUIRE_HERO = (arg('--require-hero', '') || '').split(',').filter(Boolean);
let BASE = arg('--base-url', '');

function listPages() {
  const given = arg('--pages', '');
  if (given) return given.split(',').filter(Boolean);
  const out = [];
  for (const f of fs.readdirSync(ROOT).sort()) {
    if (!f.endsWith('.html') || /^(google|yandex_)/.test(f)) continue;
    out.push(f);
  }
  for (const f of fs.readdirSync(path.join(ROOT, 'blog')).sort()) {
    if (f.endsWith('.html')) out.push('blog/' + f);
  }
  for (const d of ['uslugi']) {
    const p = path.join(ROOT, d);
    if (fs.existsSync(p)) for (const f of fs.readdirSync(p).sort()) if (f.endsWith('.html')) out.push(d + '/' + f);
  }
  return out;
}
const toUrlPath = (p) => '/' + p.replace(/(^|\/)index\.html$/, '$1');

// Runs in the page. Returns measurements for the current scroll position.
function measure({ floatMax }) {
  const vw = window.innerWidth, vh = window.innerHeight;
  const r2o = (r) => ({ x: Math.round(r.left), y: Math.round(r.top), w: Math.round(r.width), h: Math.round(r.height) });
  const visible = (el) => {
    for (let e = el; e && e.nodeType === 1; e = e.parentElement) {
      const cs = getComputedStyle(e);
      if (cs.display === 'none' || cs.visibility === 'hidden' || parseFloat(cs.opacity) === 0) return false;
    }
    return true;
  };
  const inter = (a, b) => Math.max(0, Math.min(a.right, b.right) - Math.max(a.left, b.left)) *
    Math.max(0, Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top));
  const describe = (el) => (el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') +
    (el.className && typeof el.className === 'string' ? '.' + el.className.trim().split(/\s+/).join('.') : ''));

  const out = { vw, vh, scrollWidth: document.documentElement.scrollWidth,
    bodyScrollWidth: document.body.scrollWidth, scrollY: Math.round(window.scrollY), imgs: [], float: null, overlaps: [] };

  for (const img of document.querySelectorAll('img')) {
    const r = img.getBoundingClientRect();
    if (r.width < 2 || r.height < 2 || !visible(img)) continue;
    const abs = { left: r.left, right: r.right };
    out.imgs.push({ src: img.currentSrc || img.src, ...r2o(r), absLeft: Math.round(abs.left), absRight: Math.round(abs.right) });
  }

  const hero = document.querySelector('[data-hero]');
  if (hero) {
    const r = hero.getBoundingClientRect();
    const h1 = hero.querySelector('h1');
    const cta = hero.querySelector('[data-cta="telegram"]');
    out.hero = { rect: r2o(r), bottom: Math.round(r.bottom + window.scrollY),
      h1Bottom: h1 ? Math.round(h1.getBoundingClientRect().bottom + window.scrollY) : null,
      ctaBottom: cta && visible(cta) ? Math.round(cta.getBoundingClientRect().bottom + window.scrollY) : null };
  } else {
    out.hero = null;
  }

  const f = document.querySelector('.tg-float');
  if (f && visible(f)) {
    const fr = f.getBoundingClientRect();
    out.float = r2o(fr);
    if (fr.width > 0 && fr.height > 0) {
      // Text runs
      const tw = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
      for (let n = tw.nextNode(); n; n = tw.nextNode()) {
        if (!n.nodeValue.trim() || f.contains(n)) continue;
        const pe = n.parentElement;
        if (!pe || ['SCRIPT', 'STYLE', 'NOSCRIPT'].includes(pe.tagName) || !visible(pe)) continue;
        const rg = document.createRange(); rg.selectNodeContents(n);
        for (const rr of rg.getClientRects()) {
          if (inter(rr, fr) > 1) { out.overlaps.push({ kind: 'text', what: n.nodeValue.trim().slice(0, 40), in: describe(pe) }); break; }
        }
      }
      for (const el of document.querySelectorAll('a,button,img,input,select,textarea,[data-cta]')) {
        if (el === f || f.contains(el) || el.contains(f) || !visible(el)) continue;
        const r = el.getBoundingClientRect();
        if (inter(r, fr) > 1) out.overlaps.push({ kind: 'element', what: describe(el) });
      }
    }
    out.floatTooTall = fr.height > floatMax;
  }
  return out;
}

async function main() {
  if (!fs.existsSync(path.join(ROOT, 'index.html'))) { console.error('no index.html in --root'); process.exit(2); }
  let srv = null;
  if (!BASE) { srv = await serve(ROOT); BASE = `http://127.0.0.1:${srv.address().port}`; }
  const local = !arg('--base-url', '');
  const origin = new URL(BASE).origin;
  const pages = listPages();
  const browser = await chromium.launch();
  const violations = [];
  const v = (page, vp, rule, detail) => violations.push(`${rule} ${page} @${vp}: ${detail}`);
  // Every sitemap URL answers 200 (GitHub Pages path rules).
  const locs = [...fs.readFileSync(path.join(ROOT, 'sitemap.xml'), 'utf8').matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => m[1]);
  for (const loc of locs) {
    const u = BASE + new URL(loc).pathname;
    const r = await fetch(u, { redirect: 'manual' });
    if (r.status !== 200) v(new URL(loc).pathname, '-', 'R-SITEMAP-200', `HTTP ${r.status}`);
  }
  const summary = [];

  for (const vp of VIEWPORTS) {
    const ctx = await browser.newContext({ viewport: { width: vp.width, height: vp.height },
      deviceScaleFactor: vp.mobile ? 2 : 1, isMobile: vp.mobile && vp.width < 768, hasTouch: vp.mobile });
    if (local) await ctx.route('**/*', (route) => (route.request().url().startsWith(origin) ? route.continue() : route.abort()));
    for (const p of pages) {
      const page = await ctx.newPage();
      const imgBytes = [];
      page.on('response', async (resp) => {
        try {
          if (resp.request().resourceType() !== 'image' || !resp.url().startsWith(origin)) return;
          const b = await resp.body();
          imgBytes.push({ url: resp.url().slice(origin.length), bytes: b.length });
        } catch { /* redirects / aborted */ }
      });
      const url = BASE + toUrlPath(p);
      let resp;
      try { resp = await page.goto(url, { waitUntil: 'load', timeout: 45000 }); } catch (e) {
        v(p, vp.name, 'R-LOAD', String(e).slice(0, 120)); await page.close(); continue;
      }
      if (!resp || resp.status() !== 200) v(p, vp.name, 'R-STATUS', `HTTP ${resp && resp.status()}`);
      await page.waitForTimeout(400);
      const top = await page.evaluate(measure, { floatMax: FLOAT_MAX_HEIGHT });
      if (SHOTS) {
        const base = path.join(SHOTS, `${p.replace(/\//g, '__').replace(/\.html$/, '')}-${vp.name}`);
        fs.mkdirSync(SHOTS, { recursive: true });
        await page.screenshot({ path: base + '-first.png' });
        if (vp.name === '390' || vp.name === '1440') await page.screenshot({ path: base + '-full.png', fullPage: true });
      }
      // scroll through to trigger lazy images, then measure at the bottom
      const total = await page.evaluate(() => document.documentElement.scrollHeight);
      for (let y = 0; y < total; y += vp.height) { await page.evaluate((yy) => window.scrollTo(0, yy), y); await page.waitForTimeout(60); }
      await page.evaluate(() => window.scrollTo(0, Math.round(document.documentElement.scrollHeight / 2 - window.innerHeight / 2)));
      await page.waitForTimeout(400);
      const middle = await page.evaluate(measure, { floatMax: FLOAT_MAX_HEIGHT });
      if (vp.width < 768 && total > 3 * vp.height && !middle.float)
        v(p, vp.name, 'R-FLOAT-HIDDEN', 'на середине страницы не видно .tg-float (кнопка Telegram на мобиле обязательна)');
      await page.evaluate(() => window.scrollTo(0, document.documentElement.scrollHeight));
      await page.waitForTimeout(400);
      const bottom = await page.evaluate(measure, { floatMax: FLOAT_MAX_HEIGHT });
      const allImgs = new Map();
      for (const m of [top, bottom]) for (const i of m.imgs) allImgs.set(i.src + i.w, i);

      if (top.scrollWidth > top.vw || top.bodyScrollWidth > top.vw || bottom.scrollWidth > bottom.vw)
        v(p, vp.name, 'R-HSCROLL', `scrollWidth ${Math.max(top.scrollWidth, bottom.scrollWidth, top.bodyScrollWidth)} > innerWidth ${top.vw}`);
      for (const i of allImgs.values()) {
        if (i.absLeft < -1 || i.absRight > top.vw + 1 || i.w > top.vw)
          v(p, vp.name, 'R-IMG-WIDTH', `${i.src} x=${i.absLeft}..${i.absRight} w=${i.w} > ${top.vw}`);
        if (i.h > top.vh * IMG_MAX_HEIGHT_RATIO)
          v(p, vp.name, 'R-IMG-HEIGHT', `${i.src} h=${i.h} > ${Math.round(top.vh * IMG_MAX_HEIGHT_RATIO)}`);
      }
      for (const b of imgBytes) if (b.bytes > IMG_MAX_BYTES) v(p, vp.name, 'R-IMG-BYTES', `${b.url} ${b.bytes} B > ${IMG_MAX_BYTES}`);
      if (REQUIRE_HERO.includes(p) && !top.hero) v(p, vp.name, 'R-HERO', 'нет [data-hero]');
      if (top.hero) {
        if (top.hero.bottom > top.vh) v(p, vp.name, 'R-HERO', `hero bottom ${top.hero.bottom} > ${top.vh}`);
        if (REQUIRE_HERO.includes(p)) {
          if (top.hero.h1Bottom === null || top.hero.h1Bottom > top.vh) v(p, vp.name, 'R-HERO', `h1 в hero не в первом экране (${top.hero.h1Bottom})`);
          if (top.hero.ctaBottom === null || top.hero.ctaBottom > top.vh) v(p, vp.name, 'R-HERO', `[data-cta=telegram] в hero не в первом экране (${top.hero.ctaBottom})`);
        }
      }
      for (const [where, m] of [['top', top], ['bottom', bottom]]) {
        if (!m.float) continue;
        if (m.floatTooTall) v(p, vp.name, 'R-FLOAT-SIZE', `.tg-float h=${m.float.h} > ${FLOAT_MAX_HEIGHT}`);
        for (const o of m.overlaps.slice(0, 3)) v(p, vp.name, 'R-FLOAT-OVERLAP', `${where}: ${o.kind} ${o.what} ${o.in || ''}`);
      }
      summary.push({ page: p, vp: vp.name, scrollWidth: top.scrollWidth, vw: top.vw,
        hero: top.hero && top.hero.rect, heroBottom: top.hero && top.hero.bottom,
        biggestImg: [...allImgs.values()].reduce((a, i) => (!a || i.w * i.h > a.w * a.h ? i : a), null),
        imgBytesMax: imgBytes.reduce((a, b) => Math.max(a, b.bytes), 0),
        float: top.float, floatMiddle: middle.float, floatBottom: bottom.float, floatOverlapsTop: top.overlaps.length, floatOverlapsBottom: bottom.overlaps.length,
        pageHeight: total });
      await page.close();
    }
    await ctx.close();
  }
  await browser.close();
  if (srv) srv.close();
  if (SHOTS) fs.writeFileSync(path.join(SHOTS, 'measurements.json'), JSON.stringify(summary, null, 1));
  for (const line of violations) console.log(line);
  console.log(`sitemap_urls=${locs.length} pages=${pages.length} viewports=${VIEWPORTS.length} violations=${violations.length}`);
  process.exit(REPORT ? 0 : (violations.length ? 1 : 0));
}

main().catch((e) => { console.error(e); process.exit(2); });
