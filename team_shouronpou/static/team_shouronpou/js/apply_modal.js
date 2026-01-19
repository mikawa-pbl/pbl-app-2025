// 応募モーダルの開閉制御
function showModal() {
    const modal = document.getElementById('applyModal');
    if (modal) modal.style.display = 'block';
}

function hideModal() {
    const modal = document.getElementById('applyModal');
    if (modal) modal.style.display = 'none';
}

// モーダル外クリックで閉じる処理
window.addEventListener('click', function(event) {
    const modal = document.getElementById('applyModal');
    if (event.target === modal) {
        hideModal();
    }
});