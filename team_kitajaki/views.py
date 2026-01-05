from django.shortcuts import render, redirect
from django.db.models import Avg, F, Count
from typing import Optional



from .models import Member, MenuRating # ★ MenuRating をインポート

from .menu_pdf import get_today_menu, get_this_week_menu

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

    # ★ 追加：今日メニュー用の入賞バッジ（総合/味/量 複数可）
    today_rank_badges = []

    try:
        # --- 今日のメニュー取得 ---
        info = get_today_menu()
        today_date = info["date"]
        weekday_char = info["weekday_char"]
        menu_lines = info["menu_lines"]

        # DB検索キー（メニュー名）
        today_menu_text = menu_lines[0] if menu_lines else None

        comments = []
        if today_menu_text:
            comments = list(
                MenuRating.objects.filter(menu_name=today_menu_text)
                .exclude(comment="")
                .order_by("-created_at")[:50]   # ★多すぎる時用に最大50件
            )


        # --- 今日の平均スコア（既存機能） ---
        if today_menu_text:
            rating_stats = MenuRating.objects.filter(
                menu_name=today_menu_text
            ).aggregate(
                avg_taste=Avg("taste_score"),
                avg_volume=Avg("volume_score"),
            )

            if rating_stats["avg_taste"] is not None:
                average_scores = {
                    "avg_taste": round(rating_stats["avg_taste"], 1),
                    "avg_volume": round(rating_stats["avg_volume"], 1),
                    "count": MenuRating.objects.filter(menu_name=today_menu_text).count(),
                }

        # --- 今週のメニュー一覧 ---
        week_menus = get_this_week_menu()

        # --- ★ 追加：ランキングTop5（総合/味/量）を作る ---
        qs = MenuRating.objects.values("menu_name").annotate(
            avg_taste=Avg("taste_score"),
            avg_volume=Avg("volume_score"),
        ).annotate(
            overall_score=(F("avg_taste") + F("avg_volume")) / 2.0
        )

        ranking_overall = list(qs.order_by("-overall_score")[:5])
        ranking_taste = list(qs.order_by("-avg_taste")[:5])
        ranking_volume = list(qs.order_by("-avg_volume")[:5])

        # menu_name -> rank の辞書（スコアも必要なら入れられる）
        overall_map = {row["menu_name"]: i for i, row in enumerate(ranking_overall, start=1)}
        taste_map   = {row["menu_name"]: i for i, row in enumerate(ranking_taste, start=1)}
        volume_map  = {row["menu_name"]: i for i, row in enumerate(ranking_volume, start=1)}

        def badges_for(menu_name: Optional[str]) -> list[dict]:
            """
            メニューがTop5に入っている部門のバッジ一覧を返す（複数可）
            表示順：総合→味→量
            例: [{"key":"overall","label":"総合","rank":1,"icon":"👑"}, ...]
            """
            if not menu_name:
                return []

            badges = []
            if menu_name in overall_map:
                badges.append({"key": "overall", "label": "総合", "rank": overall_map[menu_name], "icon": "👑"})
            if menu_name in taste_map:
                badges.append({"key": "taste", "label": "味", "rank": taste_map[menu_name], "icon": "👑"})
            if menu_name in volume_map:
                badges.append({"key": "volume", "label": "量", "rank": volume_map[menu_name], "icon": "👑"})
            return badges

        # 今日のメニューのバッジ
        today_rank_badges = badges_for(today_menu_text)

        # 今週の表の各メニューにもバッジ情報を付与（行ハイライト用）
        for item in week_menus:
            menu_name = item.get("menu")
            item["rank_badges"] = badges_for(menu_name)
            item["is_ranked"] = bool(item["rank_badges"])

    except Exception as e:
        error_message = f"メニュー取得中にエラーが発生しました: {e}"

    context = {
        "today_date": today_date,
        "weekday_char": weekday_char,
        "menu_lines": menu_lines,
        "week_menus": week_menus,
        "error_message": error_message,
        "average_scores": average_scores,
        "comments": comments,


        # ★ 追加：テンプレで右上に王冠＋順位表示するため
        "today_rank_badges": today_rank_badges,
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
                    comment=comment,  # ★追加
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
    戻り値:
      {
        "overall": {"カルボナーラ": {"rank": 1, "score": 4.2}, ...},
        "taste":   {"カルボナーラ": {"rank": 2, "score": 4.5}, ...},
        "volume":  {"カルボナーラ": {"rank": 3, "score": 4.1}, ...},
      }
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
    表示順は 総合→味→量 に固定
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
                "label": label,          # 総合 / 味 / 量
                "rank": info["rank"],    # 1..5
                "icon": icon,            # 👑
            })

    return badges


def menu_ranking(request):
    """
    メニューの評価ランキングを表示するビュー
    """
    # メニュー名ごとにグループ化し、味と量の平均値 + 評価件数を算出
    qs = MenuRating.objects.values('menu_name').annotate(
        avg_taste=Avg('taste_score'),
        avg_volume=Avg('volume_score'),
        rating_count=Count('id'),   # ★ 追加：評価件数（=表示する人数）
    ).annotate(
        # 総合得点 = (味平均 + 量平均) / 2
        overall_score=(F('avg_taste') + F('avg_volume')) / 2.0
    )

    # 各部門のトップ5を取得 (降順)
    ranking_overall = qs.order_by('-overall_score')[:5]
    ranking_taste = qs.order_by('-avg_taste')[:5]
    ranking_volume = qs.order_by('-avg_volume')[:5]

    context = {
        'ranking_overall': ranking_overall,
        'ranking_taste': ranking_taste,
        'ranking_volume': ranking_volume,
    }
    return render(request, 'teams/team_kitajaki/menu_ranking.html', context)
