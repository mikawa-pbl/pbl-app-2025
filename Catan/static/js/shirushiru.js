function openDialog() {
    document.getElementById('statusDialog').classList.add('show');
}

function closeDialog() {
    document.getElementById('statusDialog').classList.remove('show');
}

function saveStatus() {
    const location = document.getElementById('locationSelect').value;
    const comment = document.getElementById('commentInput').value;

    // クライアント側でテーブルの該当行を更新する（簡易版）
    const locCell = document.getElementById('user-location-cell');
    const comCell = document.getElementById('user-comment-cell');
    if (locCell) locCell.textContent = location;
    if (comCell) comCell.textContent = comment;

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