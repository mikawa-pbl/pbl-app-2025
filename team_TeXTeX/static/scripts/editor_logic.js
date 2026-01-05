document.addEventListener('DOMContentLoaded', function () {
  const texInput = document.getElementById('tex-input');
  const compileButton = document.getElementById('compile-button');
  const saveUrl = window.saveFileUrl; // editer.htmlで定義
  const projectId = window.projectId; // editer.htmlで定義

  /**
   * ファイル保存関数
   * @returns {Promise}
   */
  function saveFile() {
    if (!texInput || !saveUrl || !projectId) {
      console.error("Missing required elements for save.");
      return Promise.reject("Missing elements");
    }

    const content = texInput.value;
    console.log("Saving file...");

    // 保存中ステータス表示
    // compileButton.textContent = "保存中..."; 
    compileButton.innerHTML = '<div class="spinner"></div>'; // スピナーを表示
    compileButton.disabled = true;

    const token = window.csrfToken || csrftoken; // window.csrfTokenを優先

    // 現在のファイルID (file_manager.jsで切り替えられた場合)
    // 指定がない場合はデフォルト動作(メインファイル)になるが、
    // 切り替えている場合はそのIDを送る
    const currentFileId = window.currentFileId || null;

    // リクエストボディ
    const payload = {
      project_id: projectId,
      content: content
    };
    // ファイル名ではなくIDで更新指定したいところだが、
    // 現在のAPI(save_file)は project と is_main=True を見ていた。
    // file_manager対応で save_file API も file_id を受け取るように改修したほうがよい。
    // しかしbackendを変える手間があるので、file_manager.jsでファイル名を正しく渡すか、
    // save_file APIを少し拡張する。

    // ここでは payload に file_id があれば追加する
    if (currentFileId) {
      payload.file_id = currentFileId;
    }

    return fetch(saveUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': token
      },
      body: JSON.stringify(payload)
    })
      .then(response => {
        if (!response.ok) {
          throw new Error('Save failed');
        }
        return response.json();
      })
      .then(data => {
        console.log("Saved successfully:", data);
        // 保存完了表示 -> ボタンをアイコンに戻す
        compileButton.innerHTML = '<span class="material-symbols-rounded">play_arrow</span>';
        return data;
      })
      .catch(error => {
        console.error("Save error:", error);
        alert("保存に失敗しました。");
        // エラー時もアイコンに戻す
        compileButton.innerHTML = '<span class="material-symbols-rounded">play_arrow</span>';
      })
      .finally(() => {
        compileButton.disabled = false;
        // finallyでも念のためチェックして戻す
        if (compileButton.querySelector('.spinner')) {
          compileButton.innerHTML = '<span class="material-symbols-rounded">play_arrow</span>';
        }
      });
  }

  // --------------------------------------------------------
  // Shortcut Keys (Ctrl+S / Cmd+S)
  // --------------------------------------------------------
  document.addEventListener('keydown', function (e) {
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
      e.preventDefault(); // ブラウザの保存をキャンセル
      saveFile();
    }
  });

  // --------------------------------------------------------
  // Compile Button Integration (Auto-save before compile)
  // --------------------------------------------------------
  if (compileButton) {
    // 既存のクリックイベントは上書きせず、追加のハンドラとして動作するが、
    // コンパイル処理自体をここで制御したい場合（保存完了を待ちたい場合）は工夫が必要。
    // editer.html 内のインラインスクリプトやPDFviewer_logic.jsと連携する必要がある。

    // 既存のリスナーよりも先に実行されるか、あるいは既存の処理をここでラップするか。
    // シンプルに「保存処理」を呼び出すが、Promiseを返すように設計したので、
    // コンパイルボタンのonclickをここで完全に管理する方が安全。

    // しかし、editer.htmlには既にクリックリスナーがある。
    // 「保存が完了してからコンパイル」を実現するためには、
    // 既存のリスナーを無効化するか、カスタムイベントを使う。

    // 今回は、editer.html側のロジックを修正し、
    // window.saveFile() を呼んでから compile を呼ぶ形にするのがきれい。
    // そのため、ここでは関数をwindowに公開するだけにする。
  }

  // 外部から呼べるように公開
  window.saveAndCompile = function (callback) {
    saveFile().then(() => {
      if (typeof callback === 'function') {
        callback();
      }
    });
  };

  window.saveFile = saveFile;
});
