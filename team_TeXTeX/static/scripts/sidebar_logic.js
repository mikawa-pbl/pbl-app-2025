// scripts/sidebar_logic.js
// サイドバーの開閉、コンテンツの操作、クリップボードコピー、リサイズなどのUI/UXロジックを管理

document.addEventListener('DOMContentLoaded', function () {

    // -----------------------------------------------------------------
    // 0. DOM要素定義
    // -----------------------------------------------------------------
    const sidebarContent = document.getElementById('sidebar-content');
    const popup = document.getElementById('tex-preview-popup');
    const previewImage = document.getElementById('tex-preview-image');
    let currentCheckedItem = null;

    // リサイズ関連の要素
    const editorInterface = document.getElementById('editor-interface');
    const editorArea = document.getElementById('editor-area');
    const previewArea = document.getElementById('preview-area');
    const splitter = document.getElementById('splitter');
    let isDragging = false;

    // -----------------------------------------------------------------
    // 1. TeXレンダリングURL生成関数 (ホバープレビュー用 - Codecogs使用)
    // -----------------------------------------------------------------
    function getLatexImageUrl(texCode) {
        const encodedCode = encodeURIComponent(texCode);
        // MathJaxではなくCodeCogsを使用（ホバープレビューは画像の方が表示が安定するため）
        return `https://latex.codecogs.com/gif.latex?${encodedCode}`;
    }

    // -----------------------------------------------------------------
    // 2. イベントリスナーの割り当て (DOMはHTMLで既に生成済み)
    // -----------------------------------------------------------------

    // -----------------------------------------------------------------
    // 2. イベントリスナー (Event Delegation)
    // -----------------------------------------------------------------

    // クリックイベント (クリップボードコピー)
    sidebarContent.addEventListener('click', function (e) {
        const link = e.target.closest('a.tex-item');
        if (!link) return;

        e.preventDefault();
        const texCode = link.getAttribute('data-tex-code');
        if (!texCode) return;

        const inlineToggle = document.getElementById('inline-mode-toggle');
        let textToCopy = texCode;

        // インラインモードがON、かつ、環境定義(begin/display)でない場合に$で囲む
        if (inlineToggle && inlineToggle.checked) {
            // 簡易判定: \begin, \[, $$, $ が含まれていない場合のみ囲む
            if (!texCode.includes('\\begin') && !texCode.includes('\\[') && !texCode.includes('$$') && !texCode.startsWith('$')) {
                textToCopy = `$${texCode}$`;
            }
        }

        navigator.clipboard.writeText(textToCopy).then(() => {
            // 常駐チェックマークの更新
            if (currentCheckedItem) {
                const oldCheckMark = currentCheckedItem.parentElement.querySelector('.copy-checkmark');
                if (oldCheckMark) { oldCheckMark.remove(); }
            }
            const checkMark = document.createElement('span');
            checkMark.textContent = '✓';
            checkMark.className = 'copy-checkmark';
            link.parentElement.appendChild(checkMark);
            currentCheckedItem = link;
        }).catch(err => {
            console.error('クリップボードへのコピーに失敗しました:', err);
            const message = link.parentElement.querySelector('.copy-error-msg');
            if (message) message.remove();

            const errorMsg = document.createElement('span');
            errorMsg.textContent = 'コピー失敗';
            errorMsg.className = 'copy-error-msg';
            errorMsg.style.color = 'red';
            link.parentElement.appendChild(errorMsg);
            setTimeout(() => errorMsg.remove(), 2000);
        });
    });

    // ホバープレビュー (mouseover/mouseout delegation)
    // mouseover/mouseout はバブリングする
    sidebarContent.addEventListener('mouseover', function (e) {
        const link = e.target.closest('a.tex-item');
        if (!link) return;

        const texCode = link.getAttribute('data-tex-code');
        if (!texCode) return;

        // サイドバープレビューはインライン数式としてラップ
        let wrappedCode = texCode;
        if (!texCode.includes('\\begin') && !texCode.includes('\\[')) {
            wrappedCode = `\\inline\\begin{matrix}${texCode}\\end{matrix}`;
        }

        previewImage.src = getLatexImageUrl(wrappedCode);
        const rect = link.getBoundingClientRect();
        popup.style.display = 'block';

        // アイテムの中心座標を計算
        const itemCenterY = rect.top + (rect.height / 2);
        popup.style.top = itemCenterY + 'px';
    });

    sidebarContent.addEventListener('mouseout', function (e) {
        const link = e.target.closest('a.tex-item');
        if (!link) return;

        // 関連ターゲット(移動先)が同じリンク内の要素なら隠さない
        if (link.contains(e.relatedTarget)) return;

        popup.style.display = 'none';
    });

    // -----------------------------------------------------------------
    // 3. 全開閉機能
    // -----------------------------------------------------------------
    document.getElementById('expand-all').addEventListener('click', function () {
        sidebarContent.querySelectorAll('details').forEach(detail => { detail.open = true; });
    });

    document.getElementById('collapse-all').addEventListener('click', function () {
        sidebarContent.querySelectorAll('details').forEach(detail => { detail.open = false; });
    });

    // -----------------------------------------------------------------
    // 4. リサイズ機能
    // -----------------------------------------------------------------

    splitter.addEventListener('mousedown', function (e) {
        e.preventDefault();
        isDragging = true;
        document.body.style.cursor = 'col-resize';
        editorArea.style.userSelect = 'none';
        previewArea.style.userSelect = 'none';
    });

    document.addEventListener('mousemove', function (e) {
        if (!isDragging) return;

        const bounds = editorInterface.getBoundingClientRect();
        const mouseX = e.clientX - bounds.left;

        const splitterWidth = splitter.offsetWidth + 20;
        const availableWidth = bounds.width - splitterWidth;

        let editorWidthPx = mouseX - 10 - splitter.offsetWidth / 2;
        let editorWidthPercent = (editorWidthPx / availableWidth) * 100;

        const minWidth = 150;
        const minWidthPercent = (minWidth / availableWidth) * 100;
        const maxWidthPercent = 100 - minWidthPercent;

        if (editorWidthPercent < minWidthPercent) {
            editorWidthPercent = minWidthPercent;
        } else if (editorWidthPercent > maxWidthPercent) {
            editorWidthPercent = maxWidthPercent;
        }

        editorArea.style.width = editorWidthPercent + '%';
        previewArea.style.width = (100 - editorWidthPercent) + '%';
    });

    document.addEventListener('mouseup', function () {
        if (isDragging) {
            isDragging = false;
            document.body.style.cursor = 'default';
            editorArea.style.userSelect = 'auto';
            previewArea.style.userSelect = 'auto';
        }
    });


    // -----------------------------------------------------------------
    // 5. 検索機能
    // -----------------------------------------------------------------
    const searchBox = document.getElementById('search-box');
    const searchButton = document.getElementById('search-button');

    function executeSearch() {
        const query = searchBox.value.toLowerCase().trim();
        const detailsList = sidebarContent.querySelectorAll('details');

        detailsList.forEach(detail => {
            const items = detail.querySelectorAll('li');
            let hasVisibleItem = false;

            items.forEach(item => {
                const text = item.textContent.toLowerCase();
                if (text.includes(query)) {
                    item.style.display = '';
                    hasVisibleItem = true;
                } else {
                    item.style.display = 'none';
                }
            });

            if (hasVisibleItem) {
                detail.style.display = '';
                if (query !== '') {
                    detail.open = true; // 検索時は開く
                }
            } else {
                detail.style.display = 'none';
            }
        });
    }

    if (searchButton && searchBox) {
        // ボタンクリックで検索
        searchButton.addEventListener('click', executeSearch);

        // Enterキーで検索
        searchBox.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                e.preventDefault(); // フォーム送信を防ぐ
                executeSearch();
            }
        });

        // リアルタイム検索（オプション: 入力時に即時反映させる場合）
        // searchBox.addEventListener('input', executeSearch);
    }

    // -----------------------------------------------------------------
    // 実行
    // -----------------------------------------------------------------

    // DOM要素がロードされた後にイベントリスナーを割り当て
    // attachItemEventListeners(); // Delegationに移行したため不要
});