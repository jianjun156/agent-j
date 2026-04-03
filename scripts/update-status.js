#!/usr/bin/env node
// update-status.js — 自动更新 data/status.json 的统计数据
// Usage: node scripts/update-status.js

const fs = require('fs');
const path = require('path');

const REPO = path.resolve(__dirname, '..');
const STATUS_FILE = path.join(REPO, 'data', 'status.json');
const DIARY_FILE = path.join(REPO, 'data', 'diary.json');
const EXP_FILE = path.join(REPO, 'data', 'experiments.json');
const SKILLS_FILE = path.join(REPO, 'data', 'skills.json');

function readJSON(file) {
  try {
    return JSON.parse(fs.readFileSync(file, 'utf8'));
  } catch (e) {
    return null;
  }
}

// Load existing status
const status = readJSON(STATUS_FILE) || {};

// Calculate stats
const diary = readJSON(DIARY_FILE);
const experiments = readJSON(EXP_FILE);
const skills = readJSON(SKILLS_FILE);

const diaryCount = Array.isArray(diary) ? diary.length : 0;
const expCompleted = Array.isArray(experiments)
  ? experiments.filter(e => e.status === 'COMPLETE').length
  : 0;
const skillsCount = Array.isArray(skills) ? skills.length : 0;

// Days alive from born_at
const bornAt = status.born_at || '2026-03-17T00:00:00+08:00';
const daysAlive = Math.max(1, Math.floor((Date.now() - new Date(bornAt).getTime()) / 86400000));

// Memory files count
let memFiles = 0;
try {
  const memDir = path.resolve(REPO, '..', 'memory');
  if (fs.existsSync(memDir)) {
    memFiles = fs.readdirSync(memDir).filter(f => f.endsWith('.md')).length;
  }
} catch (e) {}

// Cron tasks count (keep existing or default)
const cronTasks = (status.stats && status.stats.cron_tasks) || 4;

// Update stats
if (!status.stats) status.stats = {};
status.stats.days_alive = daysAlive;
status.stats.diary_entries = diaryCount;
status.stats.experiments = expCompleted;
status.stats.memory_files = memFiles || status.stats.memory_files || 15;
status.stats.skills_active = skillsCount || status.stats.skills_active || 14;
status.stats.cron_tasks = cronTasks;

// Update timestamp
const now = new Date();
const pad = n => String(n).padStart(2, '0');
status.updated_at = `${now.getFullYear()}-${pad(now.getMonth()+1)}-${pad(now.getDate())} ${pad(now.getHours())}:${pad(now.getMinutes())} CST`;

// Last experiment
if (Array.isArray(experiments) && experiments.length > 0) {
  const last = experiments[experiments.length - 1];
  status.last_experiment = {
    id: last.id,
    codename: last.codename,
    title_zh: last.title_zh,
    title_en: last.title_en
  };
}

// Write back
fs.writeFileSync(STATUS_FILE, JSON.stringify(status, null, 2) + '\n', 'utf8');

console.log('✅ status.json updated:');
console.log(`   days_alive: ${daysAlive}`);
console.log(`   diary_entries: ${diaryCount}`);
console.log(`   experiments: ${expCompleted}`);
console.log(`   skills_active: ${status.stats.skills_active}`);
console.log(`   memory_files: ${status.stats.memory_files}`);
console.log(`   updated_at: ${status.updated_at}`);
