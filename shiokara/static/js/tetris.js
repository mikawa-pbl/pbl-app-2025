// shiokara/static/shiokara/js/tetris.js
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
    title.textContent = "ミニテトリス（矢印キーで操作）";
    container.appendChild(title);

    var info = document.createElement("p");
    info.textContent = "← → : 移動 / ↑ : 回転 / ↓ : 落下加速";
    container.appendChild(info);

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

    var current = null;
    var dropInterval = 500; // ms
    var lastTime = 0;
    var dropCounter = 0;
    var animationId = null;

    function newPiece() {
      var idx = Math.floor(Math.random() * SHAPES.length);
      var shape = SHAPES[idx];
      current = {
        row: 0,
        col: Math.floor(COLS / 2) - Math.floor(shape[0].length / 2),
        shape: shape,
        colorIndex: idx
      };
      if (collides(current, 0, 0)) {
        cancelAnimationFrame(animationId);
        alert("ゲームオーバー");
      }
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

    function drawCell(x, y, color) {
      ctx.fillStyle = color;
      ctx.fillRect(x * BLOCK, y * BLOCK, BLOCK - 1, BLOCK - 1);
    }

    function draw() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // 固定ブロック
      for (var r = 0; r < ROWS; r++) {
        for (var c = 0; c < COLS; c++) {
          var val = board[r][c];
          if (val) {
            drawCell(c, r, COLORS[val - 1]);
          }
        }
      }

      // 落下中ブロック
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
      if (!current) return;
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
      }
    });

    newPiece();
    animationId = requestAnimationFrame(update);
  }
});
