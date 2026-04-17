"""
Rewrites all dashboard CSS components and home.html with new design.
Run from project root: python build_dashboard.py
"""
import os, pathlib

BASE = pathlib.Path(__file__).parent
STYLES = BASE / "assets" / "styles" / "components"
SCRIPTS = BASE / "assets" / "scripts"

def w(path, content):
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"  wrote {p.relative_to(BASE)}")

# ─────────────────────────────────────────────────────────────
# 1. header/design.css
# ─────────────────────────────────────────────────────────────
w(STYLES / "header" / "design.css", """
header {
    position: fixed; top: 0; left: 0; right: 0;
    height: 52px; width: 100%;
    background: #141e2e;
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 16px; z-index: 1000; box-sizing: border-box;
    border-bottom: 1px solid rgba(62,207,142,0.12);
    box-shadow: 0 2px 16px rgba(0,0,0,0.35);
}
.app_name {
    font-size: 15px; font-weight: 900; letter-spacing: 3px;
    color: #fff; margin: 0; text-transform: uppercase;
}
.streak-badge, .date-badge,
.days, .date {
    display: flex; align-items: center; gap: 5px;
    color: rgba(255,255,255,0.85);
    padding: 5px 10px; border-radius: 20px;
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.1);
    transition: background 0.2s; text-decoration: none;
}
.streak-badge:hover, .date-badge:hover,
.days:hover, .date:hover { background: rgba(255,255,255,0.14); }
.days_img, .calendar {
    width: 15px; height: auto;
    filter: brightness(0) invert(1); opacity: 0.8;
}
.calc_days, .date_text {
    font-size: 12px; font-weight: 700; color: #fff;
}
""".strip())

# ─────────────────────────────────────────────────────────────
# 2. week/design.css
# ─────────────────────────────────────────────────────────────
w(STYLES / "week" / "design.css", """
.week-strip, .week-days {
    display: flex; justify-content: space-between;
    align-items: flex-start; padding: 4px 2px 8px; gap: 2px;
}
.day {
    display: flex; flex-direction: column; align-items: center;
    gap: 4px; flex: 1; cursor: pointer; user-select: none;
    transition: transform 0.15s; padding: 2px;
}
.day:active { transform: scale(0.9); }
.day_name {
    font-size: 10px; font-weight: 600;
    color: rgba(255,255,255,0.38); text-transform: uppercase; letter-spacing: 0.3px;
}
.day_circle {
    width: 34px; height: 34px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    border: 2px solid transparent;
    background: rgba(255,255,255,0.07);
    transition: all 0.2s;
}
.day_date {
    font-size: 13px; font-weight: 700; color: rgba(255,255,255,0.5);
}
.day.today .day_name { color: var(--accent_color); font-weight: 800; }
.day.today .day_circle {
    border-color: var(--accent_color);
    background: rgba(62,207,142,0.15);
    box-shadow: 0 0 10px rgba(62,207,142,0.3);
}
.day.today .day_date { color: var(--accent_color); font-weight: 900; }
.day.has-data .day_circle { background: rgba(62,207,142,0.1); }
""".strip())

# ─────────────────────────────────────────────────────────────
# 3. home/design.css  (hero, calorie ring, quick actions, nutrients)
# ─────────────────────────────────────────────────────────────
w(STYLES / "home" / "design.css", """
/* ── Layout ── */
main { padding-top: 0; padding-bottom: 90px; }

/* ── Hero ── */
.hero {
    background: var(--hero_gradient);
    padding: 12px 16px 20px;
    display: flex; flex-direction: column; gap: 14px;
    position: relative; overflow: hidden;
}
.hero::before {
    content: ''; position: absolute; inset: 0;
    background: radial-gradient(ellipse 70% 50% at 50% 0%, rgba(62,207,142,0.1) 0%, transparent 65%);
    pointer-events: none;
}

/* ── Greeting row ── */
.hero-greeting {
    display: flex; align-items: center; gap: 10px;
}
.hero-greeting-text { flex: 1; }
.hero-greeting-sub { font-size: 11px; color: rgba(255,255,255,0.55); font-weight: 500; }
.hero-greeting-name { font-size: 18px; font-weight: 800; color: #fff; line-height: 1.2; }
.hero-avatar {
    width: 40px; height: 40px; border-radius: 50%;
    background: rgba(255,255,255,0.1); display: flex; align-items: center;
    justify-content: center; font-size: 20px;
    border: 1.5px solid rgba(255,255,255,0.2);
}

/* ── Calorie section ── */
.calorie-section {
    display: flex; align-items: center;
    justify-content: space-between; gap: 6px; padding: 4px 0;
}
.cal-side {
    display: flex; flex-direction: column;
    align-items: center; gap: 4px; flex: 1;
}
.cal-icon {
    width: 28px; height: 28px;
    filter: invert(76%) sepia(38%) saturate(558%) hue-rotate(101deg) brightness(95%);
}
.cal-side-val { font-size: 17px; font-weight: 800; color: #fff; line-height: 1; }
.cal-side-lbl { font-size: 10px; color: rgba(255,255,255,0.6); font-weight: 500; }

/* ── Calorie ring ── */
.cal-ring-wrap {
    position: relative; width: 148px; height: 148px; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
}
.cal-ring-svg { width: 148px; height: 148px; transform: rotate(-90deg); }
.ring-bg { fill: none; stroke: rgba(255,255,255,0.1); stroke-width: 13; }
.ring-fill {
    fill: none; stroke: url(#ringGrad); stroke-width: 13; stroke-linecap: round;
    transition: stroke-dashoffset 1s cubic-bezier(.4,0,.2,1), stroke 0.4s;
}
.ring-center {
    position: absolute; inset: 0;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center; gap: 2px;
}
.ring-kcal { font-size: 30px; font-weight: 900; color: #fff; line-height: 1; }
.ring-goal-txt { font-size: 11px; color: rgba(255,255,255,0.55); font-weight: 500; }
.ring-pct-badge {
    font-size: 12px; font-weight: 800;
    background: rgba(62,207,142,0.2); color: var(--accent_color);
    padding: 2px 10px; border-radius: 20px; margin-top: 3px;
    border: 1px solid rgba(62,207,142,0.35);
    transition: background 0.3s, color 0.3s, border-color 0.3s;
}
.ring-pct-badge.over {
    background: rgba(255,71,87,0.2); color: #ff6b6b;
    border-color: rgba(255,71,87,0.35);
}

/* ── Quick actions ── */
.quick-actions {
    display: flex; gap: 8px; justify-content: center; padding: 2px 0;
}
.action-btn {
    flex: 1; max-width: 74px; height: 50px;
    border-radius: 14px; border: 1px solid rgba(255,255,255,0.12);
    background: rgba(255,255,255,0.07);
    display: flex; align-items: center; justify-content: center;
    cursor: pointer; transition: background 0.15s, transform 0.12s;
}
.action-btn:hover { background: rgba(255,255,255,0.12); }
.action-btn:active { transform: scale(0.91); }
.action-btn img { width: 22px; height: 22px; filter: brightness(0) invert(1); opacity: 0.85; }

/* ── Cards area ── */
.cards-area {
    padding: 14px 14px 90px;
    display: flex; flex-direction: column; gap: 12px;
    background: var(--bg_color);
}

/* ── Nutrients card ── */
.nutrients-card {
    background: var(--card_color); border-radius: 20px;
    padding: 16px; box-shadow: var(--card_shadow); overflow: hidden;
}
.nutrients-header {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 14px;
}
.nutrients-title { font-size: 15px; font-weight: 800; color: var(--text_color); }
.nutrients-toggle {
    background: none; border: none; cursor: pointer;
    color: var(--text_muted); font-size: 11px; padding: 4px 8px;
    border-radius: 8px; transition: background 0.2s; line-height: 1;
}
.nutrients-toggle:hover { background: var(--bg_color); }
.nutrients-body {
    max-height: 200px; overflow: hidden;
    transition: max-height 0.35s ease, opacity 0.3s;
    opacity: 1;
}
.nutrients-body.collapsed { max-height: 0; opacity: 0; }

.nutrients-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 6px; text-align: center; }
.nutrient-col { display: flex; flex-direction: column; align-items: center; gap: 3px; }
.nutrient-name {
    font-size: 11px; font-weight: 700; color: var(--text_muted);
    text-transform: uppercase; letter-spacing: 0.3px;
}
.nutrient-val { font-size: 15px; font-weight: 800; color: var(--text_color); line-height: 1.1; }
.nutrient-ring-wrap {
    position: relative; width: 76px; height: 76px;
    display: flex; align-items: center; justify-content: center;
}
.nutrient-ring {
    width: 76px; height: 76px; transform: rotate(-90deg);
    position: absolute; inset: 0;
}
.n-ring-bg { fill: none; stroke: #eef1f5; stroke-width: 7; }
.n-ring-fill {
    fill: none; stroke-width: 7; stroke-linecap: round;
    stroke-dasharray: 175.9; stroke-dashoffset: 175.9;
    transition: stroke-dashoffset .9s cubic-bezier(.4,0,.2,1), stroke .35s;
}
.n-ring-fill.protein { stroke: var(--protein_color); }
.n-ring-fill.carbs   { stroke: var(--carbs_color); }
.n-ring-fill.fat     { stroke: var(--fat_color); }
.nutrient-pct {
    position: relative; z-index: 1;
    font-size: 13px; font-weight: 800; color: var(--text_color);
}
.nutrient-goal { font-size: 11px; color: var(--text_muted); font-weight: 500; }

/* ── Meals section ── */
.meals-section { display: flex; flex-direction: column; gap: 0; }
.meal-card {
    background: var(--card_color); border-radius: 16px;
    box-shadow: var(--card_shadow); overflow: hidden; margin-bottom: 10px;
}
.meal-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 14px 16px 10px;
}
.meal-header-left { display: flex; flex-direction: column; gap: 2px; }
.meal-title { font-size: 14px; font-weight: 700; color: var(--text_color); }
.meal-kcal { font-size: 12px; color: var(--text_muted); }
.meal-add-btn {
    background: none; border: 1.5px solid var(--accent_color);
    color: var(--accent_color); border-radius: 8px;
    font-size: 12px; font-weight: 700; padding: 5px 12px; cursor: pointer;
    transition: background 0.15s, color 0.15s;
}
.meal-add-btn:hover { background: var(--accent_color); color: #fff; }
.meal-items { padding: 0 12px 10px; }
.log-empty { text-align: center; color: var(--text_muted); font-size: 13px; padding: 12px 0; }
.log-item {
    display: flex; align-items: center; gap: 10px;
    padding: 10px 4px; border-top: 1px solid var(--bg_color);
}
.log-item:first-child { border-top: none; }
.log-item-info { flex: 1; min-width: 0; }
.log-item-name { font-size: 13px; font-weight: 600; color: var(--text_color); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.log-item-qty { font-size: 11px; color: var(--text_muted); margin-top: 1px; }
.log-item-kcal { font-size: 13px; font-weight: 700; color: var(--accent_color); flex-shrink: 0; }
.log-item-del { background: none; border: none; color: #e55; font-size: 18px; cursor: pointer; padding: 4px; flex-shrink: 0; }
""".strip())

# ─────────────────────────────────────────────────────────────
# 4. dashboard/design.css  (tabs, food, modals, stats, profile)
# ─────────────────────────────────────────────────────────────
(STYLES / "dashboard").mkdir(parents=True, exist_ok=True)
w(STYLES / "dashboard" / "design.css", """
/* ── Body / tabs ── */
body.dashboard { overflow: hidden; height: 100dvh; }
.tab-panel {
    display: none; flex-direction: column;
    height: calc(100dvh - 52px - 64px);
    overflow-y: auto; padding-top: 52px;
    -webkit-overflow-scrolling: touch;
}
.tab-panel.active { display: flex; }

/* ── Loader ── */
.loader { display: flex; align-items: center; justify-content: center; height: 80px; }
.spinner { width: 26px; height: 26px; border: 3px solid var(--border_color); border-top-color: var(--accent_color); border-radius: 50%; animation: spin .7s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Buttons ── */
.btn-main {
    width: 100%; padding: 15px; border: none; border-radius: 14px;
    background: var(--accent_gradient); color: #fff;
    font-size: 15px; font-weight: 700; cursor: pointer;
    transition: opacity .2s, transform .12s;
}
.btn-main:hover { opacity: .92; }
.btn-main:active { transform: scale(.97); }
.btn-main:disabled { opacity: .5; cursor: not-allowed; }
.btn-main-outline {
    width: 100%; padding: 13px; border: 1.5px solid var(--accent_color); border-radius: 14px;
    background: none; color: var(--accent_color);
    font-size: 14px; font-weight: 700; cursor: pointer; margin-top: 8px;
}

/* ── Food tab ── */
.food-section { padding: 16px 16px 0; }
.food-search-wrap { position: relative; margin-bottom: 14px; }
.food-search {
    width: 100%; padding: 11px 16px 11px 40px;
    border: 1.5px solid var(--border_color); border-radius: 12px;
    background: var(--card_color); color: var(--text_color);
    font-size: 14px; outline: none;
}
.food-search:focus { border-color: var(--accent_color); }
.food-search-icon {
    position: absolute; left: 13px; top: 50%; transform: translateY(-50%);
    color: var(--text_muted); font-size: 15px; pointer-events: none;
}
.food-list { display: flex; flex-direction: column; gap: 8px; padding: 0 16px 16px; }
.food-card {
    display: flex; align-items: center; gap: 12px;
    background: var(--card_color); border-radius: 14px;
    padding: 12px 14px; cursor: pointer;
    box-shadow: var(--card_shadow); transition: transform .12s;
}
.food-card:active { transform: scale(.98); }
.food-card-emoji { font-size: 24px; flex-shrink: 0; }
.food-card-info { flex: 1; min-width: 0; }
.food-card-name { font-size: 13px; font-weight: 600; color: var(--text_color); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.food-card-macros { font-size: 11px; color: var(--text_muted); margin-top: 2px; }
.food-card-kcal { font-size: 14px; font-weight: 700; color: var(--accent_color); flex-shrink: 0; }
.food-card-custom { font-size: 10px; background: var(--accent_color); color: #fff; padding: 2px 6px; border-radius: 6px; }

/* ── Meal filter chips ── */
.meal-chip {
    padding: 6px 14px; border-radius: 99px; border: 1.5px solid var(--border_color);
    font-size: 12px; font-weight: 600; cursor: pointer; background: var(--bg_color);
    color: var(--text_muted); transition: all .2s; white-space: nowrap;
}
.meal-chip.active { background: var(--accent_color); border-color: var(--accent_color); color: #fff; }

/* ── Modal ── */
.modal-overlay {
    position: fixed; inset: 0; background: rgba(0,0,0,.5);
    z-index: 300; display: none; align-items: flex-end;
    backdrop-filter: blur(3px);
}
.modal-overlay.open { display: flex; }
.modal-sheet {
    width: 100%; background: var(--card_color);
    border-radius: 24px 24px 0 0; padding: 14px 18px 30px;
    max-height: 92dvh; overflow-y: auto;
    animation: slideUp .28s ease;
}
@keyframes slideUp { from { transform: translateY(100%); } to { transform: translateY(0); } }
.modal-handle { width: 36px; height: 4px; background: var(--border_color); border-radius: 99px; margin: 0 auto 14px; }
.modal-title { font-size: 17px; font-weight: 800; color: var(--text_color); margin-bottom: 14px; }

.qty-row { display: flex; align-items: center; gap: 10px; margin: 14px 0; }
.qty-btn { width: 38px; height: 38px; border-radius: 50%; border: 1.5px solid var(--border_color); background: var(--bg_color); color: var(--text_color); font-size: 20px; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: background .15s; }
.qty-btn:hover { background: var(--border_color); }
.qty-input { flex: 1; text-align: center; font-size: 19px; font-weight: 700; border: 1.5px solid var(--border_color); border-radius: 12px; padding: 9px; color: var(--text_color); background: var(--bg_color); outline: none; }
.qty-input:focus { border-color: var(--accent_color); }

.meal-selector { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 14px; }
.modal-food-preview { background: var(--bg_color); border-radius: 14px; padding: 12px; margin-bottom: 14px; }
.modal-food-name { font-size: 15px; font-weight: 700; color: var(--text_color); margin-bottom: 8px; }
.macro-chips { display: flex; gap: 7px; flex-wrap: wrap; }
.macro-chip { font-size: 12px; padding: 4px 9px; border-radius: 8px; font-weight: 600; }
.mc-cal { background: #fff3e0; color: #e65100; }
.mc-prot { background: #e8f0ff; color: #1565c0; }
.mc-carb { background: #fff8e1; color: #f57f17; }
.mc-fat  { background: #fce4ec; color: #c62828; }

/* ── Form fields ── */
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px; }
.form-field { display: flex; flex-direction: column; gap: 4px; }
.form-field label { font-size: 10px; font-weight: 700; color: var(--text_muted); text-transform: uppercase; letter-spacing: .4px; }
.form-field input {
    padding: 10px 12px; border: 1.5px solid var(--border_color); border-radius: 10px;
    background: var(--bg_color); color: var(--text_color); font-size: 14px; outline: none;
}
.form-field input:focus { border-color: var(--accent_color); }
.form-field.full { grid-column: 1 / -1; }

/* ── Profile ── */
.profile-section { padding: 16px; }
.profile-card {
    background: var(--card_color); border-radius: 18px;
    padding: 20px; margin-bottom: 14px; box-shadow: var(--card_shadow);
}
.profile-avatar {
    width: 70px; height: 70px; border-radius: 50%;
    background: var(--accent_gradient); display: flex; align-items: center;
    justify-content: center; font-size: 30px; margin: 0 auto 10px;
}
.profile-name { font-size: 20px; font-weight: 800; text-align: center; color: var(--text_color); }
.profile-email { font-size: 12px; color: var(--text_muted); text-align: center; margin-top: 3px; }
.profile-stats { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; margin-top: 14px; }
.profile-stat { text-align: center; }
.profile-stat-val { font-size: 18px; font-weight: 800; color: var(--text_color); }
.profile-stat-lbl { font-size: 10px; color: var(--text_muted); margin-top: 2px; }

.profile-settings { display: flex; flex-direction: column; gap: 10px; }
.settings-item {
    display: flex; align-items: center; justify-content: space-between;
    background: var(--card_color); border-radius: 14px;
    padding: 14px 16px; box-shadow: var(--card_shadow);
}
.settings-item-label { font-size: 14px; font-weight: 600; color: var(--text_color); }
.settings-item-val { font-size: 13px; color: var(--text_muted); margin-top: 2px; }
.settings-item-edit { font-size: 13px; color: var(--accent_color); font-weight: 700; cursor: pointer; }
.btn-logout {
    width: 100%; padding: 14px; margin-top: 14px; border: none; border-radius: 14px;
    background: #fee2e2; color: #dc2626; font-size: 14px; font-weight: 700; cursor: pointer;
    transition: background .15s;
}
.btn-logout:hover { background: #fecaca; }

/* ── Stats ── */
.stats-section { padding: 16px; }
.week-chart { background: var(--card_color); border-radius: 18px; padding: 18px; box-shadow: var(--card_shadow); margin-bottom: 12px; }
.week-chart-title { font-size: 15px; font-weight: 700; color: var(--text_color); margin-bottom: 14px; }
.week-bars { display: flex; gap: 5px; align-items: flex-end; height: 90px; }
.week-bar-wrap { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 4px; }
.week-bar { width: 100%; border-radius: 5px 5px 0 0; background: var(--accent_gradient); min-height: 4px; transition: height .4s ease; }
.week-bar.today { background: linear-gradient(135deg, #f9ca24, #f0932b); }
.week-bar-label { font-size: 10px; color: var(--text_muted); font-weight: 600; }
.week-bar-val { font-size: 9px; color: var(--text_muted); }

/* ── Log items ── */
.log-section { padding: 0 16px 8px; }
.log-date-title { font-size: 12px; font-weight: 700; color: var(--text_muted); text-transform: uppercase; letter-spacing: .5px; padding: 10px 0 6px; }
.log-empty { text-align: center; color: var(--text_muted); font-size: 13px; padding: 20px 0; }

/* ── Mobile ── */
@media (max-width: 430px) {
    .tab-panel { height: calc(100dvh - 52px - 60px); }
    .cal-ring-wrap { width: 130px; height: 130px; }
    .cal-ring-svg  { width: 130px; height: 130px; }
    .ring-kcal { font-size: 26px; }
    .nutrient-ring-wrap { width: 68px; height: 68px; }
    .nutrient-ring { width: 68px; height: 68px; }
    .n-ring-fill { stroke-dasharray: 157.1; stroke-dashoffset: 157.1; }
    .nutrient-pct { font-size: 12px; }
    .modal-sheet { padding: 12px 14px 26px; }
}
""".strip())

# ─────────────────────────────────────────────────────────────
# 5. main.css  (add dashboard import if missing)
# ─────────────────────────────────────────────────────────────
main_css_path = BASE / "assets" / "styles" / "main.css"
main_css = main_css_path.read_text(encoding="utf-8")
if "dashboard" not in main_css:
    main_css += "\n@import url('components/dashboard/design.css');\n"
    main_css_path.write_text(main_css, encoding="utf-8")
    print("  updated assets/styles/main.css")
else:
    print("  main.css already has dashboard import")

# ─────────────────────────────────────────────────────────────
# 6. home.html  (full rewrite, English, new design)
# ─────────────────────────────────────────────────────────────
HOME_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
    <title>Calogram</title>
    <link rel="stylesheet" href="assets/styles/main.css">
    <link rel="icon" href="assets/images/favicon.png" type="image/png">
</head>
<body class="dashboard">

<!-- ══════ HEADER ══════ -->
<header>
    <a class="days" href="#" id="days_icon">
        <img class="days_img" src="assets/images/components/interface/medal1.svg" alt="streak">
        <span class="calc_days" id="active_days">0</span>
    </a>
    <h3 class="app_name">CALOGRAM</h3>
    <a class="date" href="#" id="today_date">
        <img class="calendar" src="assets/images/components/interface/calendar.svg" alt="date">
        <span class="date_text" id="today_date_text">00.00</span>
    </a>
</header>

<!-- ══════ TAB: TODAY ══════ -->
<div class="tab-panel active" id="tab-home">

    <!-- Hero dark block -->
    <section class="hero">

        <!-- Greeting -->
        <div class="hero-greeting">
            <div class="hero-greeting-text">
                <div class="hero-greeting-sub">Welcome,</div>
                <div class="hero-greeting-name" id="hero_name">—</div>
            </div>
            <div class="hero-avatar" id="hero_avatar">&#128578;</div>
        </div>

        <!-- Week strip -->
        <div class="week-strip">
            <div class="day" id="day_1"><span class="day_name">Mon</span><div class="day_circle"><span class="day_date">0</span></div></div>
            <div class="day" id="day_2"><span class="day_name">Tue</span><div class="day_circle"><span class="day_date">0</span></div></div>
            <div class="day" id="day_3"><span class="day_name">Wed</span><div class="day_circle"><span class="day_date">0</span></div></div>
            <div class="day" id="day_4"><span class="day_name">Thu</span><div class="day_circle"><span class="day_date">0</span></div></div>
            <div class="day" id="day_5"><span class="day_name">Fri</span><div class="day_circle"><span class="day_date">0</span></div></div>
            <div class="day" id="day_6"><span class="day_name">Sat</span><div class="day_circle"><span class="day_date">0</span></div></div>
            <div class="day" id="day_7"><span class="day_name">Sun</span><div class="day_circle"><span class="day_date">0</span></div></div>
        </div>

        <!-- Calorie ring -->
        <div class="calorie-section">
            <div class="cal-side">
                <img src="assets/images/components/interface/food1.svg" class="cal-icon" alt="food">
                <span class="cal-side-val" id="consumed_kcal">0</span>
                <span class="cal-side-lbl">Consumed</span>
            </div>

            <div class="cal-ring-wrap">
                <svg class="cal-ring-svg" viewBox="0 0 120 120">
                    <defs>
                        <linearGradient id="ringGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%"   stop-color="#3ecf8e"/>
                            <stop offset="100%" stop-color="#00e5b0"/>
                        </linearGradient>
                    </defs>
                    <circle class="ring-bg"   cx="60" cy="60" r="50"/>
                    <circle class="ring-fill" id="ring_fill" cx="60" cy="60" r="50"
                        stroke-dasharray="314" stroke-dashoffset="314"/>
                </svg>
                <div class="ring-center">
                    <span class="ring-kcal" id="ring_kcal">0</span>
                    <span class="ring-goal-txt">/ <span id="ring_goal_num">2000</span> kcal</span>
                    <span class="ring-pct-badge" id="ring_pct_badge">0%</span>
                </div>
            </div>

            <div class="cal-side">
                <img src="assets/images/components/interface/run.svg" class="cal-icon" alt="activity">
                <span class="cal-side-val" id="activity_kcal">0</span>
                <span class="cal-side-lbl">Activity</span>
            </div>
        </div>

        <!-- Quick actions -->
        <div class="quick-actions">
            <button class="action-btn" onclick="openAddFoodModal('breakfast')">
                <img src="assets/images/components/interface/plass.svg" alt="add">
            </button>
            <button class="action-btn">
                <img src="assets/images/components/interface/qr-code.svg" alt="barcode">
            </button>
            <button class="action-btn">
                <img src="assets/images/components/interface/camera.svg" alt="photo">
            </button>
            <button class="action-btn">
                <img src="assets/images/components/interface/fit.svg" alt="activity">
            </button>
        </div>
    </section>

    <!-- Cards area (light background) -->
    <div class="cards-area">

        <!-- Nutrients -->
        <section class="nutrients-card">
            <div class="nutrients-header">
                <span class="nutrients-title">Nutrients</span>
                <button class="nutrients-toggle" id="nut-toggle" onclick="toggleNutrients()">&#9650;</button>
            </div>
            <div class="nutrients-body" id="nutrients-body">
                <div class="nutrients-grid">
                    <!-- Protein -->
                    <div class="nutrient-col">
                        <span class="nutrient-name">Protein</span>
                        <span class="nutrient-val"><span id="nv_protein">0</span> g</span>
                        <div class="nutrient-ring-wrap">
                            <svg class="nutrient-ring" viewBox="0 0 80 80">
                                <circle class="n-ring-bg"  cx="40" cy="40" r="28"/>
                                <circle class="n-ring-fill protein" id="n_protein" cx="40" cy="40" r="28"
                                    stroke-dasharray="175.9" stroke-dashoffset="175.9"/>
                            </svg>
                            <span class="nutrient-pct" id="np_protein">0%</span>
                        </div>
                        <span class="nutrient-goal">of <span id="ng_protein">0</span> g</span>
                    </div>
                    <!-- Carbs -->
                    <div class="nutrient-col">
                        <span class="nutrient-name">Carbs</span>
                        <span class="nutrient-val"><span id="nv_carbs">0</span> g</span>
                        <div class="nutrient-ring-wrap">
                            <svg class="nutrient-ring" viewBox="0 0 80 80">
                                <circle class="n-ring-bg"  cx="40" cy="40" r="28"/>
                                <circle class="n-ring-fill carbs" id="n_carbs" cx="40" cy="40" r="28"
                                    stroke-dasharray="175.9" stroke-dashoffset="175.9"/>
                            </svg>
                            <span class="nutrient-pct" id="np_carbs">0%</span>
                        </div>
                        <span class="nutrient-goal">of <span id="ng_carbs">0</span> g</span>
                    </div>
                    <!-- Fat -->
                    <div class="nutrient-col">
                        <span class="nutrient-name">Fat</span>
                        <span class="nutrient-val"><span id="nv_fat">0</span> g</span>
                        <div class="nutrient-ring-wrap">
                            <svg class="nutrient-ring" viewBox="0 0 80 80">
                                <circle class="n-ring-bg"  cx="40" cy="40" r="28"/>
                                <circle class="n-ring-fill fat" id="n_fat" cx="40" cy="40" r="28"
                                    stroke-dasharray="175.9" stroke-dashoffset="175.9"/>
                            </svg>
                            <span class="nutrient-pct" id="np_fat">0%</span>
                        </div>
                        <span class="nutrient-goal">of <span id="ng_fat">0</span> g</span>
                    </div>
                </div>
            </div>
        </section>

        <!-- Meal log -->
        <div class="meals-section" id="today-log-meals"></div>

    </div><!-- /cards-area -->
</div><!-- /tab-home -->

<!-- ══════ TAB: STATS ══════ -->
<div class="tab-panel" id="tab-stats">
    <div class="stats-section" style="padding-top:68px;">
        <div class="week-chart">
            <div class="week-chart-title">Calories this week</div>
            <div class="week-bars" id="week-bars"></div>
        </div>
        <div style="background:var(--card_color);border-radius:18px;padding:18px;box-shadow:var(--card_shadow);">
            <div style="font-size:15px;font-weight:700;color:var(--text_color);margin-bottom:12px;">Today</div>
            <div id="stats-macro-list" style="display:flex;flex-direction:column;gap:10px;"></div>
        </div>
    </div>
</div>

<!-- ══════ TAB: FOOD ══════ -->
<div class="tab-panel" id="tab-food">
    <div class="food-section" style="padding-top:68px;">
        <div style="display:flex;gap:8px;margin-bottom:10px;">
            <div class="food-search-wrap" style="flex:1;margin-bottom:0;">
                <span class="food-search-icon">&#128269;</span>
                <input class="food-search" id="food-search-input" type="search"
                    placeholder="Search foods..." oninput="handleFoodSearch(this.value)">
            </div>
            <button onclick="openCustomFoodModal()"
                style="padding:0 14px;border-radius:12px;border:1.5px solid var(--accent_color);background:none;color:var(--accent_color);font-size:22px;cursor:pointer;font-weight:700;">+</button>
        </div>
        <div style="display:flex;gap:6px;margin-bottom:14px;overflow-x:auto;padding-bottom:3px;">
            <button class="meal-chip active" id="filter-all"    onclick="setFoodFilter('all')">All</button>
            <button class="meal-chip"        id="filter-shared" onclick="setFoodFilter('shared')">General</button>
            <button class="meal-chip"        id="filter-custom" onclick="setFoodFilter('custom')">My foods</button>
        </div>
    </div>
    <div class="food-list" id="food-list-items">
        <div class="loader"><div class="spinner"></div></div>
    </div>
</div>

<!-- ══════ TAB: PROFILE ══════ -->
<div class="tab-panel" id="tab-profile">
    <div class="profile-section" style="padding-top:68px;padding-bottom:80px;">
        <div class="profile-card">
            <div class="profile-avatar" id="profile-avatar">&#128100;</div>
            <div class="profile-name"  id="profile-name">—</div>
            <div class="profile-email" id="profile-email">—</div>
            <div class="profile-stats">
                <div class="profile-stat">
                    <div class="profile-stat-val" id="ps-age">—</div>
                    <div class="profile-stat-lbl">Age</div>
                </div>
                <div class="profile-stat">
                    <div class="profile-stat-val" id="ps-weight">—</div>
                    <div class="profile-stat-lbl">Weight</div>
                </div>
                <div class="profile-stat">
                    <div class="profile-stat-val" id="ps-goal">—</div>
                    <div class="profile-stat-lbl">Goal</div>
                </div>
            </div>
        </div>
        <div class="profile-settings">
            <div class="settings-item">
                <div>
                    <div class="settings-item-label">Calorie goal</div>
                    <div class="settings-item-val" id="sp-calgoal">— kcal/day</div>
                </div>
                <span class="settings-item-edit" onclick="openGoalEditor()">Edit</span>
            </div>
            <div class="settings-item">
                <div>
                    <div class="settings-item-label">Protein / Carbs / Fat</div>
                    <div class="settings-item-val" id="sp-macros">—</div>
                </div>
            </div>
            <div class="settings-item">
                <div>
                    <div class="settings-item-label">Gender</div>
                    <div class="settings-item-val" id="sp-gender">—</div>
                </div>
            </div>
        </div>
        <button class="btn-logout" onclick="logout()">Sign out</button>
    </div>
</div>

<!-- ══════ FOOTER NAV ══════ -->
<footer>
    <nav>
        <a class="nav-link active" href="#home" onclick="switchTab('home',this)">
            <img class="nav_img" src="assets/images/components/interface/home.svg" alt="home">
            <span>Today</span>
        </a>
        <a class="nav-link" href="#stats" onclick="switchTab('stats',this)">
            <img class="nav_img" src="assets/images/components/interface/stats.svg" alt="stats">
            <span>Stats</span>
        </a>
        <a class="nav-link nav-link--add" href="#new" onclick="openAddFoodModal('breakfast');return false;">
            <div class="add-circle">
                <img class="nav_img" src="assets/images/components/interface/plass.svg" alt="add">
            </div>
        </a>
        <a class="nav-link" href="#food" onclick="switchTab('food',this)">
            <img class="nav_img" src="assets/images/components/interface/food.svg" alt="food">
            <span>Food</span>
        </a>
        <a class="nav-link" href="#profile" onclick="switchTab('profile',this)">
            <img class="nav_img" src="assets/images/components/interface/user.svg" alt="profile">
            <span>Profile</span>
        </a>
    </nav>
</footer>

<!-- ══════ MODAL: ADD FOOD ══════ -->
<div class="modal-overlay" id="modal-add-food" onclick="closeModalIfOverlay(event,'modal-add-food')">
    <div class="modal-sheet">
        <div class="modal-handle"></div>
        <div class="modal-title">Add to diary</div>
        <div class="food-search-wrap">
            <span class="food-search-icon">&#128269;</span>
            <input class="food-search" id="modal-food-search" type="search"
                placeholder="Search food..." oninput="handleModalSearch(this.value)">
        </div>
        <div id="modal-food-results" style="max-height:190px;overflow-y:auto;margin-bottom:10px;"></div>
        <div id="modal-selected-food" style="display:none;">
            <div class="modal-food-preview">
                <div class="modal-food-name" id="modal-food-name">—</div>
                <div class="macro-chips" id="modal-food-macros"></div>
            </div>
            <div style="font-size:12px;font-weight:700;color:var(--text_muted);margin-bottom:6px;">Quantity</div>
            <div class="qty-row">
                <button class="qty-btn" onclick="changeQty(-10)">&#8722;</button>
                <input class="qty-input" id="modal-qty" type="number" value="100" min="1" max="9999" oninput="updateMacroPreview()">
                <span style="font-size:13px;color:var(--text_muted);font-weight:600;" id="modal-qty-unit">g</span>
                <button class="qty-btn" onclick="changeQty(10)">+</button>
            </div>
            <div style="font-size:12px;font-weight:700;color:var(--text_muted);margin-bottom:6px;">Meal</div>
            <div class="meal-selector">
                <button class="meal-chip active" data-meal="breakfast" onclick="selectMeal(this)">Breakfast</button>
                <button class="meal-chip" data-meal="lunch"     onclick="selectMeal(this)">Lunch</button>
                <button class="meal-chip" data-meal="dinner"    onclick="selectMeal(this)">Dinner</button>
                <button class="meal-chip" data-meal="snack"     onclick="selectMeal(this)">Snack</button>
            </div>
            <button class="btn-main" id="modal-add-btn" onclick="confirmAddFood()">Add</button>
        </div>
    </div>
</div>

<!-- ══════ MODAL: CUSTOM FOOD ══════ -->
<div class="modal-overlay" id="modal-custom-food" onclick="closeModalIfOverlay(event,'modal-custom-food')">
    <div class="modal-sheet">
        <div class="modal-handle"></div>
        <div class="modal-title">New food item</div>
        <div class="form-field full" style="margin-bottom:10px;">
            <label>Food name</label>
            <input id="cf-name" type="text" placeholder="E.g. Protein bar">
        </div>
        <div class="form-row">
            <div class="form-field"><label>Calories (per 100g)</label><input id="cf-cal" type="number" placeholder="0" min="0"></div>
            <div class="form-field"><label>Unit</label><input id="cf-unit" type="text" placeholder="g" value="g"></div>
        </div>
        <div class="form-row">
            <div class="form-field"><label>Protein (g)</label><input id="cf-protein" type="number" placeholder="0" min="0"></div>
            <div class="form-field"><label>Carbs (g)</label><input id="cf-carbs" type="number" placeholder="0" min="0"></div>
        </div>
        <div class="form-row">
            <div class="form-field"><label>Fat (g)</label><input id="cf-fat" type="number" placeholder="0" min="0"></div>
            <div class="form-field"><label>Serving weight (g)</label><input id="cf-unit-weight" type="number" placeholder="100" min="1" value="100"></div>
        </div>
        <div id="cf-error" style="color:#e55;font-size:12px;min-height:16px;margin-bottom:6px;"></div>
        <button class="btn-main" onclick="submitCustomFood()">Save food</button>
    </div>
</div>

<!-- ══════ MODAL: EDIT GOAL ══════ -->
<div class="modal-overlay" id="modal-goal" onclick="closeModalIfOverlay(event,'modal-goal')">
    <div class="modal-sheet">
        <div class="modal-handle"></div>
        <div class="modal-title">Daily calorie goal</div>
        <div class="form-field" style="margin-bottom:14px;">
            <label>Calories (kcal/day)</label>
            <input id="goal-cal-input" type="number" min="800" max="10000" placeholder="2000">
        </div>
        <button class="btn-main" onclick="saveGoal()">Save</button>
    </div>
</div>

<script>
const API = `http://${window.location.hostname}:28016/api`;
let token = localStorage.getItem('cg_token');
let userData = null;
let allFoods = [];
let todayLog = [];
let selectedFood = null;
let foodFilter = 'all';
const TODAY = new Date().toISOString().slice(0, 10);
const CIRC_MAIN = 314;   // 2*pi*50
const CIRC_NUT  = 175.9; // 2*pi*28

if (!token) { window.location.href = 'index.html'; }

// ── API ──────────────────────────────────────────────────────
async function api(method, path, body) {
    const opts = { method, headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token } };
    if (body) opts.body = JSON.stringify(body);
    const res = await fetch(API + path, opts);
    if (res.status === 401) { localStorage.removeItem('cg_token'); window.location.href = 'index.html'; }
    return res.json();
}

// ── Tabs ─────────────────────────────────────────────────────
function switchTab(name, el) {
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    document.getElementById('tab-' + name).classList.add('active');
    document.querySelectorAll('.nav-link').forEach(a => a.classList.remove('active'));
    if (el) el.classList.add('active');
    if (name === 'stats')   loadWeekStats();
    if (name === 'food')    loadFoods();
    if (name === 'profile') renderProfile();
}

// ── Date helpers ─────────────────────────────────────────────
function getWeekDays() {
    const today = new Date();
    const dow = (today.getDay() + 6) % 7;
    return Array.from({ length: 7 }, (_, i) => {
        const d = new Date(today); d.setDate(today.getDate() - dow + i); return d;
    });
}

// ── Week header ──────────────────────────────────────────────
function renderWeekHeader() {
    const days = getWeekDays();
    days.forEach((d, i) => {
        const el = document.getElementById('day_' + (i + 1));
        if (!el) return;
        el.querySelector('.day_date').textContent = d.getDate();
        const iso = d.toISOString().slice(0, 10);
        if (iso === TODAY) el.classList.add('today');
    });
    const now = new Date();
    document.getElementById('today_date_text').textContent =
        now.toLocaleDateString('en-GB', { day: '2-digit', month: '2-digit' });
}

// ── Load today ───────────────────────────────────────────────
async function loadToday() {
    const [stats, log] = await Promise.all([
        api('GET', '/food/stats?date=' + TODAY),
        api('GET', '/food/log?date='+  TODAY)
    ]);
    todayLog = log;
    const kcal = Math.round(stats.calories || 0);
    const goal = stats.calorie_goal || 2000;
    const pct  = Math.round(kcal / goal * 100);
    const fill = Math.min(100, pct);
    const isOver = kcal > goal;

    document.getElementById('ring_kcal').textContent      = kcal;
    document.getElementById('ring_goal_num').textContent  = goal;
    document.getElementById('consumed_kcal').textContent  = kcal;

    const rf = document.getElementById('ring_fill');
    rf.style.strokeDashoffset = CIRC_MAIN * (1 - fill / 100);
    rf.style.stroke = isOver ? '#ff6b6b' : 'url(#ringGrad)';

    const badge = document.getElementById('ring_pct_badge');
    badge.textContent = pct + '%';
    badge.className = 'ring-pct-badge' + (isOver ? ' over' : '');

    setNutrient('protein', stats.protein, stats.protein_goal || 120);
    setNutrient('carbs',   stats.carbs,   stats.carbs_goal   || 250);
    setNutrient('fat',     stats.fat,     stats.fat_goal     || 65);
    renderMealLog(log);
}

function setNutrient(id, val, goal) {
    const v   = Math.round(val || 0);
    const g   = goal || 1;
    const pct = Math.round(v / g * 100);
    const fill = Math.min(100, pct);
    const offset = CIRC_NUT * (1 - fill / 100);
    const isOver = pct > 100;

    document.getElementById('nv_' + id).textContent  = v;
    document.getElementById('ng_' + id).textContent  = goal;
    document.getElementById('np_' + id).textContent  = pct + '%';

    const ring = document.getElementById('n_' + id);
    if (ring) {
        ring.style.strokeDashoffset = offset;
        ring.style.stroke = isOver ? '#ff4757'
            : id === 'protein' ? 'var(--protein_color)'
            : id === 'carbs'   ? 'var(--carbs_color)'
            :                    'var(--fat_color)';
    }
    const pctEl = document.getElementById('np_' + id);
    if (pctEl) pctEl.style.color = isOver ? '#ff4757' : 'var(--text_color)';
}

// ── Nutrients toggle ─────────────────────────────────────────
function toggleNutrients() {
    const body = document.getElementById('nutrients-body');
    const btn  = document.getElementById('nut-toggle');
    const collapsed = body.classList.toggle('collapsed');
    btn.innerHTML = collapsed ? '&#9660;' : '&#9650;';
}

// ── Meal log ─────────────────────────────────────────────────
const MEALS = {
    breakfast: 'Breakfast',
    lunch:     'Lunch',
    dinner:    'Dinner',
    snack:     'Snack'
};

function renderMealLog(log) {
    const container = document.getElementById('today-log-meals');
    const byMeal = {};
    for (const m of Object.keys(MEALS)) byMeal[m] = [];
    log.forEach(item => { if (byMeal[item.meal_type]) byMeal[item.meal_type].push(item); });

    container.innerHTML = '';
    for (const [mealKey, items] of Object.entries(byMeal)) {
        const total = items.reduce((s, i) => s + i.total_calories, 0);
        const itemsHtml = items.length === 0
            ? `<div class="log-empty">Nothing added yet</div>`
            : items.map(i => `
                <div class="log-item">
                    <div class="log-item-info">
                        <div class="log-item-name">${i.name}</div>
                        <div class="log-item-qty">${i.quantity}${i.unit} &middot; P:${i.total_protein}g C:${i.total_carbs}g F:${i.total_fat}g</div>
                    </div>
                    <div class="log-item-kcal">${i.total_calories} kcal</div>
                    <button class="log-item-del" onclick="deleteLogItem(${i.id})">&#215;</button>
                </div>`).join('');

        container.insertAdjacentHTML('beforeend', `
        <div class="meal-card">
            <div class="meal-header">
                <div class="meal-header-left">
                    <span class="meal-title">${MEALS[mealKey]}</span>
                    <span class="meal-kcal">${Math.round(total)} kcal</span>
                </div>
                <button class="meal-add-btn" onclick="openAddFoodModal('${mealKey}')">+ Add</button>
            </div>
            <div class="meal-items">${itemsHtml}</div>
        </div>`);
    }
}

async function deleteLogItem(id) {
    await api('DELETE', '/food/log/' + id);
    await loadToday();
}

// ── Stats ────────────────────────────────────────────────────
async function loadWeekStats() {
    const data = await api('GET', '/food/stats/week');
    const maxCal = Math.max(...data.map(d => d.calories), 1);
    const names  = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];
    document.getElementById('week-bars').innerHTML = data.map((d, i) => {
        const h = Math.round((d.calories / maxCal) * 84);
        return `<div class="week-bar-wrap">
            <div class="week-bar-val">${Math.round(d.calories) || ''}</div>
            <div class="week-bar ${d.date === TODAY ? 'today' : ''}" style="height:${h}px"></div>
            <div class="week-bar-label">${names[i]}</div>
        </div>`;
    }).join('');

    const stats = await api('GET', '/food/stats?date=' + TODAY);
    document.getElementById('stats-macro-list').innerHTML = [
        { label:'Calories', val:Math.round(stats.calories), goal:stats.calorie_goal, unit:'kcal', color:'#e65100' },
        { label:'Protein',  val:Math.round(stats.protein),  goal:stats.protein_goal, unit:'g',    color:'#1565c0' },
        { label:'Carbs',    val:Math.round(stats.carbs),    goal:stats.carbs_goal,   unit:'g',    color:'#f57f17' },
        { label:'Fat',      val:Math.round(stats.fat),      goal:stats.fat_goal,     unit:'g',    color:'#c62828' },
    ].map(m => {
        const pct = Math.min(100, Math.round(m.val / (m.goal||1) * 100));
        return `<div>
            <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                <span style="font-size:13px;font-weight:600;color:var(--text_color)">${m.label}</span>
                <span style="font-size:12px;color:var(--text_muted)">${m.val} / ${m.goal} ${m.unit}</span>
            </div>
            <div style="height:7px;background:var(--bg_color);border-radius:99px;overflow:hidden;">
                <div style="height:100%;width:${pct}%;background:${m.color};border-radius:99px;transition:width .4s;"></div>
            </div>
        </div>`;
    }).join('');
}

// ── Foods ─────────────────────────────────────────────────────
function foodEmoji(name) {
    const n = (name||'').toLowerCase();
    if (n.includes('chicken') || n.includes('breast')) return '🍗';
    if (n.includes('egg'))     return '🥚';
    if (n.includes('rice') || n.includes('buckwheat')) return '🍚';
    if (n.includes('milk') || n.includes('kefir'))     return '🥛';
    if (n.includes('banana'))  return '🍌';
    if (n.includes('apple'))   return '🍎';
    if (n.includes('bread'))   return '🥖';
    if (n.includes('cheese'))  return '🧀';
    if (n.includes('salmon') || n.includes('tuna') || n.includes('fish')) return '🐟';
    if (n.includes('potato'))  return '🥔';
    if (n.includes('cucumber'))return '🥒';
    if (n.includes('tomato'))  return '🍅';
    if (n.includes('nut'))     return '🌰';
    if (n.includes('honey'))   return '🍯';
    if (n.includes('butter'))  return '🧈';
    if (n.includes('pasta'))   return '🍝';
    if (n.includes('avocado')) return '🥑';
    if (n.includes('orange'))  return '🍊';
    if (n.includes('yogurt'))  return '🫙';
    if (n.includes('strawberry')) return '🍓';
    if (n.includes('broccoli'))   return '🥦';
    if (n.includes('oat'))     return '🥣';
    return '🍽️';
}

async function loadFoods() {
    const list = await api('GET', '/food/list');
    allFoods = list;
    renderFoodList(list);
}

function setFoodFilter(f) {
    foodFilter = f;
    ['all','shared','custom'].forEach(id =>
        document.getElementById('filter-' + id).classList.toggle('active', id === f));
    filterAndRender(document.getElementById('food-search-input').value);
}
function handleFoodSearch(q) { filterAndRender(q); }
function filterAndRender(q) {
    let filtered = allFoods;
    if (foodFilter === 'shared') filtered = filtered.filter(f => !f.is_custom);
    if (foodFilter === 'custom') filtered = filtered.filter(f =>  f.is_custom);
    if (q) filtered = filtered.filter(f => f.name.toLowerCase().includes(q.toLowerCase()));
    renderFoodList(filtered);
}
function renderFoodList(foods) {
    const c = document.getElementById('food-list-items');
    if (!foods.length) { c.innerHTML = '<div class="log-empty">Nothing found</div>'; return; }
    c.innerHTML = foods.map(f => `
        <div class="food-card" onclick="openAddFoodModal('breakfast',${f.id})">
            <span class="food-card-emoji">${foodEmoji(f.name)}</span>
            <div class="food-card-info">
                <div class="food-card-name">${f.name}${f.is_custom?` <span class="food-card-custom">Mine</span>`:''}</div>
                <div class="food-card-macros">P:${f.protein}g &middot; C:${f.carbs}g &middot; F:${f.fat}g &middot; per ${f.unit_weight}${f.unit}</div>
            </div>
            <span class="food-card-kcal">${f.calories}<br><span style="font-size:10px;font-weight:400;color:var(--text_muted)">kcal</span></span>
        </div>`).join('');
}

// ── Add food modal ────────────────────────────────────────────
let currentMeal = 'breakfast';
async function openAddFoodModal(meal, foodId) {
    if (!allFoods.length) await loadFoods();
    currentMeal = meal || 'breakfast';
    document.querySelectorAll('.meal-chip[data-meal]').forEach(c =>
        c.classList.toggle('active', c.dataset.meal === currentMeal));
    document.getElementById('modal-food-results').innerHTML = '';
    document.getElementById('modal-food-search').value = '';
    document.getElementById('modal-selected-food').style.display = 'none';
    document.getElementById('modal-add-food').classList.add('open');
    selectedFood = null;
    if (foodId) { const food = allFoods.find(f => f.id === foodId); if (food) selectFoodForLog(food); }
    setTimeout(() => document.getElementById('modal-food-search').focus(), 120);
}
function handleModalSearch(q) {
    if (!q.trim()) { document.getElementById('modal-food-results').innerHTML = ''; return; }
    const results = allFoods.filter(f => f.name.toLowerCase().includes(q.toLowerCase())).slice(0, 10);
    document.getElementById('modal-food-results').innerHTML = results.map(f => `
        <div class="food-card" style="margin-bottom:6px;" onclick="selectFoodForLog(${JSON.stringify(f).replace(/"/g,'&quot;')})">
            <span class="food-card-emoji">${foodEmoji(f.name)}</span>
            <div class="food-card-info">
                <div class="food-card-name">${f.name}</div>
                <div class="food-card-macros">${f.calories} kcal &middot; ${f.unit_weight}${f.unit}</div>
            </div>
        </div>`).join('');
}
function selectFoodForLog(food) {
    selectedFood = food;
    document.getElementById('modal-food-results').innerHTML = '';
    document.getElementById('modal-food-search').value = food.name;
    document.getElementById('modal-selected-food').style.display = 'block';
    document.getElementById('modal-food-name').textContent = food.name;
    document.getElementById('modal-qty').value = food.unit_weight;
    document.getElementById('modal-qty-unit').textContent = food.unit;
    updateMacroPreview();
}
function updateMacroPreview() {
    if (!selectedFood) return;
    const qty = parseFloat(document.getElementById('modal-qty').value) || 100;
    const f = qty / (selectedFood.unit_weight || 100);
    document.getElementById('modal-food-macros').innerHTML = `
        <span class="macro-chip mc-cal">${Math.round(selectedFood.calories * f)} kcal</span>
        <span class="macro-chip mc-prot">P: ${Math.round(selectedFood.protein * f)}g</span>
        <span class="macro-chip mc-carb">C: ${Math.round(selectedFood.carbs * f)}g</span>
        <span class="macro-chip mc-fat">F: ${Math.round(selectedFood.fat * f)}g</span>`;
}
function changeQty(delta) {
    const inp = document.getElementById('modal-qty');
    inp.value = Math.max(1, (parseFloat(inp.value) || 0) + delta);
    updateMacroPreview();
}
function selectMeal(el) {
    document.querySelectorAll('.meal-chip[data-meal]').forEach(c => c.classList.remove('active'));
    el.classList.add('active');
    currentMeal = el.dataset.meal;
}
async function confirmAddFood() {
    if (!selectedFood) return;
    const qty = parseFloat(document.getElementById('modal-qty').value) || 100;
    const btn = document.getElementById('modal-add-btn');
    btn.disabled = true; btn.textContent = 'Adding...';
    await api('POST', '/food/log', { food_id: selectedFood.id, quantity: qty, meal_type: currentMeal, date: TODAY });
    btn.disabled = false; btn.textContent = 'Add';
    closeModal('modal-add-food');
    await loadToday();
}

// ── Custom food ───────────────────────────────────────────────
function openCustomFoodModal() {
    ['cf-name','cf-cal','cf-protein','cf-carbs','cf-fat'].forEach(id => document.getElementById(id).value = '');
    document.getElementById('cf-unit').value = 'g';
    document.getElementById('cf-unit-weight').value = '100';
    document.getElementById('cf-error').textContent = '';
    document.getElementById('modal-custom-food').classList.add('open');
}
async function submitCustomFood() {
    const name = document.getElementById('cf-name').value.trim();
    const cal  = parseFloat(document.getElementById('cf-cal').value);
    const err  = document.getElementById('cf-error');
    if (!name) { err.textContent = 'Enter a name'; return; }
    if (isNaN(cal)) { err.textContent = 'Enter calories'; return; }
    err.textContent = '';
    const result = await api('POST', '/food/add', {
        name, calories: cal,
        protein: parseFloat(document.getElementById('cf-protein').value) || 0,
        carbs:   parseFloat(document.getElementById('cf-carbs').value)   || 0,
        fat:     parseFloat(document.getElementById('cf-fat').value)     || 0,
        unit:    document.getElementById('cf-unit').value || 'g',
        unit_weight: parseFloat(document.getElementById('cf-unit-weight').value) || 100,
    });
    if (result.error) { err.textContent = result.error; return; }
    allFoods.push(result);
    closeModal('modal-custom-food');
    renderFoodList(allFoods);
}

// ── Goal editor ───────────────────────────────────────────────
function openGoalEditor() {
    document.getElementById('goal-cal-input').value = userData?.calorie_goal || 2000;
    document.getElementById('modal-goal').classList.add('open');
}
async function saveGoal() {
    const cal = parseInt(document.getElementById('goal-cal-input').value);
    if (!cal || cal < 800) return;
    const res = await api('PUT', '/user/profile', { calorie_goal: cal });
    userData = res;
    renderProfile();
    closeModal('modal-goal');
    await loadToday();
}

// ── Profile ───────────────────────────────────────────────────
const GOAL_LABELS   = { lose:'Lose weight', maintain:'Maintain', gain:'Gain weight' };
const GENDER_LABELS = { female:'Female', male:'Male', other:'Other' };

function renderProfile() {
    if (!userData) return;
    const name = userData.name || userData.email.split('@')[0];
    document.getElementById('profile-name').textContent  = name;
    document.getElementById('profile-email').textContent = userData.email;
    document.getElementById('ps-age').textContent    = userData.age    ? userData.age + ' y'    : '—';
    document.getElementById('ps-weight').textContent = userData.weight ? userData.weight + ' kg' : '—';
    document.getElementById('ps-goal').textContent   = GOAL_LABELS[userData.goal]   || '—';
    document.getElementById('sp-calgoal').textContent = (userData.calorie_goal || 2000) + ' kcal/day';
    document.getElementById('sp-macros').textContent  = `P:${userData.protein_goal||120}g C:${userData.carbs_goal||250}g F:${userData.fat_goal||65}g`;
    document.getElementById('sp-gender').textContent  = GENDER_LABELS[userData.gender] || '—';
    const avatarMap = { female:'👩', male:'👨', other:'🧑' };
    const emoji = avatarMap[userData.gender] || '👤';
    document.getElementById('profile-avatar').textContent = emoji;
    document.getElementById('hero_name').textContent  = name;
    document.getElementById('hero_avatar').textContent = emoji;
}

// ── Modals ────────────────────────────────────────────────────
function closeModal(id) { document.getElementById(id).classList.remove('open'); }
function closeModalIfOverlay(e, id) { if (e.target.id === id) closeModal(id); }
function logout() { localStorage.removeItem('cg_token'); window.location.href = 'index.html'; }

// ── Boot ──────────────────────────────────────────────────────
(async () => {
    userData = await api('GET', '/user/me');
    renderProfile();
    renderWeekHeader();
    await loadToday();
    await loadFoods();
})();
</script>
</body>
</html>"""

w(BASE / "home.html", HOME_HTML)
print("\nAll files written successfully!")
