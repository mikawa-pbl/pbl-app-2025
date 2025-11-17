// scripts/sidebar_logic.js
// サイドバーの開閉、コンテンツの操作、クリップボードコピー、リサイズなどのUI/UXロジックを管理

document.addEventListener('DOMContentLoaded', function() {

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
    
    function attachItemEventListeners() {
        // HTMLで生成された要素に直接リスナーを割り当てる
        const sidebarLinks = sidebarContent.querySelectorAll('a.tex-item');
        sidebarLinks.forEach(link => {
            const texCode = link.getAttribute('data-tex-code');
            
            // ホバープレビュー
            link.addEventListener('mouseenter', function(e) {
                if (!texCode) return;
                // サイドバープレビューはインライン数式としてラップ
                const wrappedCode = `\\inline\\begin{matrix}${texCode}\\end{matrix}`; 
                previewImage.src = getLatexImageUrl(wrappedCode);
                popup.style.display = 'block';
                popup.style.top = (e.pageY - 10) + 'px';
            });
            link.addEventListener('mouseleave', function() { popup.style.display = 'none'; });
            
            // クリップボードコピー
            link.addEventListener('click', function(e) { 
                e.preventDefault(); 
                if (!texCode) return;
                navigator.clipboard.writeText(texCode).then(() => {
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
        });
    }
    
    // -----------------------------------------------------------------
    // 3. 全開閉機能
    // -----------------------------------------------------------------
    document.getElementById('expand-all').addEventListener('click', function() {
      sidebarContent.querySelectorAll('details').forEach(detail => { detail.open = true; });
    });

    document.getElementById('collapse-all').addEventListener('click', function() {
      sidebarContent.querySelectorAll('details').forEach(detail => { detail.open = false; });
    });
    
    // -----------------------------------------------------------------
    // 4. リサイズ機能
    // -----------------------------------------------------------------
    
    splitter.addEventListener('mousedown', function(e) {
        e.preventDefault(); 
        isDragging = true;
        document.body.style.cursor = 'col-resize';
        editorArea.style.userSelect = 'none';
        previewArea.style.userSelect = 'none'; 
    });

    document.addEventListener('mousemove', function(e) {
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

    document.addEventListener('mouseup', function() {
        if (isDragging) {
            isDragging = false;
            document.body.style.cursor = 'default';
            editorArea.style.userSelect = 'auto';
            previewArea.style.userSelect = 'auto'; 
        }
    });


    // -----------------------------------------------------------------
    // 実行
    // -----------------------------------------------------------------
    
    // DOM要素がロードされた後にイベントリスナーを割り当て
    attachItemEventListeners();
});