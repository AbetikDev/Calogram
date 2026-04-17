const WEEKDAYS = ['Нд', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'];

let centerDate = null;
let isAnimating = false;

function toMidnight(d) {
    const c = new Date(d);
    c.setHours(0, 0, 0, 0);
    return c;
}

function fillCells() {
    const today = toMidnight(new Date());

    for (let i = 1; i <= 7; i++) {
        const offset = i - 4; // day_4 = center
        const date = new Date(centerDate);
        date.setDate(centerDate.getDate() + offset);

        const el = document.getElementById(`day_${i}`);
        if (!el) continue;

        const nameEl  = el.querySelector('.day_name');
        const dateEl  = el.querySelector('.day_date');
        const diffMs  = date - today;
        const diffDay = Math.round(diffMs / 86400000);

        dateEl.textContent = date.getDate();
        nameEl.textContent = WEEKDAYS[date.getDay()];

        el.className = 'day';
        if (diffDay === 0) el.classList.add('day--today');
        if (diffDay < 0)  el.classList.add('day--past');
        if (diffDay > 0)  el.classList.add('day--future');
        if (offset === 0) el.classList.add('day--selected');

        el.onclick = () => {
            if (offset === 0 || isAnimating) return;
            slide(date, offset < 0 ? 'prev' : 'next');
        };
    }
}

function slide(newCenter, direction) {
    isAnimating = true;
    const container = document.querySelector('.week-days');

    container.classList.add(`slide-out-${direction}`);
    setTimeout(() => {
        container.classList.remove(`slide-out-${direction}`);
        centerDate = toMidnight(newCenter);
        fillCells();
        container.classList.add(`slide-in-${direction}`);
        setTimeout(() => {
            container.classList.remove(`slide-in-${direction}`);
            isAnimating = false;
        }, 220);
    }, 180);
}

export function initWeekDays() {
    centerDate = toMidnight(new Date());
    fillCells();
}
