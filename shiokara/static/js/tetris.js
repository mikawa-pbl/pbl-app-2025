// shiokara/static/js/tetris.js
document.addEventListener("DOMContentLoaded", function () {
  var form = document.getElementById("company-search-form");
  if (!form) {
    // このページに検索フォームがなければ何もしない
    return;
  }

  var input = document.getElementById("company-search-q");
  var tetrisRoot = document.getElementById("tetris-root");
  var gameStarted = false;

  // フォーム送信時に「テトリス」ならゲーム起動
  form.addEventListener("submit", function (event) {
    if (!input) return;
    var value = input.value.trim();
    if (value === "テトリス" || value.toLowerCase() === "tetris") {
      event.preventDefault();
      if (!gameStarted) {
        startTetris(tetrisRoot);
        gameStarted = true;
      }
    }
  });

  function startTetris(root) {
    if (!root) {
      root = document.body;
    }

    // --- 画面の用意 ---
    var container = document.createElement("div");

    var title = document.createElement("h2");
    title.textContent = "ミニテトリス（矢印キー / C: ホールド）あああああああああああああああああああああああああ";
    container.appendChild(title);

    var info = document.createElement("p");
    info.textContent = "← → : 移動 / ↑ : 回転 / ↓ : 落下加速 / C : ホールドああああああああああああああああ";
    container.appendChild(info);

    // ホールド情報表示
    var holdInfo = document.createElement("p");
    container.appendChild(holdInfo);

    var canvas = document.createElement("canvas");
    canvas.id = "tetris-canvas";
    container.appendChild(canvas);

    // 既存の中身を消して差し替え
    root.innerHTML = "";
    root.appendChild(container);

    // --- ゲーム本体 ---
    var COLS = 10;
    var ROWS = 20;
    var BLOCK = 24;

    canvas.width = COLS * BLOCK;
    canvas.height = ROWS * BLOCK;

    var ctx = canvas.getContext("2d");

    // 盤面
    var board = [];
    for (var r = 0; r < ROWS; r++) {
      board[r] = [];
      for (var c = 0; c < COLS; c++) {
        board[r][c] = 0;
      }
    }

    var SHAPES = [
      [[1, 1, 1, 1]],                // I
      [[1, 1], [1, 1]],              // O
      [[0, 1, 0], [1, 1, 1]],        // T
      [[1, 0, 0], [1, 1, 1]],        // J
      [[0, 0, 1], [1, 1, 1]],        // L
      [[1, 1, 0], [0, 1, 1]],        // S
      [[0, 1, 1], [1, 1, 0]]         // Z
    ];

    var COLORS = [
      "#00f0f0", "#f0f000", "#a000f0",
      "#0000f0", "#f0a000", "#00f000", "#f00000"
    ];

    var PIECE_NAMES = ["I", "O", "T", "J", "L", "S", "Z"];

    // 7-BAG ランダマイザ用
    var bag = [];
    function refillBag() {
      bag = [0, 1, 2, 3, 4, 5, 6];
      // フィッシャー–イェーツのシャッフル
      for (var i = bag.length - 1; i > 0; i--) {
        var j = Math.floor(Math.random() * (i + 1));
        var tmp = bag[i];
        bag[i] = bag[j];
        bag[j] = tmp;
      }
    }
    function nextRandomIndex() {
      if (bag.length === 0) {
        refillBag();
      }
      return bag.shift();
    }

    // 現在のピース・ホールド・ゲーム状態
    var current = null;
    var holdIndex = null;   // ホールド中のピース（型）インデックス
    var canHold = true;     // このターンでホールドできるか（1ターン1回制限）
    var dropInterval = 500; // ms
    var lastTime = 0;
    var dropCounter = 0;
    var animationId = null;
    var gameOver = false;

    function updateHoldInfo() {
      var text = "ホールド: ";
      if (holdIndex === null) {
        text += "なし";
      } else {
        text += PIECE_NAMES[holdIndex];
      }
      text += "（Cキーでホールド）";
      holdInfo.textContent = text;
    }

    function createPiece(idx) {
      var shape = SHAPES[idx];
      // shape はそのまま参照でOK（回転時は新しい配列を生成）
      return {
        row: 0,
        col: Math.floor(COLS / 2) - Math.floor(shape[0].length / 2),
        shape: shape,
        colorIndex: idx,
        typeIndex: idx
      };
    }

    function spawnPiece(idx) {
      current = createPiece(idx);
      canHold = true; // 新しいピースが出たターンではまたホールドできる

      // 出現時にすでに衝突していたらゲームオーバー
      if (collides(current, 0, 0)) {
        gameOver = true;
        cancelAnimationFrame(animationId);
        draw(); // 最後の状態を描画
        alert("ゲームオーバー");
      }
    }

    function newPiece() {
      var idx = nextRandomIndex();
      spawnPiece(idx);
    }

    function rotate(shape) {
      var rows = shape.length;
      var cols = shape[0].length;
      var res = [];
      for (var c = 0; c < cols; c++) {
        res[c] = [];
        for (var r = rows - 1; r >= 0; r--) {
          res[c][rows - 1 - r] = shape[r][c];
        }
      }
      return res;
    }

    function collides(piece, dr, dc, newShape) {
      var shape = newShape || piece.shape;
      for (var r = 0; r < shape.length; r++) {
        for (var c = 0; c < shape[r].length; c++) {
          if (!shape[r][c]) continue;
          var nr = piece.row + r + dr;
          var nc = piece.col + c + dc;
          if (nr < 0 || nr >= ROWS || nc < 0 || nc >= COLS) {
            return true;
          }
          if (board[nr][nc]) {
            return true;
          }
        }
      }
      return false;
    }

    function merge(piece) {
      var shape = piece.shape;
      for (var r = 0; r < shape.length; r++) {
        for (var c = 0; c < shape[r].length; c++) {
          if (shape[r][c]) {
            board[piece.row + r][piece.col + c] = piece.colorIndex + 1;
          }
        }
      }
    }

    function clearLines() {
      for (var r = ROWS - 1; r >= 0; r--) {
        var full = true;
        for (var c = 0; c < COLS; c++) {
          if (!board[r][c]) {
            full = false;
            break;
          }
        }
        if (full) {
          // 1行詰める
          for (var y = r; y > 0; y--) {
            for (var x = 0; x < COLS; x++) {
              board[y][x] = board[y - 1][x];
            }
          }
          for (var x2 = 0; x2 < COLS; x2++) {
            board[0][x2] = 0;
          }
          r++; // 同じ行をもう一度チェック
        }
      }
    }

    // ゴーストピース（着地位置）を求める
    function getGhostPiece(piece) {
      if (!piece) return null;

      // コピーを作って下に落としていく
      var ghost = {
        row: piece.row,
        col: piece.col,
        shape: piece.shape,
        colorIndex: piece.colorIndex,
        typeIndex: piece.typeIndex
      };

      while (!collides(ghost, 1, 0)) {
        ghost.row++;
      }
      return ghost;
    }

    // ホールド処理（Cキー）
    function handleHold() {
      if (!current || gameOver || !canHold) return;

      var currentIndex = current.typeIndex;

      if (holdIndex === null) {
        // 初回ホールド：今のピースをホールドして、新しいピースをランダム出現
        holdIndex = currentIndex;
        newPiece();
      } else {
        // 2回目以降：ホールドピースと今のピースを交換
        var temp = holdIndex;
        holdIndex = currentIndex;
        spawnPiece(temp);
      }

      canHold = false; // このターンではもうホールドできない
      updateHoldInfo();
    }

    function drawCell(x, y, color) {
      ctx.fillStyle = color;
      ctx.fillRect(x * BLOCK, y * BLOCK, BLOCK - 1, BLOCK - 1);
    }

    function drawGrid() {
      // 背景（設置可能エリアをはっきりさせるため、青みのある色に）
      ctx.fillStyle = "#e0f7fa";
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // グリッド線
      ctx.strokeStyle = "#b0bec5";
      ctx.lineWidth = 1;

      // 縦線
      for (var x = 0; x <= COLS; x++) {
        ctx.beginPath();
        ctx.moveTo(x * BLOCK + 0.5, 0);
        ctx.lineTo(x * BLOCK + 0.5, ROWS * BLOCK);
        ctx.stroke();
      }
      // 横線
      for (var y = 0; y <= ROWS; y++) {
        ctx.beginPath();
        ctx.moveTo(0, y * BLOCK + 0.5);
        ctx.lineTo(COLS * BLOCK, y * BLOCK + 0.5);
        ctx.stroke();
      }

      // 枠線（プレイエリアの境界を強調）
      ctx.strokeStyle = "#455a64";
      ctx.lineWidth = 2;
      ctx.strokeRect(0.5, 0.5, COLS * BLOCK - 1, ROWS * BLOCK - 1);
    }

    function draw() {
      // まずプレイエリア（グリッド）を描画
      drawGrid();

      // 固定ブロック
      for (var r = 0; r < ROWS; r++) {
        for (var c = 0; c < COLS; c++) {
          var val = board[r][c];
          if (val) {
            drawCell(c, r, COLORS[val - 1]);
          }
        }
      }

      // ゴーストピース（現在のピースが着地する位置）
      if (current) {
        var ghost = getGhostPiece(current);
        if (ghost) {
          var gShape = ghost.shape;

          // ゴーストは「枠線だけ」で描画（着地位置のガイド）
          ctx.strokeStyle = "#78909c";
          ctx.lineWidth = 1.5;

          for (var gr = 0; gr < gShape.length; gr++) {
            for (var gc = 0; gc < gShape[gr].length; gc++) {
              if (gShape[gr][gc]) {
                var gx = (ghost.col + gc) * BLOCK;
                var gy = (ghost.row + gr) * BLOCK;
                ctx.strokeRect(gx + 0.5, gy + 0.5, BLOCK - 1, BLOCK - 1);
              }
            }
          }
        }
      }

      // 落下中ブロック本体
      if (current) {
        var shape = current.shape;
        for (var r2 = 0; r2 < shape.length; r2++) {
          for (var c2 = 0; c2 < shape[r2].length; c2++) {
            if (shape[r2][c2]) {
              drawCell(
                current.col + c2,
                current.row + r2,
                COLORS[current.colorIndex]
              );
            }
          }
        }
      }
    }

    function update(time) {
      if (gameOver) return;

      if (!lastTime) lastTime = time;
      var delta = time - lastTime;
      lastTime = time;
      dropCounter += delta;

      if (dropCounter > dropInterval) {
        dropCounter = 0;
        if (!current) {
          newPiece();
        } else {
          if (!collides(current, 1, 0)) {
            current.row++;
          } else {
            // 固定して次のピースへ
            merge(current);
            clearLines();
            newPiece();
          }
        }
      }

      draw();
      animationId = requestAnimationFrame(update);
    }

    // キー入力
    document.addEventListener("keydown", function (event) {
      if (!current || gameOver) return;

      if (event.key === "ArrowLeft") {
        if (!collides(current, 0, -1)) {
          current.col--;
        }
      } else if (event.key === "ArrowRight") {
        if (!collides(current, 0, 1)) {
          current.col++;
        }
      } else if (event.key === "ArrowDown") {
        if (!collides(current, 1, 0)) {
          current.row++;
        }
      } else if (event.key === "ArrowUp") {
        var rotated = rotate(current.shape);
        if (!collides(current, 0, 0, rotated)) {
          current.shape = rotated;
        }
      } else if (event.key === "c" || event.key === "C") {
        // ホールド
        handleHold();
      }
    });

    // 初期状態
    holdIndex = null;
    updateHoldInfo();
    newPiece();
    animationId = requestAnimationFrame(update);
  }
});
