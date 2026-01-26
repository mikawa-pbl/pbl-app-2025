document.addEventListener('DOMContentLoaded', function () {
  // PDF.js worker setting
  pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
  // CMap setting for Japanese support
  const CMAP_URL = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/bcmaps/';
  const CMAP_PACKED = true;

  const pdfCanvas = document.getElementById('the-canvas');
  if (!pdfCanvas) return; // Canvasがない場合は何もしない

  const ctx = pdfCanvas.getContext('2d');
  let pdfDoc = null;
  let pageNum = 1;
  let pageRendering = false;
  let pageNumPending = null;
  let scale = 1.0;

  // UI Elements
  const zoomInBtn = document.getElementById('zoom-in');
  const zoomOutBtn = document.getElementById('zoom-out');
  const zoomResetBtn = document.getElementById('zoom-reset');
  const savePdfBtn = document.getElementById('save-pdf');
  const canvasContainer = document.getElementById('pdf-render-container');

  // 現在のPDF URLを保持
  let currentPdfUrl = null;

  /**
   * Get page info from document, resize canvas accordingly, and render page.
   * @param num Page number.
   */
  function renderPage(num) {
    pageRendering = true;

    // Fetch page
    return pdfDoc.getPage(num).then(function (page) {
      const viewport = page.getViewport({ scale: scale });

      // Support HiDPI-screens.
      const outputScale = window.devicePixelRatio || 1;

      // Set canvas dimensions (actual resolution)
      pdfCanvas.width = Math.floor(viewport.width * outputScale);
      pdfCanvas.height = Math.floor(viewport.height * outputScale);

      // Set CSS dimensions (display size)
      pdfCanvas.style.width = Math.floor(viewport.width) + "px";
      pdfCanvas.style.height = Math.floor(viewport.height) + "px";

      // Render PDF page into canvas context
      const transform = outputScale !== 1
        ? [outputScale, 0, 0, outputScale, 0, 0]
        : null;

      const renderContext = {
        canvasContext: ctx,
        transform: transform,
        viewport: viewport
      };
      const renderTask = page.render(renderContext);

      // Wait for render to finish
      return renderTask.promise.then(function () {
        pageRendering = false;
        if (pageNumPending !== null) {
          // New page rendering is pending
          renderPage(pageNumPending);
          pageNumPending = null;
        }
      });
    });
  }

  /**
   * If another page rendering in progress, waits until the rendering is
   * finised. Otherwise, executes rendering immediately.
   */
  function queueRenderPage(num) {
    if (pageRendering) {
      pageNumPending = num;
    } else {
      renderPage(num);
    }
  }

  /**
   * PDFをロード・リロードする関数 (外部から呼べるようにwindowに公開するか、イベントで連携)
   * @param {string} url - PDFのURL
   */
  window.loadPDF = function (url) {
    currentPdfUrl = url;
    console.log("Loading PDF from:", url);

    // エラー表示用コンテナを取得または作成
    let errorContainer = document.getElementById('pdf-error-container');
    if (!errorContainer) {
      errorContainer = document.createElement('div');
      errorContainer.id = 'pdf-error-container';
      errorContainer.style.padding = '20px';
      errorContainer.style.color = '#721c24';
      errorContainer.style.backgroundColor = '#f8d7da';
      errorContainer.style.border = '1px solid #f5c6cb';
      errorContainer.style.borderRadius = '5px';
      errorContainer.style.margin = '10px';
      errorContainer.style.whiteSpace = 'pre-wrap';
      errorContainer.style.fontFamily = 'monospace';
      errorContainer.style.overflow = 'auto';
      errorContainer.style.maxHeight = '100%';
      errorContainer.style.display = 'none';

      // canvasContainerの親要素に追加するが、canvasContainer自体を隠す必要があるかもしれない
      canvasContainer.appendChild(errorContainer);
    }

    // まずエラーを非表示、Canvasを表示
    errorContainer.style.display = 'none';
    errorContainer.innerHTML = '';
    pdfCanvas.style.display = 'block';

    // FetchでPDFを取得することでステータスコードを確認
    fetch(url)
      .then(response => {
        if (!response.ok) {
          // エラーの場合 (500 Internal Server Errorなど)
          return response.text().then(text => {
            throw new Error("Compilation Error:\n" + text);
          });
        }
        return response.blob();
      })
      .then(blob => {
        const objectUrl = URL.createObjectURL(blob);
        const loadingTask = pdfjsLib.getDocument({
          url: objectUrl,
          cMapUrl: CMAP_URL,
          cMapPacked: CMAP_PACKED
        });
        return loadingTask.promise;
      })
      .then(function (pdf) {
        pdfDoc = pdf;
        // console.log("PDF Loaded. Pages:", pdf.numPages);
        // console.log("PDF Loaded. Pages:", pdf.numPages);
        return renderPage(pageNum);
      })
      .then(function () {
        // ローディング非表示
        const overlay = document.getElementById('loading-overlay');
        if (overlay) overlay.style.display = 'none';

        // コンパイル完了フラグ OFF & ボタン復帰
        window.isCompiling = false;
        const compileButton = document.getElementById('compile-button');
        if (compileButton) {
          compileButton.disabled = false;
          compileButton.innerHTML = '<span class="material-symbols-rounded">play_arrow</span>';
        }

      }, function (reason) {
        // PDF loading error
        console.error('Error loading PDF:', reason);

        // ローディング非表示 (エラー時も)
        const overlay = document.getElementById('loading-overlay');
        if (overlay) overlay.style.display = 'none';

        // コンパイル完了フラグ OFF & ボタン復帰
        window.isCompiling = false;
        const compileButton = document.getElementById('compile-button');
        if (compileButton) {
          compileButton.disabled = false;
          compileButton.innerHTML = '<span class="material-symbols-rounded">play_arrow</span>';
        }

        // エラーを画面に表示
        // pdfCanvas.style.display = 'none'; // This is already handled below
        // errorContainer.style.display = 'block'; // This is already handled below
        // ... error display logic can remain or be improved here
        pdfCanvas.style.display = 'none';
        errorContainer.style.display = 'block';
        // HTMLタグが含まれている場合があるのでinnerHTMLを使うが、XSSに注意
        // views.pyからは <br><pre>...</pre> で返ってくる想定
        // エラーメッセージの prefix "Compilation Error:\n" を除去して表示
        let msg = reason.message || reason;
        if (typeof msg === 'string' && msg.startsWith("Compilation Error:\n")) {
          msg = msg.substring("Compilation Error:\n".length);
        }
        errorContainer.innerHTML = msg;
      });
  };

  // --------------------------------------------------------
  // Zoom Logic
  // --------------------------------------------------------
  if (zoomInBtn) {
    zoomInBtn.addEventListener('click', function () {
      scale += 0.2;
      if (pdfDoc) queueRenderPage(pageNum);
    });
  }

  if (zoomOutBtn) {
    zoomOutBtn.addEventListener('click', function () {
      if (scale > 0.4) { // Minimum scale
        scale -= 0.2;
        if (pdfDoc) queueRenderPage(pageNum);
      }
    });
  }

  if (zoomResetBtn) {
    zoomResetBtn.addEventListener('click', function () {
      scale = 1.0;
      if (pdfDoc) queueRenderPage(pageNum);
    });
  }

  // --------------------------------------------------------
  // Save Logic
  // --------------------------------------------------------
  if (savePdfBtn) {
    savePdfBtn.addEventListener('click', function () {
      if (!currentPdfUrl) return;

      // ダウンロードリンクを作成してクリック
      const link = document.createElement('a');
      link.href = currentPdfUrl;
      link.download = 'project.pdf'; // ファイル名
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    });
  }
});
