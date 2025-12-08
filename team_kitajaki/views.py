from django.shortcuts import render, redirect
from django.db.models import Avg # ★ Avgをインポート

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
    
    # ★ 追加：平均スコア用の変数
    average_scores = None

    try:
        info = get_today_menu()
        today_date = info["date"]
        weekday_char = info["weekday_char"]
        menu_lines = info["menu_lines"]

        # ★ 今日のメニューテキストをDB検索用のキーとして取得 (ここでは1行目を使用)
        today_menu_text = menu_lines[0] if menu_lines else None
        
        # ★ 平均スコアを計算
        if today_menu_text:
            # メニュー名が完全に一致する評価を集計
            rating_stats = MenuRating.objects.filter(
                menu_name=today_menu_text
            ).aggregate(
                avg_taste=Avg('taste_score'),
                avg_volume=Avg('volume_score')
            )
            
            if rating_stats['avg_taste'] is not None:
                # 小数点以下1桁に丸める
                average_scores = {
                    'avg_taste': round(rating_stats['avg_taste'], 1),
                    'avg_volume': round(rating_stats['avg_volume'], 1),
                    # 評価数を取得
                    'count': MenuRating.objects.filter(menu_name=today_menu_text).count() 
                }

        # ★ 今週のメニュー一覧
        week_menus = get_this_week_menu()

    except Exception as e:
        error_message = f"メニュー取得中にエラーが発生しました: {e}"

    context = {
        "today_date": today_date,
        "weekday_char": weekday_char,
        "menu_lines": menu_lines,
        "week_menus": week_menus,
        "error_message": error_message,
        "average_scores": average_scores, # ★ コンテキストに追加
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

        # メニューがあり、評価値が取得できたらDBに保存
        if taste_rating and volume_rating and today_menu_text != "メニュー不明":
            try:
                # ★ 評価データをデータベースに保存
                MenuRating.objects.create(
                    menu_name=today_menu_text,
                    taste_score=int(taste_rating),
                    volume_score=int(volume_rating)
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
        }
        return render(request, "teams/team_kitajaki/rate_menu.html", context)

    # GETリクエスト（初期表示）の処理
    context = {
        "today_menu": today_menu_text,
        "today_date": today_date,
        "error_message": error_message,
    }
    return render(request, "teams/team_kitajaki/rate_menu.html", context)