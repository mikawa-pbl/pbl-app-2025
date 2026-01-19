document.addEventListener('DOMContentLoaded', function() {
    const grid = document.getElementById('viewGrid');
    if (!grid) return;

    const dataInput = document.getElementById('view_slots_data') || document.getElementById('user_slots_data');
    const userInput = document.getElementById('login_user_slots');

    let targetSlots = [];
    let mySlots = [];

    try { if (dataInput && dataInput.value) targetSlots = JSON.parse(dataInput.value.replace(/'/g, '"')); } catch(e) {}
    try { if (userInput && userInput.value) mySlots = JSON.parse(userInput.value.replace(/'/g, '"')); } catch(e) {}
    
    const days = ['mon', 'tue', 'wed', 'thu', 'fri'];
    const dayLabels = ['月', '火', '水', '木', '金'];
    
    let html = '<div class="grid-header-view"></div>';
    dayLabels.forEach(d => html += `<div class="grid-header-view">${d}</div>`);

    for (let h = 8; h < 21; h++) {
        for (let m of [0, 30]) {
            const timeStr = `${h}:${m === 0 ? '00' : '30'}`;
            const timeId = `${h.toString().padStart(2, '0')}${m === 0 ? '00' : '30'}`;
            const borderClass = m === 30 ? 'border-bottom-bold' : '';

            html += `<div class="time-label-view ${borderClass}">${timeStr}</div>`;

            days.forEach(day => {
                const val = `${day}_${timeId}`;
                let className = `slot-box ${borderClass}`;
                
                const isTarget = targetSlots.includes(val);
                const isMine = mySlots.includes(val);

                if (isTarget && isMine) { className += ' matched'; }
                else if (isTarget) { className += ' active'; }
                html += `<div class="${className}" title="${timeStr}"></div>`;
            });
        }
    }
    grid.innerHTML = html;
});