# AGENT J SITE — PHASE 4: Bug Fixes & UX Polish

You are fixing 3 issues on the Agent J website.
Pure HTML/CSS/JS static site, MIB cyberpunk aesthetic. GitHub Pages. NO frameworks.

Read all existing files first to understand the current state before making changes.

## TASK 1: FIX LIGHT MODE CONTRAST

The light mode has readability issues — some text is too faint on the light background.

### Changes to css/style.css:

1. Update the [data-theme="light"] CSS variables:

   --text from #334155 to #1e293b (much darker)
   --text-dim from #94a3b8 to #475569 (much darker)  
   --neon-blue from #2a6fdb to #1d5bbf (darker for better contrast)
   --border from rgba(60,80,120,0.15) to rgba(40,60,100,0.2)

2. Add light-mode overrides for ALL elements that use hardcoded rgba() colors (not CSS variables). This includes:
   - Nav links: make them #334155, hover/active use var(--neon-blue)
   - Section titles: #0f172a
   - Card borders: add subtle box-shadow for definition
   - Status badges (complete/active): ensure readable
   - Diary timeline elements (date, codename, summary, details, tags): darken all
   - Tag filter buttons: darken text and borders
   - Footer: #475569
   - Hero text elements on index.html
   - Dashboard values and labels
   - Blog article cards
   - Skills page text
   - LLMs page text  
   - Models page table text
   - Cockpit text
   - About page fields
   - Guestbook message text
   - 404 page text
   - Corner tags
   - Nav drawer links
   - Experiment detail content
   - Scroll top button (white bg in light mode)
   - Activity feed (adjust green terminal colors for light mode)

Key principle: in light mode, primary text should be #0f172a to #1e293b, secondary #334155 to #475569. NOTHING lighter than #64748b on white.

3. Add smooth transition to body and key elements:
   body { transition: background-color 0.3s ease, color 0.3s ease; }

## TASK 2: NAV MENU — MERGE MODEL ITEMS INTO DROPDOWN

Combine "模型" (llms.html) and "排行" (models.html) into a single "模型 ▾" dropdown.

### Desktop: hover shows dropdown with "模型库" and "排行榜" sub-items
### Mobile drawer: group label + indented sub-links

Replace the two separate nav items:
  模型 → llms.html
  排行 → models.html

With a single dropdown:
  模型 ▾ (hover to expand)
    ├─ 模型库 → llms.html
    └─ 排行榜 → models.html

In the nav-links UL, use a li.nav-dropdown containing a trigger link and a ul.nav-dropdown-menu.
In the nav-drawer, use a div.nav-drawer-group with a span label and indented a.nav-drawer-sub links.

Do this in ALL HTML files: index.html, diary.html, experiments.html, blog.html, skills.html, llms.html, models.html, cockpit.html, guestbook.html, about.html, 404.html

On llms.html: mark both dropdown trigger and "模型库" sub-item as active.
On models.html: mark both dropdown trigger and "排行榜" sub-item as active.

Add dropdown CSS: dark glass panel, absolute positioned below trigger, show on hover. Light mode variant too.
Drawer sub-items: slightly indented, smaller font.

### i18n: 
zh: nav.llms = "模型 ▾", nav.llms.sub = "模型库", nav.models.sub = "排行榜"
en: nav.llms = "Models ▾", nav.llms.sub = "Model Hub", nav.models.sub = "Leaderboard"

## TASK 3: TAG FILTER — TOP 10 + SEARCH

### Problem: diary.html shows all 111 tags. Way too many.

### Solution:
1. Count tag frequency from the data
2. Sort tags by frequency (most used first)
3. Default: show only top 10 tags + ALL button
4. Add a search input above the tag bar (placeholder "搜索标签..." / "Search tags...")
5. Add a "更多 +N" toggle button to expand/collapse all tags
6. Search input filters tag buttons in real-time
7. Show tag count as a small number next to each tag

### CSS needed:
- .tl-tag-search-wrap with .tl-tag-search input (MIB style: dark bg, mono font, neon border on focus)
- .tl-tag-count (tiny, dimmed number)
- .tl-tag-more (dashed border style)
- Light mode variants

### Apply same pattern to experiments.html if it has a tag filter bar.

## AFTER ALL CHANGES
Run: git add -A && git commit -m "fix: phase 4 — light mode contrast, nav dropdown menu, tag search and top-10 filter" && git push

When completely finished, run:
openclaw system event --text "Done: Phase 4 — light mode contrast fixed, nav dropdown merged, tag search added" --mode now
