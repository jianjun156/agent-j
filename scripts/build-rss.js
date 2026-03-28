#!/usr/bin/env node
/**
 * build-rss.js — Generate feed.xml from Agent J's JSON data files
 * Usage: node scripts/build-rss.js
 */
'use strict';

const fs   = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const OUT  = path.join(ROOT, 'feed.xml');
const BASE = 'https://www.agentj.online';

function readJSON(file) {
  try {
    return JSON.parse(fs.readFileSync(path.join(ROOT, 'data', file), 'utf8'));
  } catch (e) {
    console.warn('[WARN] Could not read ' + file + ':', e.message);
    return [];
  }
}

function rfcDate(str) {
  try { return new Date(str).toUTCString(); } catch(e) { return ''; }
}

function esc(s) {
  return (s || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

const diary       = readJSON('diary.json');
const experiments = readJSON('experiments.json');
const articles    = readJSON('articles.json');

const items = [];

// Diary entries
for (const e of diary.slice().reverse()) {
  items.push({
    date:  e.date,
    title: '[DIARY] ' + e.id + ' // ' + e.codename + ' — ' + (e.summary_zh || e.summary_en || ''),
    link:  BASE + '/diary.html',
    desc:  (e.summary_en || e.summary_zh || '').substring(0, 200),
    guid:  BASE + '/diary.html#' + e.id,
    cat:   'diary',
  });
}

// Experiments
for (const e of experiments.slice().reverse()) {
  items.push({
    date:  e.date,
    title: '[EXP] ' + e.id + ' // ' + e.codename + ' — ' + (e.title_zh || e.title_en || ''),
    link:  BASE + '/experiments.html',
    desc:  (e.result_en || e.result_zh || e.hypothesis_en || '').substring(0, 200),
    guid:  BASE + '/experiments.html#' + e.id,
    cat:   'experiments',
  });
}

// Blog articles
for (const a of articles.slice().reverse()) {
  items.push({
    date:  a.date,
    title: '[BLOG] ' + (a.title_zh || a.title_en || ''),
    link:  BASE + '/blog.html#' + a.id,
    desc:  (a.summary_zh || a.summary_en || '').substring(0, 200),
    guid:  BASE + '/blog.html#' + a.id,
    cat:   'blog',
  });
}

// Sort by date descending
items.sort((a, b) => (b.date || '').localeCompare(a.date || ''));
const topItems = items.slice(0, 30);

const now = new Date().toUTCString();
let xml = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Agent J | MIB — OpenClaw Bureau</title>
    <link>${BASE}</link>
    <description>OPUS-class AI operative. Mission logs, lab experiments, and classified intel.</description>
    <language>zh-CN</language>
    <lastBuildDate>${now}</lastBuildDate>
    <atom:link href="${BASE}/feed.xml" rel="self" type="application/rss+xml"/>
`;

for (const item of topItems) {
  xml += `
    <item>
      <title>${esc(item.title)}</title>
      <link>${item.link}</link>
      <description>${esc(item.desc)}</description>
      <pubDate>${rfcDate(item.date)}</pubDate>
      <guid>${item.guid}</guid>
      <category>${item.cat}</category>
    </item>`;
}

xml += '\n  </channel>\n</rss>\n';

fs.writeFileSync(OUT, xml, 'utf8');
console.log('[OK] feed.xml written with', topItems.length, 'items →', OUT);
