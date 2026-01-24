import io
import datetime
import re

import pdfplumber
import requests

from typing import Optional

PDF_URL = "https://www.tut.ac.jp/student/studentlife/docs/kissa_menu.pdf"

DAY_CHARS = "月火水木金土日"


def _fetch_pdf_bytes() -> bytes:
    # サーバ側の設定変更に備えて User-Agent を付ける（今は必須ではないが安定）
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/pdf,*/*;q=0.8",
    }
    resp = requests.get(PDF_URL, headers=headers, timeout=20)
    resp.raise_for_status()
    return resp.content


def _load_tables_all_pages() -> list[list[list[Optional[str]]]]:
    """
    PDFの全ページからテーブルを抽出して返す。
    戻り値: [table, table, ...] （tableは list[row]、rowは list[cell]）
    """
    pdf_bytes = _fetch_pdf_bytes()
    tables: list[list[list[Optional[str]]]] = []

    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                tables.append(table)

    return tables


def _resolve_year(base_year: int, base_month: int, month_in_pdf: int) -> int:
    """
    年末年始またぎ補正：
    例）base_month=1（1月）なのに month_in_pdf=12（12月）が出たら base_year-1 とみなす。
    """
    if base_month == 1 and month_in_pdf == 12:
        return base_year - 1
    if base_month == 12 and month_in_pdf == 1:
        return base_year + 1
    return base_year


def build_date_menu_dict(year: Optional[int] = None) -> dict[datetime.date, str]:
    """
    全ページのテーブルから「日付 → メニュー文字列」の辞書を作る。
    """
    today = datetime.date.today()
    if year is None:
        year = today.year

    tables = _load_tables_all_pages()
    if not tables:
        return {}

    date_to_menu: dict[datetime.date, str] = {}

    # ページ（table）ごとに独立して走査する（ページまたぎでペアが崩れない）
    for table in tables:
        # 行を順番に見て、「日付行」と「次のメニュー行」をペアにする
        for row_idx in range(len(table) - 1):
            header_row = table[row_idx]
            menu_row = table[row_idx + 1]

            if not header_row or not menu_row:
                continue

            # header_row の中に日付セルが1個も無ければスキップ（ノイズ行対策）
            if not any(cell and re.search(r"(\d{1,2})月(\d{1,2})日", cell) for cell in header_row):
                continue

            for col_idx, cell in enumerate(header_row):
                if not cell:
                    continue

                m = re.search(r"(\d{1,2})月(\d{1,2})日", cell)
                if not m:
                    continue

                month = int(m.group(1))
                day = int(m.group(2))

                use_year = _resolve_year(year, today.month, month)

                try:
                    d = datetime.date(use_year, month, day)
                except ValueError:
                    continue

                menu_cell = menu_row[col_idx] if col_idx < len(menu_row) else None
                if not menu_cell:
                    continue

                menu_text = " ".join(menu_cell.split())
                date_to_menu[d] = menu_text

    return date_to_menu


def get_today_menu() -> dict:
    """
    今日のメニュー情報を返す。
    """
    today = datetime.date.today()
    weekday_char = DAY_CHARS[today.weekday()]

    date_menu = build_date_menu_dict(today.year)
    menu = date_menu.get(today)

    return {
        "date": today,
        "weekday_char": weekday_char,
        "menu_lines": [menu] if menu else [],
    }


def get_this_week_menu() -> list[dict]:
    """
    今週（月〜金）のメニュー一覧を返す。
    """
    today = datetime.date.today()
    monday = today - datetime.timedelta(days=today.weekday())

    date_menu = build_date_menu_dict(today.year)

    week_list: list[dict] = []
    for i in range(5):
        d = monday + datetime.timedelta(days=i)
        week_list.append({
            "date": d,
            "weekday_char": DAY_CHARS[d.weekday()],
            "menu": date_menu.get(d),
        })

    return week_list
