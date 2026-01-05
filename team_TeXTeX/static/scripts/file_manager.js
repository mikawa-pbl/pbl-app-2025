document.addEventListener('DOMContentLoaded', function () {
  console.log("File manager script loaded");
  const fileHeader = document.querySelector('#editor-area .editor-header h2');
  const projectId = window.projectId;
  const csrfToken = window.csrfToken;
  let currentFileId = null;
  let lastAccessedPath = ""; // 最後にアクセスしたパス (ファイルまたはフォルダ)

  if (!fileHeader) {
    console.error("File header h2 not found");
    return;
  }

  // ヘッダーをボタン化
  fileHeader.style.cursor = 'pointer';
  fileHeader.classList.add('clickable-header');
  fileHeader.title = "Click to manage files";
  // アイコン追加
  const iconSpan = document.createElement('span');
  iconSpan.className = 'material-symbols-rounded';
  iconSpan.textContent = 'expand_more';
  iconSpan.style.verticalAlign = 'middle';
  iconSpan.style.marginLeft = '5px';
  iconSpan.style.fontSize = '20px';
  fileHeader.appendChild(iconSpan);

  // モーダル(Popover)作成
  const modal = document.createElement('div');
  modal.id = 'file-manager-modal';
  modal.className = 'modal';
  modal.style.display = 'none';

  // コンテンツラッパー (配置制御用)
  const modalContent = document.createElement('div');
  modalContent.className = 'modal-content';
  modalContent.innerHTML = `
        <div class="modal-body">
            <div class="file-toolbar" style="display:flex; gap:5px;">
                <button id="new-file-btn" title="Create File"><span class="material-symbols-rounded">note_add</span></button>
                <button id="new-folder-btn" title="Create Folder"><span class="material-symbols-rounded">create_new_folder</span></button>
                <button id="rename-btn" title="Rename"><span class="material-symbols-rounded">edit</span></button>
                <button id="import-btn" title="Import File"><span class="material-symbols-rounded">upload_file</span></button>
                <button id="save-project-btn" title="Save Project"><span class="material-symbols-rounded">download</span></button>
                <input type="file" id="file-upload-input" style="display: none;">
            </div>
            <div id="file-tree" class="file-tree">Loading...</div>
        </div>
    `;
  modal.appendChild(modalContent);
  document.body.appendChild(modal);

  const fileTree = modalContent.querySelector('#file-tree');
  const newFileBtn = modalContent.querySelector('#new-file-btn');
  const newFolderBtn = modalContent.querySelector('#new-folder-btn');
  const renameBtn = modalContent.querySelector('#rename-btn');
  const importBtn = modalContent.querySelector('#import-btn');
  const fileUploadInput = modalContent.querySelector('#file-upload-input');
  const saveProjectBtn = modalContent.querySelector('#save-project-btn');

  // イベントリスナー
  fileHeader.addEventListener('click', (e) => {
    e.stopPropagation(); // バブリング防止
    toggleModal();
  });

  window.addEventListener('click', (event) => {
    if (event.target == modal) {
      modal.style.display = 'none';
    }
  });

  newFileBtn.addEventListener('click', () => {
    const base = getLastContextPath();
    const input = prompt(`Create new file in: ${base}\nEnter filename (e.g. newfile.tex):`);
    if (input) {
      // パス結合: base が空なら input そのもの、そうでなければ base/input
      const fullPath = base ? `${base}/${input}`.replace(/\/+/g, '/') : input;
      createFile(fullPath);
    }
  });

  newFolderBtn.addEventListener('click', () => {
    const base = getLastContextPath();
    const input = prompt(`Create new folder in: ${base}\nEnter folder name:`);
    if (input) {
      const fullPath = base ? `${base}/${input}`.replace(/\/+/g, '/') : input;
      createFolder(fullPath);
    }
  });

  renameBtn.addEventListener('click', () => {
    if (!lastAccessedPath && lastAccessedPath !== "") { // "" is for root
      alert("Select a file or folder to rename.");
      return;
    }

    triggerRename(lastAccessedPath);
  });

  importBtn.addEventListener('click', () => {
    // 隠しinputをクリック
    fileUploadInput.click();
  });

  fileUploadInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const base = getLastContextPath(); // アップロード先フォルダ

    const formData = new FormData();
    formData.append('project_id', projectId);
    formData.append('file', file);
    formData.append('upload_path', base);

    fetch('/team_TeXTeX/api/file/upload/', {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrfToken
      },
      body: formData
    })
      .then(res => res.json())
      .then(data => {
        if (data.error) throw new Error(data.error);
        loadFileTree();
        fileUploadInput.value = ''; // リセット
      })
      .catch(err => {
        alert("Upload failed: " + err.message);
        fileUploadInput.value = '';
      });
  });

  saveProjectBtn.addEventListener('click', () => {
    // プロジェクトをZIPでダウンロード
    const url = `/team_TeXTeX/api/project/${projectId}/download/`;
    window.location.href = url;
  });

  function toggleModal() {
    if (modal.style.display === 'block') {
      modal.style.display = 'none';
    } else {
      openModal();
    }
  }

  function openModal() {
    // 位置計算
    const rect = fileHeader.getBoundingClientRect();
    modalContent.style.top = (rect.bottom + 5) + 'px'; // ヘッダーのすぐ下
    modalContent.style.left = rect.left + 'px';       // ヘッダーの左端に合わせる

    modal.style.display = 'block';
    loadFileTree();
  }

  function loadFileTree() {
    fileTree.innerHTML = '<div class="spinner" style="border-color:#555; border-top-color:transparent; margin:10px auto;"></div>';

    fetch(`/team_TeXTeX/api/file/list/?project_id=${projectId}`)
      .then(res => res.json())
      .then(data => {
        if (data.error) throw new Error(data.error);
        // プロジェクト名保存 (グローバルまたはスコープ変数)
        window.currentProjectName = data.project_name || "Project Root";
        renderFileTree(data.files, window.currentProjectName);

        // 初回ロード時などでヘッダーがまだ更新されていない場合、更新する
        if (window.currentFileId) {
          // 現在のファイル名がわかるなら formatPath を呼び直したいが、
          // ここではヘッダーの表示更新は switchFile などで行うので、
          // プロジェクト名が変わった後のフォーマット反映は switchFile が呼ばれたタイミングか、
          // ここで現在のヘッダーテキストを再構築するか。
          // 既存のヘッダー更新処理は switchFile に依存しているため、
          // ここではツリー表示のみを責務とする。
        }
      })
      .catch(err => {
        fileTree.textContent = "Error: " + err.message;
      });
  }

  // フラットなファイルリストをツリー構造に変換してレンダリング
  function renderFileTree(files, projectName) {
    fileTree.innerHTML = '';
    const treeData = buildTreeData(files);

    // Root Item
    const rootItem = document.createElement('div');
    rootItem.className = 'folder-item root-item';
    rootItem.innerHTML = `<span class="material-symbols-rounded folder-icon" style="color:#28a745;">home</span> ${projectName}`;
    rootItem.addEventListener('click', () => {
      lastAccessedPath = "";
      highlightLastAccessed();
    });

    // Root Item Double Click to Rename Project
    rootItem.addEventListener('dblclick', (e) => {
      e.stopPropagation();
      const newName = prompt("Rename Project:", projectName);
      if (newName && newName !== projectName) {
        renameProject(newName);
      }
    });

    fileTree.appendChild(rootItem);

    const ul = createTreeList(treeData, "");
    ul.classList.add('expanded'); // ルートは展開
    ul.style.display = 'block';
    fileTree.appendChild(ul);

    highlightLastAccessed();
  }

  function getLastContextPath() {
    // lastAccessedPathがファイルならその親ディレクトリ、フォルダならそのもの
    if (!lastAccessedPath) return "";
    // 拡張子があるか簡易判定 (実際には treeData から isFile を引くのが正確だが文字列表面で判断)
    if (lastAccessedPath.match(/\.[a-zA-Z0-9]+$/)) {
      const parts = lastAccessedPath.split('/');
      parts.pop();
      return parts.join('/');
    }
    return lastAccessedPath;
  }

  function highlightLastAccessed() {
    // すべてのハイライト解除
    document.querySelectorAll('.tree-highlight').forEach(el => el.classList.remove('tree-highlight'));

    // lastAccessedPath にマッチする要素を探すのは難しい（data属性を持たせるのが良い）
    if (lastAccessedPath === "") {
      const root = fileTree.querySelector('.root-item');
      if (root) root.classList.add('tree-highlight');
    } else {
      const target = fileTree.querySelector(`[data-path="${lastAccessedPath}"]`);
      if (target) target.classList.add('tree-highlight');
    }
  }

  function buildTreeData(files) {
    const root = {};

    files.forEach(file => {
      const parts = file.filename.split('/');
      let current = root;

      parts.forEach((part, index) => {
        if (!current[part]) {
          current[part] = {
            name: part,
            isFile: (index === parts.length - 1),
            children: {},
            fileData: (index === parts.length - 1) ? file : null
          };
        }
        current = current[part].children;
      });
    });
    return root;
  }

  function createTreeList(nodes, parentPath) {
    const ul = document.createElement('ul');
    ul.className = 'file-list';

    // フォルダ優先ソート (フォルダ -> ファイル)
    const keys = Object.keys(nodes).sort((a, b) => {
      const nodeA = nodes[a];
      const nodeB = nodes[b];
      if (nodeA.isFile === nodeB.isFile) return a.localeCompare(b);
      return nodeA.isFile ? 1 : -1; // フォルダが先
    });

    keys.forEach(key => {
      const node = nodes[key];
      const li = document.createElement('li');
      const currentPath = parentPath ? `${parentPath}/${key}` : key;

      if (node.isFile) {
        // ファイルノード
        // .keep ファイルは表示しない
        if (node.fileData.filename.endsWith('.keep')) return;

        renderFileNode(li, node.fileData, currentPath);
      } else {
        // フォルダノード
        renderFolderNode(li, node, key, currentPath);
      }
      ul.appendChild(li);
    });
    return ul;
  }

  function triggerRename(path) {
    if (!path) return; // Root logic here if path===""
    if (path === "") {
      const newName = prompt("Rename Project:", window.currentProjectName);
      if (newName && newName !== window.currentProjectName) {
        renameProject(newName);
      }
      return;
    }

    const currentName = path.split('/').pop();
    const lastSlash = path.lastIndexOf('/');
    let parent = "";
    if (lastSlash !== -1) {
      parent = path.substring(0, lastSlash);
    }

    // Is it a folder or file? Check DOM.
    const el = document.querySelector(`[data-path="${path}"]`);
    if (el && el.classList.contains('folder-item')) {
      const newName = prompt(`Rename folder:`, currentName);
      if (newName && newName !== currentName) {
        const newFullPath = parent ? `${parent}/${newName}` : newName;
        renameFolder(path, newFullPath);
      }
    } else if (el && el.getAttribute('data-file-id')) {
      if (el.closest('.file-item').classList.contains('is-main')) {
        alert("Cannot rename main file.");
        return;
      }
      const newName = prompt(`Rename file:`, currentName);
      if (newName && newName !== currentName) {
        const newFullPath = parent ? `${parent}/${newName}` : newName;
        renameFile(el.getAttribute('data-file-id'), newFullPath);
      }
    }
  }

  // 展開状態を保持するセット
  const expandedPaths = new Set();

  function buildTreeData(files) {
    const root = {};
    files.forEach(file => {
      const parts = file.filename.split('/');
      let current = root;
      let pathSoFar = "";
      parts.forEach((part, index) => {
        pathSoFar = pathSoFar ? pathSoFar + "/" + part : part;
        if (!current[part]) {
          current[part] = {
            name: part,
            path: pathSoFar,
            children: {},
            isFile: (index === parts.length - 1)
          };
          if (current[part].isFile) {
            current[part].fileData = file;
          }
        }
        current = current[part].children;
      });
    });
    return root;
  }

  function createTreeList(nodeChildren, parentPath) {
    const ul = document.createElement('ul');
    ul.className = 'file-list';
    ul.style.display = 'none';

    const keys = Object.keys(nodeChildren).sort((a, b) => {
      // フォルダ優先
      const nodeA = nodeChildren[a];
      const nodeB = nodeChildren[b];
      const isFileA = nodeA.isFile;
      const isFileB = nodeB.isFile;
      if (isFileA && !isFileB) return 1;
      if (!isFileA && isFileB) return -1;
      return a.localeCompare(b);
    });

    keys.forEach(key => {
      const node = nodeChildren[key];
      const li = document.createElement('li');
      if (node.isFile) {
        renderFileNode(li, node.fileData, node.path);
      } else {
        renderFolderNode(li, node, node.name, node.path);
      }
      ul.appendChild(li);
    });
    return ul;
  }

  function renderFolderNode(li, node, folderName, fullPath) {
    const div = document.createElement('div');
    div.className = 'folder-item';
    div.setAttribute('data-path', fullPath);

    // アイコンと名前を分離
    const iconSpan = document.createElement('span');
    iconSpan.className = 'material-symbols-rounded folder-icon';
    iconSpan.style.marginRight = '5px';

    const nameSpan = document.createElement('span');
    nameSpan.className = 'folder-name';
    nameSpan.textContent = folderName;

    div.appendChild(iconSpan);
    div.appendChild(nameSpan);

    const childrenUl = createTreeList(node.children, fullPath);

    // 展開状態の復元
    if (expandedPaths.has(fullPath)) {
      childrenUl.style.display = 'block';
      iconSpan.textContent = 'folder_open';
    } else {
      childrenUl.style.display = 'none';
      iconSpan.textContent = 'folder';
    }

    const toggleFolder = () => {
      if (childrenUl.style.display === 'none') {
        childrenUl.style.display = 'block';
        iconSpan.textContent = 'folder_open';
        expandedPaths.add(fullPath);
      } else {
        childrenUl.style.display = 'none';
        iconSpan.textContent = 'folder';
        expandedPaths.delete(fullPath);
      }
    };

    // アイコンクリック: 展開/折りたたみ + 選択
    iconSpan.addEventListener('click', (e) => {
      e.stopPropagation();
      lastAccessedPath = fullPath;
      highlightLastAccessed();
      toggleFolder();
    });

    // 行クリック: 選択のみ
    div.addEventListener('click', (e) => {
      e.stopPropagation();
      lastAccessedPath = fullPath;
      highlightLastAccessed();
    });

    // ダブルクリック: 展開/折りたたみ
    div.addEventListener('dblclick', (e) => {
      e.stopPropagation();
      toggleFolder();
    });

    // コンテキストメニュー: リネーム
    div.addEventListener('contextmenu', (e) => {
      e.preventDefault();
      e.stopPropagation();
      lastAccessedPath = fullPath;
      highlightLastAccessed();
      triggerRename(fullPath);
    });

    li.appendChild(div);
    li.appendChild(childrenUl);
  }

  function renderFileNode(li, file, fullPath) {
    li.className = 'file-item';
    if (file.is_main) li.classList.add('is-main');

    const iconName = file.filename.endsWith('.tex') ? 'description' : 'insert_drive_file';

    const contentDiv = document.createElement('div');
    contentDiv.style.flexGrow = 1;
    contentDiv.style.display = 'flex';
    contentDiv.style.alignItems = 'center';
    contentDiv.setAttribute('data-path', fullPath);
    contentDiv.setAttribute('data-file-id', file.id);

    contentDiv.innerHTML = `<span class="material-symbols-rounded file-icon">${iconName}</span> <span class="file-name">${file.filename.split('/').pop()}</span>`;

    // クリック -> ファイル切り替え (即時)
    contentDiv.addEventListener('click', (e) => {
      e.stopPropagation();
      lastAccessedPath = fullPath;
      highlightLastAccessed();
      switchFile(file.id);
    });

    // ダブルクリック -> 何もしない (リネームもしない、切り替えはclickで済んでいる)
    contentDiv.addEventListener('dblclick', (e) => {
      e.stopPropagation();
    });

    // コンテキストメニュー -> リネーム
    if (!file.is_main) {
      contentDiv.addEventListener('contextmenu', (e) => {
        e.preventDefault();
        e.stopPropagation();
        lastAccessedPath = fullPath;
        highlightLastAccessed();
        triggerRename(fullPath);
      });
    }

    // コントロール (削除)
    const controls = document.createElement('div');
    controls.className = 'file-controls';

    if (!file.is_main) {
      const deleteBtn = document.createElement('span');
      deleteBtn.className = 'material-symbols-rounded action-icon';
      deleteBtn.textContent = 'delete';
      deleteBtn.style.fontSize = "16px";
      deleteBtn.onclick = (e) => {
        e.stopPropagation();
        if (confirm(`Delete ${file.filename}?`)) deleteFile(file.id);
      };
      controls.appendChild(deleteBtn);
    }

    li.appendChild(contentDiv);
    li.appendChild(controls);
  }

  function createFile(filename) {
    fetch('/team_TeXTeX/api/file/create/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
      body: JSON.stringify({ project_id: projectId, filename: filename })
    }).then(res => res.json()).then(data => {
      if (data.error) throw new Error(data.error);
      loadFileTree();
    }).catch(err => alert(err));
  }

  function createFolder(folderName) {
    fetch('/team_TeXTeX/api/file/create_folder/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
      body: JSON.stringify({ project_id: projectId, folder_name: folderName })
    }).then(res => res.json()).then(data => {
      if (data.error) throw new Error(data.error);
      loadFileTree();
    }).catch(err => alert(err));
  }

  function renameFile(fileId, newFilename) {
    fetch('/team_TeXTeX/api/file/rename/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
      body: JSON.stringify({ file_id: fileId, new_filename: newFilename })
    }).then(res => res.json()).then(data => {
      if (data.error) throw new Error(data.error);
      loadFileTree();
    }).catch(err => alert(err));
  }

  function renameFolder(oldName, newName) {
    fetch('/team_TeXTeX/api/file/rename_folder/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
      body: JSON.stringify({ project_id: projectId, old_folder_name: oldName, new_folder_name: newName })
    }).then(res => res.json()).then(data => {
      if (data.error) throw new Error(data.error);
      loadFileTree();
    }).catch(err => alert(err));
  }

  function renameProject(newName) {
    fetch('/team_TeXTeX/api/project/rename/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
      body: JSON.stringify({ project_id: projectId, new_project_name: newName })
    }).then(res => res.json()).then(data => {
      if (data.error) throw new Error(data.error);
      window.currentProjectName = data.project_name;
      loadFileTree();

      // ヘッダーのプロジェクト名部分を更新
      //formatPathが更新されたprojectNameを使うようになるが、現在表示中のパスを再描画する必要がある
      if (fileHeader.childNodes[0].nodeType === 3) {
        const currentText = fileHeader.childNodes[0].nodeValue; // ex: "OldName/folder/file.tex"
        const parts = currentText.split('/');
        // 最初の要素(ProjectName)を置換
        if (parts.length > 0) {
          parts[0] = data.project_name;
          // formatPath は "ProjectName/..." の省略ロジックを持つが、
          // ここでは単純に先頭を置き換えてみる、あるいは現在のファイルIDがわかっていれば switchFile(currentId) を呼ぶのが確実
          // しかしファイルIDなしでUI操作している場合もあるので文字列置換
          fileHeader.childNodes[0].nodeValue = parts.join('/');
        }
      }
    }).catch(err => alert("Error renaming project: " + err.message));
  }

  function deleteFile(fileId) {
    fetch('/team_TeXTeX/api/file/delete/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
      body: JSON.stringify({ file_id: fileId })
    }).then(res => res.json()).then(data => {
      if (data.error) throw new Error(data.error);
      loadFileTree();
    }).catch(err => alert(err));
  }

  function switchFile(fileId) {
    const texInput = document.getElementById('tex-input');
    texInput.value = "Loading...";
    texInput.disabled = true;

    fetch(`/team_TeXTeX/api/file/content/?file_id=${fileId}`)
      .then(res => res.json())
      .then(data => {
        if (data.error) throw new Error(data.error);
        texInput.value = data.content;
        texInput.disabled = false;

        const displayPath = formatPath(data.filename);

        if (fileHeader.childNodes[0].nodeType === 3) {
          fileHeader.childNodes[0].nodeValue = displayPath;
        } else {
          const textNode = document.createTextNode(displayPath);
          fileHeader.insertBefore(textNode, fileHeader.firstChild);
        }

        window.currentFileId = data.id;
        modal.style.display = 'none';
      })
      .catch(err => {
        texInput.value = "Error loading file.";
        alert("Error: " + err.message);
      });
  }

  function formatPath(filename) {
    const parts = filename.split('/');
    // グローバルの window.currentProjectName を使用、なければデフォルト
    const rootPrefix = (window.currentProjectName || "project_root") + "/";

    if (parts.length >= 3) {
      return rootPrefix + ".../" + parts[parts.length - 1];
    } else {
      return rootPrefix + filename;
    }
  }
});
