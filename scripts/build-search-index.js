#!/usr/bin/env node
/**
 * build-search-index.js
 * Reads diary.json, experiments.json, articles.json
 * and generates data/search-index.json for Fuse.js full-site search.
 */
'use strict';

const fs = require('fs');
const path = require('path');

const DATA_DIR = path.join(__dirname, '..', 'data');

function readJSON(file) {
  const fp = path.join(DATA_DIR, file);
  if (!fs.existsSync(fp)) {
    console.warn(`[warn] ${file} not found, skipping.`);
    return [];
  }
  return JSON.parse(fs.readFileSync(fp, 'utf-8'));
}

const diary = readJSON('diary.json');
const experiments = readJSON('experiments.json');
const articles = readJSON('articles.json');

const index = [];

// Diary entries
diary.forEach(entry => {
  index.push({
    type: 'diary',
    title_zh: entry.summary_zh || '',
    title_en: entry.summary_en || '',
    content_zh: entry.details_zh || '',
    content_en: entry.details_en || '',
    tags: entry.tags || [],
    date: entry.date || '',
    url: 'diary.html',
    codename: entry.codename || ''
  });
});

// Experiments
experiments.forEach(entry => {
  index.push({
    type: 'experiment',
    title_zh: entry.title_zh || '',
    title_en: entry.title_en || '',
    content_zh: entry.result_zh || '',
    content_en: entry.result_en || '',
    tags: entry.tags || [],
    date: entry.date || '',
    url: 'experiments.html',
    codename: entry.codename || ''
  });
});

// Articles
articles.forEach(entry => {
  // Determine URL: if content_type is 'link', use content_url directly; otherwise blog.html
  let url = 'blog.html';
  if (entry.content_url) {
    url = entry.content_url;
  }

  index.push({
    type: 'article',
    title_zh: entry.title_zh || entry.title || '',
    title_en: entry.title_en || '',
    content_zh: entry.summary_zh || entry.content_zh || '',
    content_en: entry.summary_en || entry.content_en || '',
    tags: entry.tags || [],
    date: entry.date || '',
    url: url,
    codename: ''
  });
});

const outPath = path.join(DATA_DIR, 'search-index.json');
fs.writeFileSync(outPath, JSON.stringify(index, null, 2), 'utf-8');

console.log(`[build-search-index] Generated ${index.length} entries:`);
console.log(`  diary:       ${diary.length}`);
console.log(`  experiments: ${experiments.length}`);
console.log(`  articles:    ${articles.length}`);
console.log(`  → ${outPath}`);
