// scripts/preview_logic.js
// エディタのプレビュー機能のみを管理 (MathJax対応)

document.addEventListener('DOMContentLoaded', function() {

    const texInput = document.getElementById('tex-input');
    const texOutput = document.getElementById('tex-output');
    const previewButton = document.getElementById('preview-button');
    
    // -----------------------------------------------------------------
    // 1. MathJaxを使用したエディタプレビュー実行関数
    // -----------------------------------------------------------------
    function updatePreview() {
        const rawCode = texInput.value;
        
        if (rawCode.trim() === '') {
            texOutput.innerHTML = '<p>結果がここに表示されます。</p>';
            return;
        }
        
        // MathJaxレンダリングのために、コード全体を処理するコンテナを準備
        texOutput.innerHTML = `
            <div id="mathjax-container" style="text-align: left; padding: 10px;">
                <p>処理中...</p>
            </div>`;
            
        const mathJaxContainer = document.getElementById('mathjax-container');
        
        // MathJaxがエラーを報告できるように、生のコードを挿入
        mathJaxContainer.textContent = rawCode;


        // MathJaxが読み込まれていることを確認し、処理を開始
        if (window.MathJax) {
            
            // MathJaxの処理が完了した後に実行されるフック
            MathJax.startup.promise.then(() => {
                
                // MathJaxに新しいコンテンツを処理させる
                MathJax.typesetPromise([mathJaxContainer])
                    .then(() => {
                        // 処理が成功した場合（エラーチェックはMathJaxが内部で行う）
                        const errorNode = mathJaxContainer.querySelector('.MJX-TEX-ERROR');
                        if (errorNode) {
                            // MathJaxが検出したエラーを表示
                             texOutput.innerHTML = `<div style="color: red; padding: 10px; border: 1px dashed red;">
                                <strong>構文エラー:</strong> ${errorNode.textContent}
                            </div>`;
                        } else if (mathJaxContainer.textContent.trim() === '') {
                            // 結果が空の場合（例: \documentclassのみで本文がない場合）
                             texOutput.innerHTML = `<div style="color: gray; padding: 10px;">
                                <strong>プレビュー成功:</strong> ただし、レンダリング可能な出力がありません。
                            </div>`;
                        } else {
                            // 成功
                            mathJaxContainer.style.textAlign = 'center';
                        }
                    })
                    .catch((err) => {
                        // MathJax自体の処理が失敗した場合（稀）
                        texOutput.innerHTML = `<div style="color: red; padding: 10px; border: 1px dashed red;">
                            <strong>MathJax処理失敗:</strong> ${err.message}
                        </div>`;
                    });
            });
            
        } else {
            // MathJaxがまだロードされていない、または無効な場合
            texOutput.innerHTML = `<div style="color: orange; padding: 10px;">MathJaxがロードされていません。しばらくお待ちください。</div>`;
        }
    }
    
    // -----------------------------------------------------------------
    // 3. イベントリスナーの設定
    // -----------------------------------------------------------------

    // プレビューボタンがクリックされたときに更新を実行
    previewButton.addEventListener('click', updatePreview);
});