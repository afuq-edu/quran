#!/usr/bin/env node
/* Open every app in a real browser and check it the way a student would use it (owner, 2026-10-30): phone, tablet and
   desktop sizes, light and dark, then offline. Reports script errors, missing files, sideways scrolling, a page that is not
   Arabic right-to-left, buttons too small for a finger (under 44 px), images without alt text, and whether the app still
   opens with no internet after its first visit. Saves a screenshot of each view.
   Needs Node and Playwright (npm i -D playwright && npx playwright install chromium; preinstalled in Claude's cloud sessions).
   Usage: node tools/app_check.mjs [slug ...] [--out DIR]     (default: the home page and every app in apps.json; exit 1 on errors) */
import { createRequire } from 'module';
import http from 'http';
import fs from 'fs';
import os from 'os';
import path from 'path';
import { fileURLToPath } from 'url';

const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const VIEWS = [['phone', 360, 740], ['tablet', 820, 1180], ['desktop', 1280, 800]];
const TYPES = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript', '.mjs': 'text/javascript',
  '.json': 'application/json', '.webmanifest': 'application/manifest+json', '.svg': 'image/svg+xml', '.png': 'image/png',
  '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.mp3': 'audio/mpeg', '.woff2': 'font/woff2' };

let args = process.argv.slice(2), out = path.join(os.tmpdir(), 'app-check');
const oi = args.indexOf('--out');
if (oi >= 0) { out = path.resolve(args[oi + 1]); args.splice(oi, 2); }
fs.mkdirSync(out, { recursive: true });
const reg = JSON.parse(fs.readFileSync(path.join(ROOT, 'apps.json'), 'utf8'));
const targets = args.length ? args.map(s => ['apps/' + s + '/', s]) : [['', 'home'], ...reg.apps.map(a => ['apps/' + a.slug + '/', a.slug])];

// the site is served under /quran/ on GitHub Pages; serve it the same way so relative links behave alike
const server = http.createServer((req, res) => {
  let p = decodeURIComponent(new URL(req.url, 'http://x').pathname);
  if (!p.startsWith('/quran/')) { res.writeHead(404); return res.end(); }
  p = path.join(ROOT, p.slice('/quran/'.length));
  if (!p.startsWith(ROOT)) { res.writeHead(403); return res.end(); }
  if (fs.existsSync(p) && fs.statSync(p).isDirectory()) p = path.join(p, 'index.html');
  if (!fs.existsSync(p)) { res.writeHead(404); return res.end('not found'); }
  res.writeHead(200, { 'content-type': TYPES[path.extname(p)] || 'application/octet-stream' });
  fs.createReadStream(p).pipe(res);
}).listen(0, '127.0.0.1');
await new Promise(r => server.on('listening', r));
const BASE = `http://127.0.0.1:${server.address().port}/quran/`;

// behind an HTTPS proxy (as in Claude's cloud sessions) let the browser use it too, so the Google fonts load
const PROXY = process.env.HTTPS_PROXY || process.env.https_proxy;
const browser = await chromium.launch(PROXY ? { proxy: { server: PROXY, bypass: '127.0.0.1' } } : {});
let errors = 0;
for (const [rel, name] of targets) {
  const problems = new Set(), notes = new Set();
  for (const [view, w, h] of VIEWS) for (const scheme of ['light', 'dark']) {
    const ctx = await browser.newContext({ viewport: { width: w, height: h }, colorScheme: scheme, locale: 'ar', hasTouch: view !== 'desktop', ignoreHTTPSErrors: !!PROXY });
    const page = await ctx.newPage();
    page.on('pageerror', e => problems.add('خطأ في السكربت: ' + e.message));
    page.on('console', m => { if (m.type() === 'error' && !/^Failed to load resource/.test(m.text())) problems.add('خطأ في الصفحة: ' + m.text().slice(0, 160)); });
    page.on('response', r => { if (r.status() >= 400 && r.url().startsWith(BASE)) problems.add('ملف غير موجود: ' + r.url().slice(BASE.length)); });
    page.on('requestfailed', r => { if (!r.url().startsWith(BASE)) notes.add('تعذر تحميل ملف خارجي (يحتاج إنترنت): ' + new URL(r.url()).host); });
    await page.goto(BASE + rel, { waitUntil: 'networkidle' }).catch(e => problems.add('لم تفتح الصفحة: ' + e.message));
    await page.waitForTimeout(300);
    const r = await page.evaluate(phone => {
      const d = document.documentElement, small = [];
      for (const el of document.querySelectorAll('button, select, input, textarea, [role=button], .btn, nav a, header a')) {
        const b = el.getBoundingClientRect();
        if (b.width && b.height && (b.width < 44 || b.height < 44) && getComputedStyle(el).visibility !== 'hidden')
          small.push((el.getAttribute('aria-label') || el.textContent || el.tagName).trim().slice(0, 24) + ` (${Math.round(b.width)}×${Math.round(b.height)})`);
      }
      return { overflow: d.scrollWidth - d.clientWidth, lang: d.lang, dir: d.dir, title: document.title,
        noAlt: [...document.images].filter(i => !i.hasAttribute('alt')).length, small: phone ? small.slice(0, 6) : [],
        empty: (document.body.innerText || '').trim().length < 20 };
    }, view === 'phone');
    if (r.overflow > 1) problems.add(`تمرير أفقي على ${view} (${r.overflow} px زائدة)`);
    if (r.lang !== 'ar' || r.dir !== 'rtl') problems.add(`الصفحة ليست lang="ar" dir="rtl" (lang=${r.lang || '—'} dir=${r.dir || '—'})`);
    if (!r.title) problems.add('لا عنوان للصفحة <title>');
    if (r.empty) problems.add(`الصفحة فارغة تقريبًا على ${view}`);
    if (r.noAlt) notes.add(`${r.noAlt} صورة بلا نص بديل alt`);
    if (r.small.length) notes.add('عناصر أصغر من 44 px للمس: ' + r.small.join('، '));
    await page.screenshot({ path: path.join(out, `${name}-${view}-${scheme}.png`), fullPage: false });

    if (view === 'phone' && scheme === 'light' && rel) {     // offline: needs tools/pwa.py
      const sw = await page.evaluate(async () => {
        if (!('serviceWorker' in navigator)) return 'none';
        const reg = await Promise.race([navigator.serviceWorker.ready, new Promise(r => setTimeout(() => r(null), 4000))]);
        return reg ? 'ok' : 'none';
      });
      if (sw !== 'ok') notes.add('لا يعمل بلا إنترنت بعد (شغّل tools/pwa.py)');
      else {
        await page.waitForTimeout(500);
        await ctx.setOffline(true);
        const ok = await page.reload({ waitUntil: 'load' }).then(() => page.evaluate(() => (document.body.innerText || '').trim().length > 20)).catch(() => false);
        if (!ok) problems.add('لا يفتح بلا إنترنت مع أن فيه service worker');
        else notes.add('يعمل بلا إنترنت ✓');
        await ctx.setOffline(false);
      }
    }
    await ctx.close();
  }
  errors += problems.size;
  console.log(`\n${problems.size ? '✗' : '✓'} ${name}  (${BASE}${rel})`);
  for (const p of problems) console.log('  ✗ ' + p);
  for (const n of notes) console.log('  · ' + n);
}
console.log(`\nالصور في: ${out}`);
await browser.close();
server.close();
process.exit(errors ? 1 : 0);
