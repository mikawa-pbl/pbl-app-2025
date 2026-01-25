from django.shortcuts import render
from django.db.models import Avg, F, Count
from typing import Optional
import datetime
import calendar

from .models import Member, MenuRating
from .menu_pdf import get_today_menu, get_this_week_menu, build_date_menu_dict


def index(request):
    return render(request, 'teams/team_kitajaki/index.html')


def members(request):
    qs = Member.objects.using('team_kitajaki').all()
    return render(request, 'teams/team_kitajaki/members.html', {'members': qs})


def today_menu(request):
    error_message = None
    today_date = None
    weekday_char = None
    menu_lines = []
    week_menus = []

    # 平均スコア表示用
    average_scores = None

    # ★ 今日メニュー用の入賞バッジ（総合/味/量 複数可）
    today_rank_badges = []

    # コメント（例外が起きても参照できるように先に用意）
    comments = []

    try:
        # --- 今日のメニュー取得 ---
        info = get_today_menu()
        today_date = info["date"]
        weekday_char = info["weekday_char"]
        menu_lines = info["menu_lines"]

        # DB検索キー（メニュー名）
        today_menu_text = menu_lines[0] if menu_lines else None

        # --- コメント取得 ---
        if today_menu_text:
            comments = list(
                MenuRating.objects.filter(menu_name=today_menu_text)
                .exclude(comment="")
                .order_by("-created_at")[:50]
            )

        # --- 今日の平均スコア ---
        if today_menu_text:
            rating_stats = MenuRating.objects.filter(
                menu_name=today_menu_text
            ).aggregate(
                avg_taste=Avg("taste_score"),
                avg_volume=Avg("volume_score"),
            )

            if rating_stats["avg_taste"] is not None:
                avg_taste = float(rating_stats["avg_taste"])
                avg_volume = float(rating_stats["avg_volume"])
                avg_overall = (avg_taste + avg_volume) / 2.0

                average_scores = {
                    "avg_taste": round(avg_taste, 1),
                    "avg_volume": round(avg_volume, 1),
                    "avg_overall": round(avg_overall, 1),
                    "count": MenuRating.objects.filter(menu_name=today_menu_text).count(),
                }


        # --- 今週のメニュー一覧 ---
        week_menus = get_this_week_menu()

        # --- ランキングTop5（総合/味/量）を辞書化 ---
        rank_maps = _build_rank_maps(top_n=5)

        # 今日のメニューのバッジ
        today_rank_badges = _badges_for_menu(today_menu_text, rank_maps)

        # 今週の表（残しておく場合用）：各メニューにもバッジ情報を付与
        for item in week_menus:
            menu_name = item.get("menu")
            item["rank_badges"] = _badges_for_menu(menu_name, rank_maps)
            item["is_ranked"] = bool(item["rank_badges"])

        # =========================
        # ここから：月カレンダー用
        # =========================
        ym = request.GET.get("ym")
        base = today_date or datetime.date.today()

        if ym:
            try:
                y, m = map(int, ym.split("-"))
                cal_year, cal_month = y, m
            except Exception:
                cal_year, cal_month = base.year, base.month
        else:
            cal_year, cal_month = base.year, base.month

        def shift_month(y: int, m: int, delta: int):
            m2 = m + delta
            y2 = y + (m2 - 1) // 12
            m2 = (m2 - 1) % 12 + 1
            return y2, m2

        pycal = calendar.Calendar(firstweekday=0)  # 月曜始まり
        date_menu = build_date_menu_dict(cal_year)

        cal_weeks = []
        for week in pycal.monthdayscalendar(cal_year, cal_month):
            row = []
            for day in week:
                if day == 0:
                    row.append({"in_month": False})
                    continue

                d = datetime.date(cal_year, cal_month, day)
                menu = date_menu.get(d)
                badges = _badges_for_menu(menu, rank_maps) if menu else []

                row.append({
                    "in_month": True,
                    "date": d,
                    "day": day,
                    "menu": menu,
                    "badges": badges,
                    "is_today": (d == base),
                })
            cal_weeks.append(row)

        prev_y, prev_m = shift_month(cal_year, cal_month, -1)
        next_y, next_m = shift_month(cal_year, cal_month, +1)

    except Exception as e:
        error_message = f"メニュー取得中にエラーが発生しました: {e}"
        # 月カレンダー用の変数も最低限用意（テンプレで落ちないように）
        cal_year = (today_date or datetime.date.today()).year
        cal_month = (today_date or datetime.date.today()).month
        cal_weeks = []
        prev_ym = ""
        next_ym = ""

    context = {
        "today_date": today_date,
        "weekday_char": weekday_char,
        "menu_lines": menu_lines,
        "week_menus": week_menus,
        "error_message": error_message,
        "average_scores": average_scores,
        "comments": comments,

        # ★ 今日の王冠＋順位
        "today_rank_badges": today_rank_badges,

        # ★ 月カレンダー
        "cal_year": cal_year,
        "cal_month": cal_month,
        "cal_weeks": cal_weeks,
        "prev_ym": f"{prev_y:04d}-{prev_m:02d}" if 'prev_y' in locals() else "",
        "next_ym": f"{next_y:04d}-{next_m:02d}" if 'next_y' in locals() else "",
        "week_labels": ["月", "火", "水", "木", "金", "土", "日"],
    }
    return render(request, "teams/team_kitajaki/today_menu.html", context)


def rate_menu(request):
    error_message = None
    today_menu_text = "メニュー不明"
    today_date = None

    # 今日のメニュー情報を取得
    try:
        info = get_today_menu()
        today_date = info["date"]
        # ★ メニュー名を取得（DB保存キーとして使用）
        today_menu_text = info["menu_lines"][0] if info["menu_lines"] else "メニュー不明"
    except Exception as e:
        error_message = f"メニュー取得中にエラーが発生しました: {e}"

    # POSTリクエスト（フォーム送信）の処理
    if request.method == 'POST':
        taste_rating = request.POST.get('taste_rating')
        volume_rating = request.POST.get('volume_rating')
        comment = request.POST.get('comment', '').strip()

        # メニューがあり、評価値が取得できたらDBに保存
        if taste_rating and volume_rating and today_menu_text != "メニュー不明":
            try:
                # ★ 評価データをデータベースに保存
                MenuRating.objects.create(
                    menu_name=today_menu_text,
                    taste_score=int(taste_rating),
                    volume_score=int(volume_rating),
                    comment=comment,
                )

                success_message = "評価を送信しました！ありがとうございます😊"
            except Exception as e:
                error_message = f"評価の保存中にエラーが発生しました: {e}"
                success_message = None
        else:
            error_message = "評価項目が不足しているか、今日のメニュー情報が取得できませんでした。"
            success_message = None

        # 処理結果を context に追加して画面に表示
        context = {
            "today_menu": today_menu_text,
            "today_date": today_date,
            "error_message": error_message,
            "success_message": success_message,
            "submitted_taste": taste_rating,
            "submitted_volume": volume_rating,
            "submitted_comment": comment,
        }
        return render(request, "teams/team_kitajaki/rate_menu.html", context)

    # GETリクエスト（初期表示）の処理
    context = {
        "today_menu": today_menu_text,
        "today_date": today_date,
        "error_message": error_message,
    }
    return render(request, "teams/team_kitajaki/rate_menu.html", context)


def _build_rank_maps(top_n: int = 5):
    """
    各メニューのランキング情報（総合/味/量）を辞書化して返す
    """
    qs = MenuRating.objects.values("menu_name").annotate(
        avg_taste=Avg("taste_score"),
        avg_volume=Avg("volume_score"),
    ).annotate(
        overall_score=(F("avg_taste") + F("avg_volume")) / 2.0
    )

    ranking_overall = list(qs.order_by("-overall_score")[:top_n])
    ranking_taste   = list(qs.order_by("-avg_taste")[:top_n])
    ranking_volume  = list(qs.order_by("-avg_volume")[:top_n])

    def to_map(rows, score_key: str):
        m = {}
        for i, row in enumerate(rows, start=1):
            name = row["menu_name"]
            score = row.get(score_key)
            m[name] = {"rank": i, "score": float(score) if score is not None else None}
        return m

    return {
        "overall": to_map(ranking_overall, "overall_score"),
        "taste":  to_map(ranking_taste,   "avg_taste"),
        "volume": to_map(ranking_volume,  "avg_volume"),
    }


def _badges_for_menu(menu_name: Optional[str], rank_maps: dict) -> list[dict]:
    """
    1つのメニューに対して、入賞している部門のバッジ情報を返す（複数可）
    表示順は 総合→味→量
    """
    if not menu_name:
        return []

    badges = []
    meta = [
        ("overall", "総合", "👑"),
        ("taste",   "味",   "👑"),
        ("volume",  "量",   "👑"),
    ]

    for key, label, icon in meta:
        info = rank_maps.get(key, {}).get(menu_name)
        if info:
            badges.append({
                "key": key,
                "label": label,
                "rank": info["rank"],
                "icon": icon,
            })

    return badges


def menu_ranking(request):
    """
    メニューの評価ランキングを表示するビュー
    """
    qs = MenuRating.objects.values('menu_name').annotate(
        avg_taste=Avg('taste_score'),
        avg_volume=Avg('volume_score'),
        rating_count=Count('id'),
    ).annotate(
        overall_score=(F('avg_taste') + F('avg_volume')) / 2.0
    )

    ranking_overall = qs.order_by('-overall_score')[:5]
    ranking_taste = qs.order_by('-avg_taste')[:5]
    ranking_volume = qs.order_by('-avg_volume')[:5]

    context = {
        'ranking_overall': ranking_overall,
        'ranking_taste': ranking_taste,
        'ranking_volume': ranking_volume,
    }
    return render(request, 'teams/team_kitajaki/menu_ranking.html', context)
