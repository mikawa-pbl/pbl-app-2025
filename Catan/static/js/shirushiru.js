function openDialog() {
    document.getElementById('statusDialog').classList.add('show');
}

function closeDialog() {
    document.getElementById('statusDialog').classList.remove('show');
}

function saveStatus() {
    const selectElement = document.getElementById('locationSelect');
    const location = selectElement.value;
    const comment = document.getElementById('commentInput').value;
    const talkStatus = document.getElementById('talkStatusSelect').value;
    const selectedOption = selectElement.options[selectElement.selectedIndex];
    const key = selectedOption.getAttribute('key');

    // クライアント側でテーブルの該当行を更新する（簡易版）
    const locCell = document.getElementById('user-location-cell');
    const comCell = document.getElementById('user-comment-cell');
    const statusCell = document.getElementById('user-status-cell');
    const userRow = document.getElementById('user-row');
    
    if (locCell) locCell.textContent = location;
    if (comCell) comCell.textContent = comment;
    
    // ステータスを更新
    if (statusCell) {
        if (talkStatus === 'ok') {
            statusCell.innerHTML = '<span class="status-ok">✅ OK</span>';
        } else {
            statusCell.innerHTML = '<span class="status-ng">❌ NG</span>';
        }
    }

    // 研究室（labで始まるkey）の場合、行に色を付ける
    if (userRow) {
        if (key && key.startsWith('lab')) {
            userRow.classList.add('in-lab');
        } else {
            userRow.classList.remove('in-lab');
        }
    }

    // ここでサーバーにデータを送信して永続化する処理を追加できます

    alert('在室状況を更新しました');
    closeDialog();
}

// ダイアログ外をクリックしたら閉じる
window.onclick = function (event) {
    const dialog = document.getElementById('statusDialog');
    if (event.target === dialog) {
        closeDialog();
    }
}