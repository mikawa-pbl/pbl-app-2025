# myapp/management/commands/data.py
# (アプリ名が team_TeXTeX の場合、team_TeXTeX/management/commands/data.py に配置することを想定)

from dataclasses import dataclass, field
from typing import List

# Content（個別の関数やコマンド）のデータ構造
@dataclass
class ContentData:
    name: str           # サイドバーに表示される名前 (例: "インライン数式")
    function_slug: str  # URLに使用するユニークな識別子 (例: "inline-math")
    tex_code: str       # エディタに挿入するTeXコード (例: "$$E=mc^2$$")
    guide_content: str  # 詳細ガイドページに表示する説明文 (例: "行中に数式を記述します。")

# Group（カテゴリ）のデータ構造
@dataclass
class GroupData:
    title: str                  # サイドバーのカテゴリ名 (例: "数式環境")
    contents: List[ContentData] = field(default_factory=list) # そのグループに属するContentのリスト

# 投入するデータの本体
SEED_DATA: List[GroupData] = [
    # ----------------------------------------------------------------------
    # 1. 数式環境 (equation, alignなど、数式を記述するための枠組み)
    # ----------------------------------------------------------------------
    GroupData(
        title="数式環境",
        contents=[
            ContentData(
                name="インライン数式",
                function_slug="inline-math",
                tex_code="$ E=mc^2 $",
                guide_content="文章の行中に数式を埋め込むために使用します。バックスラッシュ括弧 `\\( \\)` も同じ機能です。"
            ),
            ContentData(
                name="別行立て数式 (番号なし)",
                function_slug="display-math-no-num",
                tex_code="\\[\n  y = ax^2 + bx + c\n\\]",
                guide_content="中央揃えの独立した行に数式を表示します。数式番号は付きません。二重ドル記号 `$$ $$` も同じ機能です。"
            ),
            ContentData(
                name="equation (番号付き)",
                function_slug="equation-env",
                tex_code="\n\\begin{equation}\n  E = m c^2\n\\end{equation}\n",
                guide_content="数式番号が自動で付与される、一行の独立した数式環境です。シンプルな数式に使います。"
            ),
            ContentData(
                name="align (位置揃え)",
                function_slug="align-env",
                tex_code="\n\\begin{align}\n  (a+b)^2 &= a^2 + 2ab + b^2 \\\\ \n  (a-b)^2 &= a^2 - 2ab + b^2 \n\\end{align}\n",
                guide_content="複数行にわたる数式を特定の記号（通常は `&`）で縦に位置揃えして表示します。各行に数式番号が付きます。"
            ),
            ContentData(
                name="gather (中央揃え)",
                function_slug="gather-env",
                tex_code="\n\\begin{gather}\n  x + y = 5 \\\\ \n  2x - y = 1 \n\\end{gather}\n",
                guide_content="複数の数式を中央揃えで縦に並べる環境です。連立方程式など、位置揃えが不要な場合に便利です。"
            ),
        ]
    ),

    # ----------------------------------------------------------------------
    # 2. 数式記号 (集合・演算子・関係)
    # ----------------------------------------------------------------------
    GroupData(
        title="数式記号",
        contents=[
            ContentData(
                name="部分集合 (包含)",
                function_slug="subset",
                tex_code="$ A \\subset B $",
                guide_content="部分集合を表す記号 `⊂` を出力します。真部分集合は `\\subsetneq` です。"
            ),
            ContentData(
                name="和集合 / 共通部分",
                function_slug="union-cap",
                tex_code="$ A \\cup B \\quad A \\cap B $",
                guide_content="和集合 (`\\cup`) と共通部分 (`\\cap`) を出力します。多数の集合の和/積は `\\bigcup` / `\\bigcap` です。"
            ),
            ContentData(
                name="イコール / ノットイコール",
                function_slug="equal-neq",
                tex_code="$ x = y \\quad x \\neq y $",
                guide_content="等号 (`=`) と等しくない (`\\neq` または `\\ne`) を出力します。"
            ),
            ContentData(
                name="近似記号",
                function_slug="approx-sim",
                tex_code="$ f(x) \\approx x^2 \\quad A \\sim B $",
                guide_content="近似 (`\\approx`) や漸近的に等しい (`\\sim`) などの記号を出力します。"
            ),
            ContentData(
                name="極限",
                function_slug="limit",
                tex_code="$$ \\lim_{x \\to \\infty} \\frac{1}{x} = 0 $$",
                guide_content="極限 (`\\lim`) を出力します。添字は自動で下側に配置されます。"
            ),
        ]
    ),

    # ----------------------------------------------------------------------
    # 3. 図表・構造 (figure, table, \includegraphicsなど)
    # ----------------------------------------------------------------------
    GroupData(
        title="図表・構造",
        contents=[
            ContentData(
                name="図の挿入 (\includegraphics)",
                function_slug="includegraphics",
                tex_code="\n\\usepackage{graphicx}\n\n\\begin{figure}[htbp]\n  \\centering\n  \\includegraphics[width=0.8\\textwidth]{ファイル名.png}\n  \\caption{図のキャプション}\n  \\label{fig:example}\n\\end{figure}\n",
                guide_content="`graphicx` パッケージを使用して図（画像）を挿入します。`figure` 環境は図の自動配置に使われます。"
            ),
            ContentData(
                name="表の作成 (tabular)",
                function_slug="tabular-table",
                tex_code="\n\\begin{table}[htbp]\n  \\caption{表の例}\n  \\centering\n  \\begin{tabular}{|l|c|r|}\n    \\hline\n    左寄せ & 中央寄せ & 右寄せ \\\\ \\hline\n    項目A & 100 & 50 \\\\ \n    項目B & 200 & 75 \\\\ \\hline\n  \\end{tabular}\n\\end{table}\n",
                guide_content="`tabular` 環境を使用して表を作成します。`|lcr|` は罫線とセルの配置（左寄せ/中央/右寄せ）を定義します。"
            ),
            ContentData(
                name="セクション見出し",
                function_slug="section-heading",
                tex_code="\n\\section{はじめに}\n\\subsection{目的}\n",
                guide_content="文書の構造を定義するセクションコマンドです。自動で番号が振られます。"
            ),
            ContentData(
                name="相互参照 (ラベル)",
                function_slug="label-ref",
                tex_code="\n図を参照するには、図\\ref{fig:example}を参照してください。\n\n数式を参照するには、式\\eqref{eq:formula}を参照してください。\n",
                guide_content="`\\label` で定義した箇所を `\\ref` または数式の場合は `\\eqref` を使って参照します。番号が自動で更新されます。"
            ),
        ]
    ),
]
