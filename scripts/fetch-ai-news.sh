#!/bin/bash
# fetch-ai-news.sh — cron 入口，调用 ai-x-news skill 的采集脚本（--store 模式）
# Cron: 0 8,18 * * *
set -e
exec bash /Users/jianjun/.openclaw/workspace/skills/ai-x-news/scripts/fetch-ai-news.sh --store
