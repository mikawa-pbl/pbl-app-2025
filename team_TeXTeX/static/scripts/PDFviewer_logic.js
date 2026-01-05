document.addEventListener('DOMContentLoaded', function () {
  // PDF.js worker setting
  pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

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
    pdfDoc.getPage(num).then(function (page) {
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
      renderTask.promise.then(function () {
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

    const loadingTask = pdfjsLib.getDocument(url);
    loadingTask.promise.then(function (pdfDoc_) {
      pdfDoc = pdfDoc_;
      // console.log('PDF loaded. Pages:', pdfDoc.numPages);

      // Initial render
      renderPage(pageNum);

    }, function (reason) {
      console.error('Error loading PDF:', reason);
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
