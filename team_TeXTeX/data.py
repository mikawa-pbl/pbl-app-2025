# myapp/management/commands/data.py
# (アプリ名が team_TeXTeX の場合、team_TeXTeX/management/commands/data.py に配置)

from dataclasses import dataclass, field
from typing import List

@dataclass
class ContentData:
    name: str
    function_slug: str
    tex_code: str
    guide_content: str
    slug_id: int
    guide_id: int

@dataclass
class GroupData:
    title: str
    group_id: int
    contents: List[ContentData] = field(default_factory=list)

_slug_counter = 1
_guide_counter = 1

def create_content(name, slug, code, guide):
    global _slug_counter, _guide_counter
    c = ContentData(name, slug, code, guide, _slug_counter, _guide_counter)
    _slug_counter += 1
    _guide_counter += 1
    return c

# 1. ギリシャ文字 (Greek Letters)
group_greek = GroupData(title="ギリシャ文字", group_id=1)
group_greek.contents = [
    # 小文字
    create_content("アルファ (α)", "alpha", "\\alpha", "ギリシャ文字 α"),
    create_content("ベータ (β)", "beta", "\\beta", "ギリシャ文字 β"),
    create_content("ガンマ (γ)", "gamma", "\\gamma", "ギリシャ文字 γ"),
    create_content("デルタ (δ)", "delta", "\\delta", "ギリシャ文字 δ"),
    create_content("イプシロン (ε)", "epsilon", "\\epsilon", "ギリシャ文字 ε"),
    create_content("イプシロン変形 (ε)", "varepsilon", "\\varepsilon", "ギリシャ文字 ε (変形)"),
    create_content("ゼータ (ζ)", "zeta", "\\zeta", "ギリシャ文字 ζ"),
    create_content("イータ (η)", "eta", "\\eta", "ギリシャ文字 η"),
    create_content("シータ (θ)", "theta", "\\theta", "ギリシャ文字 θ"),
    create_content("シータ変形 (ϑ)", "vartheta", "\\vartheta", "ギリシャ文字 θ (変形)"),
    create_content("イオタ (ι)", "iota", "\\iota", "ギリシャ文字 ι"),
    create_content("カッパ (κ)", "kappa", "\\kappa", "ギリシャ文字 κ"),
    create_content("ラムダ (λ)", "lambda", "\\lambda", "ギリシャ文字 λ"),
    create_content("ミュー (μ)", "mu", "\\mu", "ギリシャ文字 μ"),
    create_content("ニュー (ν)", "nu", "\\nu", "ギリシャ文字 ν"),
    create_content("クシー (ξ)", "xi", "\\xi", "ギリシャ文字 ξ"),
    create_content("パイ (π)", "pi", "\\pi", "ギリシャ文字 π"),
    create_content("パイ変形 (ϖ)", "varpi", "\\varpi", "ギリシャ文字 π (変形)"),
    create_content("ロー (ρ)", "rho", "\\rho", "ギリシャ文字 ρ"),
    create_content("ロー変形 (ϱ)", "varrho", "\\varrho", "ギリシャ文字 ρ (変形)"),
    create_content("シグマ (σ)", "sigma", "\\sigma", "ギリシャ文字 σ"),
    create_content("シグマ変形 (ς)", "varsigma", "\\varsigma", "ギリシャ文字 ς (語末形)"),
    create_content("タウ (τ)", "tau", "\\tau", "ギリシャ文字 τ"),
    create_content("ウプシロン (υ)", "upsilon", "\\upsilon", "ギリシャ文字 υ"),
    create_content("ファイ (φ)", "phi", "\\phi", "ギリシャ文字 φ"),
    create_content("ファイ変形 (φ)", "varphi", "\\varphi", "ギリシャ文字 φ (変形)"),
    create_content("カイ (χ)", "chi", "\\chi", "ギリシャ文字 χ"),
    create_content("プサイ (ψ)", "psi", "\\psi", "ギリシャ文字 ψ"),
    create_content("オメガ (ω)", "omega", "\\omega", "ギリシャ文字 ω"),
    # 大文字
    create_content("ガンマ (Γ)", "Gamma", "\\Gamma", "ギリシャ文字 Γ"),
    create_content("デルタ (Δ)", "Delta", "\\Delta", "ギリシャ文字 Δ"),
    create_content("シータ (Θ)", "Theta", "\\Theta", "ギリシャ文字 Θ"),
    create_content("ラムダ (Λ)", "Lambda", "\\Lambda", "ギリシャ文字 Λ"),
    create_content("クシー (Ξ)", "Xi", "\\Xi", "ギリシャ文字 Ξ"),
    create_content("パイ (Π)", "Pi", "\\Pi", "ギリシャ文字 Π"),
    create_content("シグマ (Σ)", "Sigma", "\\Sigma", "ギリシャ文字 Σ"),
    create_content("ウプシロン (Υ)", "Upsilon", "\\Upsilon", "ギリシャ文字 Υ"),
    create_content("ファイ (Φ)", "Phi", "\\Phi", "ギリシャ文字 Φ"),
    create_content("プサイ (Ψ)", "Psi", "\\Psi", "ギリシャ文字 Ψ"),
    create_content("オメガ (Ω)", "Omega", "\\Omega", "ギリシャ文字 Ω"),
]

# 2. 演算子 (Operators)
group_operators = GroupData(title="演算子", group_id=2)
group_operators.contents = [
    create_content("プラス (+)", "plus", "+", "加算"),
    create_content("マイナス (-)", "minus", "-", "減算"),
    create_content("掛け算 (times)", "times", "\\times", "乗算記号 ×"),
    create_content("割り算 (div)", "div", "\\div", "除算記号 ÷"),
    create_content("ドット積 (cdot)", "cdot", "\\cdot", "ドット積・積の省略"),
    create_content("プラスマイナス (pm)", "pm", "\\pm", "プラスマイナス ±"),
    create_content("マイナスプラス (mp)", "mp", "\\mp", "マイナスプラス ∓"),
    create_content("分数 (frac)", "frac", "\\frac{a}{b}", "分数"),
    create_content("平方根 (sqrt)", "sqrt", "\\sqrt{x}", "平方根"),
    create_content("n乗根 (sqrt-n)", "sqrt-n", "\\sqrt[n]{x}", "n乗根"),
    create_content("総和 (sum)", "sum", "\\sum_{i=0}^{n}", "シグマ総和"),
    create_content("総乗 (prod)", "prod", "\\prod_{i=0}^{n}", "パイ総乗"),
    create_content("和集合 (cup)", "cup", "\\cup", "カップ U"),
    create_content("共通部分 (cap)", "cap", "\\cap", "キャップ ∩"),
    create_content("積分 (int)", "int", "\\int_{a}^{b}", "積分"),
    create_content("周回積分 (oint)", "oint", "\\oint", "周回積分"),
    create_content("偏微分 (partial)", "partial", "\\partial", "偏微分記号 ∂"),
    create_content("ナブラ (nabla)", "nabla", "\\nabla", "ナブラ ∇"),
    create_content("無限大 (infty)", "infty", "\\infty", "無限大 ∞"),
    create_content("合成 (circ)", "circ", "\\circ", "合成関数の丸"),
    create_content("スター (star)", "star", "\\star", "スター記号"),
    create_content("アスタリスク (ast)", "ast", "\\ast", "アスタリスク"),
]

# 3. 関係子 (Relations)
group_relations = GroupData(title="関係子", group_id=3)
group_relations.contents = [
    create_content("等号 (=)", "equal", "=", "等しい"),
    create_content("不同 (neq)", "neq", "\\neq", "等しくない"),
    create_content("小なり (<)", "lt", "<", "小なり"),
    create_content("大なり (>)", "gt", ">", "大なり"),
    create_content("以下 (leq)", "leq", "\\leq", "以下"),
    create_content("以上 (geq)", "geq", "\\geq", "以上"),
    create_content("近似 (approx)", "approx", "\\approx", "近似的に等しい"),
    create_content("合同 (equiv)", "equiv", "\\equiv", "合同"),
    create_content("シム (sim)", "sim", "\\sim", "シム記号 ~"),
    create_content("相似 (simeq)", "simeq", "\\simeq", "相似"),
    create_content("比例 (propto)", "propto", "\\propto", "比例"),
    create_content("中黒 (mid)", "mid", "\\mid", "縦棒（条件など）"),
    create_content("平行 (parallel)", "parallel", "\\parallel", "平行"),
    create_content("垂直 (perp)", "perp", "\\perp", "垂直"),
]

# 4. 論理・集合 (Logic & Sets)
group_logic = GroupData(title="論理・集合", group_id=4)
group_logic.contents = [
    create_content("すべての (forall)", "forall", "\\forall", "全称記号"),
    create_content("存在する (exists)", "exists", "\\exists", "存在記号"),
    create_content("空集合 (emptyset)", "emptyset", "\\emptyset", "空集合"),
    create_content("属する (in)", "in", "\\in", "要素として属する"),
    create_content("属さない (notin)", "notin", "\\notin", "要素として属さない"),
    create_content("含む (ni)", "ni", "\\ni", "要素として含む"),
    create_content("部分集合 (subset)", "subset", "\\subset", "真部分集合"),
    create_content("部分集合 (subseteq)", "subseteq", "\\subseteq", "部分集合（等号含む）"),
    create_content("上位集合 (supset)", "supset", "\\supset", "真上位集合"),
    create_content("上位集合 (supseteq)", "supseteq", "\\supseteq", "上位集合（等号含む）"),
    create_content("論理積 (land)", "land", "\\land", "かつ (AND)"),
    create_content("論理和 (lor)", "lor", "\\lor", "または (OR)"),
    create_content("否定 (lnot)", "lnot", "\\lnot", "否定 (NOT)"),
]

# 5. 矢印 (Arrows)
group_arrows = GroupData(title="矢印", group_id=5)
group_arrows.contents = [
    create_content("右矢印 (rightarrow)", "rightarrow", "\\rightarrow", "右矢印"),
    create_content("左矢印 (leftarrow)", "leftarrow", "\\leftarrow", "左矢印"),
    create_content("左右矢印 (leftrightarrow)", "leftrightarrow", "\\leftrightarrow", "左右矢印"),
    create_content("長い右矢印 (longrightarrow)", "longrightarrow", "\\longrightarrow", "長い右矢印"),
    create_content("二重右矢印 (Rightarrow)", "Rightarrow", "\\Rightarrow", "ならば"),
    create_content("二重左矢印 (Leftarrow)", "Leftarrow", "\\Leftarrow", "逆ならば"),
    create_content("同値 (Leftrightarrow)", "Leftrightarrow", "\\Leftrightarrow", "同値"),
    create_content("長い同値 (Longleftrightarrow)", "Longleftrightarrow", "\\Longleftrightarrow", "長い同値"),
    create_content("写像 (mapsto)", "mapsto", "\\mapsto", "写像"),
    create_content("長い写像 (longmapsto)", "longmapsto", "\\longmapsto", "長い写像"),
    create_content("上矢印 (uparrow)", "uparrow", "\\uparrow", "上矢印"),
    create_content("下矢印 (downarrow)", "downarrow", "\\downarrow", "下矢印"),
]

# 6. 関数 (Functions)
group_functions = GroupData(title="関数", group_id=6)
group_functions.contents = [
    create_content("sin", "sin", "\\sin", "正弦"),
    create_content("cos", "cos", "\\cos", "余弦"),
    create_content("tan", "tan", "\\tan", "正接"),
    create_content("arcsin", "arcsin", "\\arcsin", "逆正弦"),
    create_content("arccos", "arccos", "\\arccos", "逆余弦"),
    create_content("arctan", "arctan", "\\arctan", "逆正接"),
    create_content("sinh", "sinh", "\\sinh", "双曲線正弦"),
    create_content("cosh", "cosh", "\\cosh", "双曲線余弦"),
    create_content("tanh", "tanh", "\\tanh", "双曲線正接"),
    create_content("log", "log", "\\log", "対数"),
    create_content("ln", "ln", "\\ln", "自然対数"),
    create_content("exp", "exp", "\\exp", "指数"),
    create_content("lim", "lim", "\\lim", "極限"),
    create_content("max", "max", "\\max", "最大"),
    create_content("min", "min", "\\min", "最小"),
    create_content("sup", "sup", "\\sup", "上限"),
    create_content("inf", "inf", "\\inf", "下限"),
    create_content("det", "det", "\\det", "行列式"),
    create_content("deg", "deg", "\\deg", "次数"),
]

# 7. 括弧・区切り (Delimiters)
group_delims = GroupData(title="括弧・区切り", group_id=7)
group_delims.contents = [
    create_content("丸括弧 ()", "parens", "( )", "丸括弧"),
    create_content("角括弧 []", "brackets", "[ ]", "角括弧"),
    create_content("波括弧 {}", "braces", "\\{ \\}", "波括弧（エスケープが必要）"),
    create_content("山括弧 <>", "angle", "\\langle \\rangle", "内積や生成系"),
    create_content("絶対値 | |", "abs", "| x |", "絶対値"),
    create_content("ノルム || ||", "norm", "\\| x \\|", "ノルム"),
    create_content("自動サイズ調整", "left-right", "\\left( \\frac{a}{b} \\right)", "内容に合わせてサイズ調整"),
]

# 8. アクセント (Accents)
group_accents = GroupData(title="アクセント", group_id=8)
group_accents.contents = [
    create_content("ハット (hat)", "hat", "\\hat{a}", "文字上のハット"),
    create_content("バー (bar)", "bar", "\\bar{a}", "文字上のバー"),
    create_content("ドット (dot)", "dot", "\\dot{a}", "時間微分など"),
    create_content("二重ドット (ddot)", "ddot", "\\ddot{a}", "二階微分など"),
    create_content("チルダ (tilde)", "tilde", "\\tilde{a}", "チルダ"),
    create_content("ベクトル (vec)", "vec", "\\vec{a}", "ベクトル"),
    create_content("上線 (overline)", "overline", "\\overline{AB}", "上線（線分など）"),
    create_content("下線 (underline)", "underline", "\\underline{text}", "下線"),
]

# 9. 空白・スペース (Spacing)
group_spacing = GroupData(title="空白・スペース", group_id=9)
group_spacing.contents = [
    create_content("クワッド (quad)", "quad", "\\quad", "全角スペース相当"),
    create_content("ダブルクワッド (qquad)", "qquad", "\\qquad", "2倍の全角スペース"),
    create_content("小スペース (,)", "thinspace", "\\,", "小さなスペース"),
    create_content("中スペース (:)", "medspace", "\\:", "中くらいのスペース"),
    create_content("大スペース (;)", "thickspace", "\\;", "大きなスペース"),
    create_content("負のスペース (!)", "negspace", "\\!", "間隔を詰める"),
]

# 10. フォント (Fonts)
group_fonts = GroupData(title="フォント", group_id=10)
group_fonts.contents = [
    create_content("黒板太字 (mathbb)", "mathbb", "\\mathbb{R}", "実数集合など"),
    create_content("カリグラフィ (mathcal)", "mathcal", "\\mathcal{A}", "筆記体"),
    create_content("フラクトゥール (mathfrak)", "mathfrak", "\\mathfrak{g}", "ドイツ文字"),
    create_content("スクリプト (mathscr)", "mathscr", "\\mathscr{L}", "花文字 (要パッケージの場合あり)"),
    create_content("ローマン (mathrm)", "mathrm", "\\mathrm{text}", "直立体"),
    create_content("ボールド (mathbf)", "mathbf", "\\mathbf{v}", "太字"),
    create_content("サンセリフ (mathsf)", "mathsf", "\\mathsf{A}", "サンセリフ体"),
    create_content("タイプライタ (mathtt)", "mathtt", "\\mathtt{code}", "等幅フォント"),
]

# 11. 数式環境 (Environments)
group_envs = GroupData(title="数式環境", group_id=11)
group_envs.contents = [
    create_content("インライン", "inline", "$ ... $", "文中数式"),
    create_content("別行立て", "display", "\\[ ... \\]", "独立行数式"),
    create_content("equation", "equation", "\\begin{equation}\n  ...\n\\end{equation}", "番号付き数式"),
    create_content("align", "align", "\\begin{align}\n  x &= y \\\\\n    &= z\n\\end{align}", "位置揃え"),
    create_content("cases", "cases", "\\begin{cases}\n  1 & (x>0) \\\\\n  0 & (x \\le 0)\n\\end{cases}", "場合分け"),
    create_content("matrix", "matrix", "\\begin{matrix} a & b \\\\ c & d \\end{matrix}", "括弧なし行列"),
    create_content("pmatrix", "pmatrix", "\\begin{pmatrix} a & b \\\\ c & d \\end{pmatrix}", "丸括弧行列"),
    create_content("bmatrix", "bmatrix", "\\begin{bmatrix} a & b \\\\ c & d \\end{bmatrix}", "角括弧行列"),
    create_content("vmatrix", "vmatrix", "\\begin{vmatrix} a & b \\\\ c & d \\end{vmatrix}", "行列式 (| |)"),
]

# 12. 文書構造 (Structure)
group_structure = GroupData(title="文書構造", group_id=12)
group_structure.contents = [
    create_content("セクション", "section", "\\section{title}", "章"),
    create_content("サブセクション", "subsection", "\\subsection{title}", "節"),
    create_content("パラグラフ", "paragraph", "\\paragraph{title}", "段落"),
    create_content("強調 (emph)", "emph", "\\emph{text}", "強調（イタリック等）"),
    create_content("太字 (textbf)", "textbf", "\\textbf{text}", "本文太字"),
    create_content("斜体 (textit)", "textit", "\\textit{text}", "本文斜体"),
    create_content("参照 (ref)", "ref", "\\ref{key}", "図表番号等の参照"),
    create_content("数式参照 (eqref)", "eqref", "\\eqref{key}", "数式番号の参照"),
    create_content("引用 (cite)", "cite", "\\cite{key}", "文献引用"),
    create_content("ラベル (label)", "label", "\\label{key}", "ラベル定義"),
    create_content("脚注 (footnote)", "footnote", "\\footnote{text}", "脚注"),
    create_content("URL (url)", "url", "\\url{http://...}", "URLリンク"),
    create_content("画像 (includegraphics)", "includegraphics", "\\includegraphics[width=5cm]{file}", "画像挿入"),
]

SEED_DATA: List[GroupData] = [
    group_greek,
    group_operators,
    group_relations,
    group_logic,
    group_arrows,
    group_functions,
    group_delims,
    group_accents,
    group_spacing,
    group_fonts,
    group_envs,
    group_structure,
]
