from django.shortcuts import render, redirect # ★ redirect を追加
from .models import Member

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

    try:
        info = get_today_menu()
        today_date = info["date"]
        weekday_char = info["weekday_char"]
        menu_lines = info["menu_lines"]

        # ★ 追加：今週のメニュー一覧
        week_menus = get_this_week_menu()

    except Exception as e:
        error_message = f"メニュー取得中にエラーが発生しました: {e}"

    context = {
        "today_date": today_date,
        "weekday_char": weekday_char,
        "menu_lines": menu_lines,
        "week_menus": week_menus,
        "error_message": error_message,
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
        today_menu_text = info["menu_lines"][0] if info["menu_lines"] else "メニュー不明"
    except Exception as e:
        error_message = f"メニュー取得中にエラーが発生しました: {e}"

    # POSTリクエスト（フォーム送信）の処理
    if request.method == 'POST':
        taste_rating = request.POST.get('taste_rating')
        volume_rating = request.POST.get('volume_rating')

        # ★ ここに評価データをデータベースに保存するなどの処理が入ります
        
        # 処理結果を context に追加して画面に表示
        context = {
            "today_menu": today_menu_text,
            "today_date": today_date,
            "error_message": error_message,
            "success_message": "評価を送信しました！ありがとうございます😊", # 成功メッセージを追加
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