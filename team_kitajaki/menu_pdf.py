import io
import datetime
import re

import pdfplumber
import requests

PDF_URL = "https://www.tut.ac.jp/student/studentlife/docs/kissa_menu.pdf"

DAY_CHARS = "月火水木金土日"


def _load_table():
    """
    PDFの1ページ目からテーブルを抽出して返す。
    戻り値: list[list[str | None]] | None
    """
    resp = requests.get(PDF_URL)
    resp.raise_for_status()

    with pdfplumber.open(io.BytesIO(resp.content)) as pdf:
        page = pdf.pages[0]
        table = page.extract_table()
    return table


def build_date_menu_dict(year: int | None = None) -> dict[datetime.date, str]:
    """
    テーブルから「日付 → メニュー文字列」の辞書を作る。
    """
    if year is None:
        year = datetime.date.today().year

    table = _load_table()
    if not table:
        return {}

    date_to_menu: dict[datetime.date, str] = {}

    # 行を順番に見て、「日付が並んでいる行」と「その次のメニュー行」をペアにする
    for row_idx in range(len(table) - 1):
        header_row = table[row_idx]
        menu_row = table[row_idx + 1]

        if not header_row or not menu_row:
            continue

        for col_idx, cell in enumerate(header_row):
            if not cell:
                continue

            # "11月17日（月）" などの日付を拾う
            m = re.search(r"(\d{1,2})月(\d{1,2})日", cell)
            if not m:
                continue

            month = int(m.group(1))
            day = int(m.group(2))
            try:
                date = datetime.date(year, month, day)
            except ValueError:
                continue

            # 同じ列のメニューセルを取る
            menu_cell = menu_row[col_idx] if col_idx < len(menu_row) else None
            if not menu_cell:
                continue

            # 余計な改行・スペースを整理
            menu_text = " ".join(menu_cell.split())
            date_to_menu[date] = menu_text

    return date_to_menu


def get_today_menu() -> dict:
    """
    今日のメニュー情報を返す。

    戻り値:
      {
        "date": datetime.date,
        "weekday_char": "月" など,
        "menu_lines": ["メニュー文字列"] or []
      }
    """
    today = datetime.date.today()
    weekday_char = DAY_CHARS[today.weekday()]

    date_menu = build_date_menu_dict(today.year)
    menu = date_menu.get(today)

    if menu:
        menu_lines = [menu]  # とりあえず1行だけ
    else:
        menu_lines = []

    return {
        "date": today,
        "weekday_char": weekday_char,
        "menu_lines": menu_lines,
    }

def get_this_week_menu() -> list[dict]:
    """
    今週（月〜金）のメニュー一覧を返す。

    返り値の例:
    [
      {"date": date(2025, 11, 17), "weekday_char": "月", "menu": "厚旨トンカツ"},
      {"date": date(2025, 11, 18), "weekday_char": "火", "menu": "○○"},
      ...
    ]
    """
    today = datetime.date.today()
    year = today.year

    # 月曜日の日付を求める
    monday = today - datetime.timedelta(days=today.weekday())

    date_menu = build_date_menu_dict(year)

    week_list: list[dict] = []
    # 月〜金の5日分
    for i in range(5):
        d = monday + datetime.timedelta(days=i)
        menu = date_menu.get(d)
        weekday_char = DAY_CHARS[d.weekday()]

        week_list.append({
            "date": d,
            "weekday_char": weekday_char,
            "menu": menu,  # 無い日は None のまま
        })

    return week_list