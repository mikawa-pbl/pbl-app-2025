document.addEventListener('DOMContentLoaded', function() {
    const grid = document.getElementById('scheduleGrid');
    const slotsInput = document.getElementById('id_available_slots');
    
    if (!grid || !slotsInput) return;

    const days = ['mon', 'tue', 'wed', 'thu', 'fri'];
    const dayLabels = ['月', '火', '水', '木', '金'];
    
    // グリッド生成
    let html = '<div class="grid-header"></div>';
    dayLabels.forEach(d => html += `<div class="grid-header">${d}</div>`);

    for (let h = 8; h < 21; h++) {
        for (let m of [0, 30]) {
            const timeStr = `${h}:${m === 0 ? '00' : '30'}`;
            const timeId = `${h.toString().padStart(2, '0')}${m === 0 ? '00' : '30'}`;
            const rowClass = m === 30 ? 'row-separator' : '';

            html += `<div class="time-label ${rowClass}">${timeStr}</div>`;
            
            days.forEach(day => {
                const val = `${day}_${timeId}`;
                html += `<div class="slot-btn ${rowClass}" data-value="${val}"></div>`;
            });
        }
    }
    grid.innerHTML = html;

    // データの復元
    let selectedSlots = [];
    try {
        if (slotsInput.value) {
            selectedSlots = JSON.parse(slotsInput.value.replace(/'/g, '"'));
        }
    } catch(e) { selectedSlots = []; }
    if (!Array.isArray(selectedSlots)) selectedSlots = [];

    const slotBtns = document.querySelectorAll('.slot-btn');
    slotBtns.forEach(btn => {
        if (selectedSlots.includes(btn.dataset.value)) {
            btn.classList.add('active');
        }
    });

    // ドラッグ選択
    let isMouseDown = false;
    let isAdding = true;

    function updateInput() {
        const actives = Array.from(document.querySelectorAll('.slot-btn.active')).map(el => el.dataset.value);
        slotsInput.value = JSON.stringify(actives);
    }
    function toggleSlot(btn) {
        if (isAdding) btn.classList.add('active'); else btn.classList.remove('active');
    }
    grid.addEventListener('mousedown', function(e) {
        if (e.target.classList.contains('slot-btn')) {
            e.preventDefault();
            isMouseDown = true;
            isAdding = !e.target.classList.contains('active');
            toggleSlot(e.target);
            updateInput();
        }
    });
    grid.addEventListener('mouseover', function(e) {
        if (isMouseDown && e.target.classList.contains('slot-btn')) toggleSlot(e.target);
    });
    document.addEventListener('mouseup', function() {
        if (isMouseDown) { isMouseDown = false; updateInput(); }
    });
});