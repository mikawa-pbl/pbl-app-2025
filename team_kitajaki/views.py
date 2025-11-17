from django.shortcuts import render
from .models import Member

from .menu_pdf import get_today_menu, get_this_week_menu  # ← ここ

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
        "week_menus": week_menus,      # ← 追加
        "error_message": error_message,
    }
    return render(request, "teams/team_kitajaki/today_menu.html", context)
