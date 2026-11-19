#!/usr/bin/env node
// SEO/metadata guard for the Sada repository and the bilingual GitHub Pages site.
// Run from the repo root:  node scripts/seo/check-seo.mjs
// It is intentionally dependency-free (CI has Node, the site has no build step).
import { readFile, stat } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const repo = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..');
const failures = [];
const notes = [];
const fail = (msg) => failures.push(msg);
const ok = (msg) => notes.push('ok   ' + msg);
const read = (p) => readFile(join(repo, p), 'utf8');

// ---------- helpers ----------
const pngSize = async (p) => {
  const b = await readFile(join(repo, p));
  if (b.length < 24 || b.toString('ascii', 1, 4) !== 'PNG') return null;
  return { width: b.readUInt32BE(16), height: b.readUInt32BE(20), bytes: b.length };
};
const slug = (s) =>
  s.toLowerCase().replace(/<[^>]+>/g, '').replace(/[^\p{L}\p{N}\s-]/gu, '').trim().replace(/\s+/g, '-');
const plain = (html) => html.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
const metaTag = (html, attr, name) => {
  const re = new RegExp('<meta[^>]*' + attr + '=["\']' + name + '["\'][^>]*>', 'i');
  const tag = html.match(re)?.[0];
  return tag ? tag.match(/content=["']([^"']*)["']/i)?.[1] ?? '' : null;
};

// ---------- version ----------
const tauri = JSON.parse(await read('desktop/src-tauri/tauri.conf.json'));
const version = tauri.version;
if (!/^\d+\.\d+\.\d+$/.test(version)) fail('tauri.conf.json version is not semver: ' + version);

// ---------- site pages ----------
const pages = [
  { file: 'site/index.html', lang: 'ar', canonical: 'https://alshahia.github.io/sada/', hreflangAr: 'https://alshahia.github.io/sada/' },
  { file: 'site/en/index.html', lang: 'en', canonical: 'https://alshahia.github.io/sada/en/', hreflangAr: 'https://alshahia.github.io/sada/' },
];
for (const page of pages) {
  const html = await read(page.file);
  const head = html.slice(0, html.indexOf('</head>'));
  const title = plain(head.match(/<title>([\s\S]*?)<\/title>/)?.[1] ?? '');
  const description = metaTag(head, 'name', 'description') ?? '';
  if (plain(head).length < 500) fail(page.file + ': head is suspiciously short');
  if (title.length < 15 || title.length > 70) fail(page.file + ': title length ' + title.length + ' (want 15-70): ' + title);
  if (description.length < 80 || description.length > 170) fail(page.file + ': meta description length ' + description.length + ' (want 80-170)');
  if (metaTag(head, 'name', 'robots')?.includes('noindex')) fail(page.file + ': home page must be indexable');
  const canonical = head.match(/<link rel="canonical" href="([^"]+)"/)?.[1];
  if (canonical !== page.canonical) fail(page.file + ': canonical is ' + canonical);
  if (!/<html lang="/.test(html)) fail(page.file + ': missing html lang');
  if (!new RegExp('\\bdir="' + (page.lang === 'ar' ? 'rtl' : 'ltr') + '"').test(html)) fail(page.file + ': wrong dir for ' + page.lang);
  const hreflangs = [...head.matchAll(/hreflang="([^"]+)" href="([^"]+)"/g)].map((m) => [m[1], m[2]]);
  for (const code of ['ar', 'en', 'x-default']) {
    if (!hreflangs.some(([c]) => c === code)) fail(page.file + ': missing hreflang ' + code);
  }
  const ogImage = metaTag(head, 'property', 'og:image') ?? '';
  if (!ogImage.includes('/assets/social-card-')) fail(page.file + ': og:image does not point at a social card: ' + ogImage);
  if (metaTag(head, 'property', 'og:image:width') !== '1200' || metaTag(head, 'property', 'og:image:height') !== '630') {
    fail(page.file + ': og:image must declare 1200x630');
  }
  if (!metaTag(head, 'property', 'og:image:alt') && !metaTag(head, 'name', 'twitter:image:alt')) fail(page.file + ': missing social image alt text');
  if (metaTag(head, 'name', 'twitter:card') !== 'summary_large_image') fail(page.file + ': twitter card must be summary_large_image');
  const preloads = [...head.matchAll(/rel="preload"[^>]*as="font"/g)].length;
  if (preloads === 0) fail(page.file + ': no font preloads');
  const json = head.match(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/)?.[1];
  if (!json) { fail(page.file + ': no JSON-LD'); continue; }
  let data;
  try { data = JSON.parse(json); } catch (e) { fail(page.file + ': JSON-LD is not valid JSON: ' + e.message); continue; }
  const types = (data['@graph'] ?? []).map((n) => n['@type']);
  for (const need of ['WebSite', 'SoftwareApplication', 'FAQPage']) if (!types.includes(need)) fail(page.file + ': JSON-LD missing ' + need);
  const app = data['@graph']?.find((n) => n['@type'] === 'SoftwareApplication');
  if (app) {
    if (app.softwareVersion !== version) fail(page.file + ': schema softwareVersion ' + app.softwareVersion + ' != ' + version);
    if (!Array.isArray(app.screenshot) || app.screenshot.length < 2) fail(page.file + ': schema needs >=2 screenshots');
    const faq = data['@graph']?.find((n) => n['@type'] === 'FAQPage');
    if (!Array.isArray(faq?.mainEntity) || faq.mainEntity.length < 6) fail(page.file + ': FAQPage needs >=6 questions');
    // Google requires every FAQ answer/name marked up to be visible on the page.
    const bodyText = html.slice(html.indexOf('</head>'));
    for (const question of faq?.mainEntity ?? []) {
      if (!bodyText.includes(question.name)) fail(page.file + ': FAQ question is marked up but not visible: ' + question.name);
    }
  }
  const images = [...html.matchAll(/<img[^>]*src="([^"]+)"/g)].map((m) => m[1]).filter((s) => !s.startsWith('http'));
  for (const img of images) {
    const p = join(dirname(page.file), img);
    if (!(await stat(join(repo, p)).catch(() => null))) fail(page.file + ': broken image ' + img);
  }
  ok(page.file + ': meta, hreflang, JSON-LD, ' + version);
}

// ---------- social cards and icons ----------
for (const [p, w, h] of [
  ['site/assets/social-card-ar.png', 1200, 630],
  ['site/assets/social-card-en.png', 1200, 630],
  ['site/assets/apple-touch-icon.png', 180, 180],
  ['site/assets/icon-512.png', 512, 512],
]) {
  const size = await pngSize(p);
  if (!size) fail(p + ': missing or not a PNG');
  else if (size.width !== w || size.height !== h) fail(p + ': is ' + size.width + 'x' + size.height + ', want ' + w + 'x' + h);
  else ok(p + ': ' + w + 'x' + h);
}

// ---------- robots and sitemap ----------
const robots = await read('site/robots.txt');
if (!/^User-agent: \*/m.test(robots)) fail('robots.txt: missing User-agent: *');
if (!robots.includes('Sitemap: https://alshahia.github.io/sada/sitemap.xml')) fail('robots.txt: missing Sitemap line');
const sitemap = await read('site/sitemap.xml');
if (!sitemap.startsWith('<?xml')) fail('sitemap.xml: missing XML declaration');
for (const loc of ['https://alshahia.github.io/sada/', 'https://alshahia.github.io/sada/en/']) {
  if (!sitemap.includes('<loc>' + loc + '</loc>')) fail('sitemap.xml: missing ' + loc);
}
if ((sitemap.match(/<url>/g) ?? []).length !== 2) fail('sitemap.xml: expected exactly two URLs');
if (/<lastmod>(?!2026-)/.test(sitemap)) fail('sitemap.xml: lastmod looks stale');
const notFound = await read('site/404.html');
if (!/noindex/.test(notFound)) fail('site/404.html: should be noindex');
ok('robots.txt, sitemap.xml, 404.html');

// ---------- READMEs ----------
for (const file of ['README.md', 'README.ar.md']) {
  const md = await read(file);
  if (md.includes('\u27e6')) fail(file + ': placeholder character left in file');
  if ((md.match(/```/g) ?? []).length % 2 !== 0) fail(file + ': odd number of code fences');
  const headings = [...md.matchAll(/^#{2,4}\s+(.+)$/gm)].map((m) => m[1]);
  const anchors = new Set(headings.map(slug));
  const targets = [...md.matchAll(/\]\(([^)]+)\)/g)].map((m) => m[1])
    .concat([...md.matchAll(/src="([^"]+)"/g)].map((m) => m[1]));
  for (const target of targets) {
    if (/^(https?:|mailto:)/.test(target)) continue;
    if (target.startsWith('#')) { if (!anchors.has(target.slice(1))) fail(file + ': broken anchor ' + target); continue; }
    const path = target.split('#')[0];
    if (path && !(await stat(join(repo, path)).catch(() => null))) fail(file + ': broken relative link ' + target);
  }
  for (const asset of ['docs/media/badges/download.svg', 'docs/media/sada-main.png']) {
    if (!md.includes(asset.split('/').pop())) fail(file + ': README does not reference ' + asset);
  }
  if (!md.includes('Sada_' + version + '_x64-setup.exe')) fail(file + ': README does not name the ' + version + ' installer');
  ok(file + ': links, anchors, assets, version');
}

// ---------- repo metadata files ----------
const pkg = JSON.parse(await read('desktop/package.json'));
if (!Array.isArray(pkg.keywords) || pkg.keywords.length < 8) fail('desktop/package.json: add >=8 keywords');
const citation = await read('CITATION.cff');
if (!citation.includes('version: ' + version)) fail('CITATION.cff version != ' + version);
for (const doc of ['docs/DISCOVERABILITY.md', 'docs/SUPPLY-CHAIN.md', 'llms.txt', 'site/llms.txt']) {
  if (!(await stat(join(repo, doc)).catch(() => null))) fail('missing discoverability/support file: ' + doc);
}

// ---------- report ----------
console.log(notes.join('\n'));
if (failures.length) {
  console.error('\nSEO check FAILED (' + failures.length + '):');
  for (const f of failures) console.error(' - ' + f);
  process.exit(1);
}
console.log('\nSEO check passed.');
