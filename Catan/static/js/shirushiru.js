function openDialog() {
    document.getElementById('statusDialog').classList.add('show');
}

// 在室情報の最終更新時刻（フロント保持）
let lastUpdated = null;

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
            statusCell.innerHTML = '<span class="status-ok">🗣️</span>';
        } else {
            statusCell.innerHTML = '<span class="status-ng">🤫</span>';
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
    // 最終更新時刻を更新（ローカル表示用）
    lastUpdated = new Date().toLocaleString(undefined, {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
    });

    // 在室変更時の通知（サンプル）
    // alert('在室状況を更新しました');
    closeDialog();
}

// ユーザ詳細ダイアログを開く（行要素を渡す）
function openDetailDialogFromRow(tr) {
    if (!tr) return;
    const table = tr.closest('table');
    const gradeHeading = table && table.previousElementSibling && table.previousElementSibling.classList.contains('grade-title') ? table.previousElementSibling.textContent.trim() : '';
    const name = tr.querySelector('td:nth-child(1)') ? tr.querySelector('td:nth-child(1)').textContent.trim() : '';
    const location = tr.querySelector('td:nth-child(2)') ? tr.querySelector('td:nth-child(2)').textContent.trim() : '';
    const comment = tr.querySelector('td:nth-child(3)') ? tr.querySelector('td:nth-child(3)').textContent.trim() : '';
    const talk = tr.querySelector('td:nth-child(5)') ? tr.querySelector('td:nth-child(5)').textContent.trim() :'';

    const gradeElem = document.getElementById('detail-grade');
    const nameElem = document.getElementById('detail-name');
    const locElem = document.getElementById('detail-location');
    const comElem = document.getElementById('detail-comment');
    const updatedElem = document.getElementById('detail-updated');
     const talkElem = document.getElementById('detail-talk');


    if (gradeElem) gradeElem.textContent = gradeHeading || '-';
    if (nameElem) nameElem.textContent = name || '-';
    if (locElem) locElem.textContent = location || '-';
    if (comElem) comElem.textContent = comment || '-';
    if (updatedElem) updatedElem.textContent = lastUpdated || '-';
    if (talkElem) talkElem.textContent = talk || '-';


    document.getElementById('detailDialog').classList.add('show');
}

function closeDetailDialog() {
    document.getElementById('detailDialog').classList.remove('show');
}

// 初期化: テーブルの「詳細」クリックに対してダイアログを開く
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.detail').forEach(function (el) {
        el.style.cursor = 'pointer';
        el.addEventListener('click', function (e) {
            const tr = e.target.closest('tr');
            openDetailDialogFromRow(tr);
        });
    });
});

// ダイアログ外をクリックしたら閉じる（statusDialog と detailDialog の両方に対応）
window.onclick = function (event) {
    const statusDialog = document.getElementById('statusDialog');
    const detailDialog = document.getElementById('detailDialog');
    if (event.target === statusDialog) {
        closeDialog();
    }
    if (event.target === detailDialog) {
        closeDetailDialog();
    }
}