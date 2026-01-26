function fetchData(tableType) {
    // サーバーのDjangoビューにリクエストを送信
    // URLのパスが正しいか確認してください (例: /team_TeXTeX/get-data/ など、プロジェクト構成による)
    fetch(`get-data/?table_type=${tableType}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // views.pyからは {'data': [...]} という形で返ってくるので data.data を渡す
            updateTable(data.data, tableType);
        })
        .catch(error => {
            console.error('データの取得に失敗しました:', error);
            alert('データの読み込みに失敗しました。');
        });
}

function updateTable(data, tableType) {
    const tableBody = document.getElementById('tableBody');
    const tableHead = document.getElementById('dataTable').querySelector('thead tr');

    // 古い内容をクリア
    tableBody.innerHTML = '';

    // ヘッダーの書き換えと列の定義
    if (tableType === 'users') {
        tableHead.innerHTML = '<th>名前</th><th>TeXコード</th><th>スラッグ</th>';

        data.forEach(item => {
            const row = tableBody.insertRow();
            // JSONのキーに合わせてデータを配置
            row.insertCell().textContent = item.name;

            // コード部分は長い場合に備えて短縮表示などの工夫も可能
            const codeCell = row.insertCell();
            codeCell.textContent = item.tex_code;
            codeCell.style.fontFamily = 'monospace'; // コードっぽく表示

            row.insertCell().textContent = item.function_slug;
        });

    } else if (tableType === 'products') {
        // デモ用：製品一覧ボタンを押したときも同様のデータ形式を表示する場合
        tableHead.innerHTML = '<th>コマンド名</th><th>コードプレビュー</th><th>ID</th>';

        data.forEach(item => {
            const row = tableBody.insertRow();
            row.insertCell().textContent = item.name;
            row.insertCell().textContent = item.tex_code;
            row.insertCell().textContent = item.id; // IDを表示してみる
        });
    }
}

// ページロード時は何も表示しないか、デフォルトを表示するか選択
// document.addEventListener('DOMContentLoaded', () => {
//     fetchData('users');
// });
