// scripts/copy_logic.js
// ガイド詳細ページでのコピーボタンの機能を提供します。

document.addEventListener('DOMContentLoaded', function() {
    const copyButton = document.querySelector('.copy-guide-btn');

    if (copyButton) {
        copyButton.addEventListener('click', function() {
            const texCode = this.getAttribute('data-tex-code');
            
            if (!texCode) return;

            navigator.clipboard.writeText(texCode)
                .then(() => {
                    this.textContent = 'コピー完了！';
                    setTimeout(() => {
                        this.textContent = 'コードをコピー';
                    }, 1000);
                })
                .catch(err => {
                    console.error('コピー失敗:', err);
                    this.textContent = 'コピー失敗';
                });
        });
    }
});
