export function updateTodayDate() {
    const el = document.getElementById('today_date_text');
    if (!el) return;

    const now = new Date();
    const day = String(now.getDate()).padStart(2, '0');
    const month = String(now.getMonth() + 1).padStart(2, '0');
    el.textContent = `${day}.${month}`;
}

export function startTodayDateWatcher() {
    updateTodayDate();

    // Оновлення о midnight без помітного перезавантаження
    function scheduleNextUpdate() {
        const now = new Date();
        const msUntilMidnight =
            new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1) - now;
        setTimeout(() => {
            updateTodayDate();
            scheduleNextUpdate();
        }, msUntilMidnight);
    }

    scheduleNextUpdate();
}
