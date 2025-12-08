from django.shortcuts import render
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


# ★ 追加：メニュー評価画面のビュー（今回はダミーのテンプレートをレンダリングします）
def rate_menu(request):
    # 評価処理や、評価フォームの表示などが入りますが、今回は遷移確認のためのダミーです。
    info = get_today_menu()
    today_menu_text = info["menu_lines"][0] if info["menu_lines"] else "メニュー不明"
    context = {
        "today_menu": today_menu_text,
    }
    return render(request, "teams/team_kitajaki/rate_menu.html", context) # ★ rate_menu.htmlというテンプレートが必要です