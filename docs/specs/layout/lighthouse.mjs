// Lighthouse (mobile preset = Lighthouse default) for pumadelivery.ru pages served locally.
// Runs inside mcr.microsoft.com/playwright:v1.64.0-noble via docs/specs/layout/run.sh.
//
// Usage: node lighthouse.mjs --root <site dir> [--pages index.html,bangkok.html]
//        [--min-perf 90] [--min-a11y 95] [--runs 3]
// Third-party hosts (GA, Metrika, geo.hqdthai.ru, Google Fonts) are blocked so the
// score depends only on the site's own HTML/CSS/JS/images. Score per page = median
// of --runs runs. Exit code: 0 = all pages meet thresholds, 1 = below, 2 = error.

import path from 'node:path';
import lighthouse from 'lighthouse';
import * as chromeLauncher from 'chrome-launcher';
import { chromium } from 'playwright';
import { serve } from './serve.mjs';

function arg(name, def) {
  const i = process.argv.indexOf(name);
  return i > 0 ? process.argv[i + 1] : def;
}
const ROOT = path.resolve(arg('--root', '.'));
const PAGES = arg('--pages', 'index.html,bangkok.html,blog/posylka-iz-tailanda-v-rossiyu.html').split(',').filter(Boolean);
const MIN_PERF = Number(arg('--min-perf', '0'));
const MIN_A11Y = Number(arg('--min-a11y', '0'));
const RUNS = Number(arg('--runs', '3'));
const BLOCK = ['*googletagmanager.com*', '*google-analytics.com*', '*mc.yandex.ru*', '*yandex.ru/metrika*',
  '*mc.yandex.com*', '*geo.hqdthai.ru*', '*fonts.googleapis.com*', '*fonts.gstatic.com*'];

const median = (a) => { const s = [...a].sort((x, y) => x - y); return s[Math.floor(s.length / 2)]; };

async function main() {
  const srv = await serve(ROOT);
  const base = `http://127.0.0.1:${srv.address().port}`;
  const chrome = await chromeLauncher.launch({ chromePath: chromium.executablePath(),
    chromeFlags: ['--headless=new', '--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage'] });
  let bad = 0;
  try {
    for (const p of PAGES) {
      const url = base + '/' + p.replace(/(^|\/)index\.html$/, '$1');
      const perf = [], a11y = [], lcp = [], cls = [];
      for (let i = 0; i < RUNS; i++) {
        const r = await lighthouse(url, { port: chrome.port, output: 'json', logLevel: 'error',
          onlyCategories: ['performance', 'accessibility'], blockedUrlPatterns: BLOCK });
        const lhr = r.lhr;
        if (lhr.runtimeError) throw new Error(`${p}: ${lhr.runtimeError.code} ${lhr.runtimeError.message}`);
        perf.push(Math.round(lhr.categories.performance.score * 100));
        a11y.push(Math.round(lhr.categories.accessibility.score * 100));
        lcp.push(lhr.audits['largest-contentful-paint'].numericValue);
        cls.push(lhr.audits['cumulative-layout-shift'].numericValue);
      }
      const P = median(perf), A = median(a11y);
      const ok = P >= MIN_PERF && A >= MIN_A11Y;
      if (!ok) bad++;
      console.log(`${ok ? 'OK  ' : 'FAIL'} ${p} perf=${P} (runs ${perf.join('/')}) a11y=${A} ` +
        `lcp=${Math.round(median(lcp))}ms cls=${median(cls).toFixed(3)} min-perf=${MIN_PERF} min-a11y=${MIN_A11Y}`);
    }
  } finally {
    await chrome.kill();
    srv.close();
  }
  process.exit(bad ? 1 : 0);
}

main().catch((e) => { console.error(e); process.exit(2); });
