// Default daily goals (can be overridden later via user settings)
const GOALS = {
    kcal:    2000,
    protein: 140,   // g
    carbs:   220,   // g
    fat:     65,    // g
    water:   2500,  // ml
};

// Demo data — replace with real data storage later
const DATA = {
    consumed: 1240,
    activity: 320,
    protein:  88,
    carbs:    105,
    fat:      42,
    water:    1400,
};

function setRingOffset(id, value, goal, circumference) {
    const el = document.getElementById(id);
    if (!el) return;
    const pct = Math.min(value / goal, 1);
    el.style.strokeDashoffset = circumference * (1 - pct);
}

function setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
}

function injectSvgGradient() {
    const svg = document.querySelector('.calorie-ring');
    if (!svg) return;
    const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
    defs.innerHTML = `
        <linearGradient id="ringGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%"   stop-color="#3ecf8e"/>
            <stop offset="100%" stop-color="#1aab6d"/>
        </linearGradient>`;
    svg.prepend(defs);
}

export function initCalorie() {
    injectSvgGradient();

    const net = DATA.consumed - DATA.activity;
    const pct = Math.round((net / GOALS.kcal) * 100);

    // Main ring  (circumference ≈ 2π×50 ≈ 314)
    setText('consumed_kcal', DATA.consumed + ' ккал');
    setText('activity_kcal', DATA.activity + ' ккал');
    setText('ring_percent', pct + '%');
    setText('ring_goal', '/ ' + GOALS.kcal + ' ккал');
    setRingOffset('ring_fill', net, GOALS.kcal, 314);

    // Nutrient rings (circumference ≈ 2π×24 ≈ 150.8)
    const C = 150.8;
    [
        ['n_protein', DATA.protein,  GOALS.protein,  'np_protein', 'nv_protein', 'ng_protein', GOALS.protein,  'г'],
        ['n_carbs',   DATA.carbs,    GOALS.carbs,    'np_carbs',   'nv_carbs',   'ng_carbs',   GOALS.carbs,    'г'],
        ['n_fat',     DATA.fat,      GOALS.fat,      'np_fat',     'nv_fat',     'ng_fat',     GOALS.fat,      'г'],
        ['n_water',   DATA.water,    GOALS.water,    'np_water',   'nv_water',   'ng_water',   GOALS.water,    'мл'],
    ].forEach(([ringId, val, goal, pctId, valId, goalId, goalVal, unit]) => {
        const p = Math.round((val / goal) * 100);
        setRingOffset(ringId, val, goal, C);
        setText(pctId, p + '%');
        setText(valId, val);
        setText(goalId, 'з ' + goalVal + ' ' + unit);
    });
}
