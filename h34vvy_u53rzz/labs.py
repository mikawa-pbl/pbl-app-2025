from dataclasses import dataclass


@dataclass
class Lab:
    id: str
    name: str


LABORATORIES = [
    Lab("lab_nakamura", "中村研究室"),
    Lab("lab_sato", "佐藤研究室"),
    Lab("lab_suzuki", "鈴木研究室"),
    Lab("lab_takahashi", "高橋研究室"),
    Lab("lab_tanaka", "田中研究室"),
    # 追加してください
]
