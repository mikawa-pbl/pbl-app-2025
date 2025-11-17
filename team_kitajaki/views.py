from django.shortcuts import render
from .models import Member

# ★ 追加：PDF からメニューを取ってくる関数
from .menu_pdf import get_today_menu


def index(request):
    return render(request, 'teams/team_kitajaki/index.html')


def members(request):
    qs = Member.objects.using('team_kitajaki').all()
    return render(request, 'teams/team_kitajaki/members.html', {'members': qs})


# ★ 追加：今日のメニュー
def today_menu(request):
    error_message = None
    today_date = None
    weekday_char = None
    menu_lines = []

    try:
        info = get_today_menu()
        today_date = info["date"]
        weekday_char = info["weekday_char"]
        menu_lines = info["menu_lines"]
    except Exception as e:
        error_message = f"メニュー取得中にエラーが発生しました: {e}"

    context = {
        "today_date": today_date,
        "weekday_char": weekday_char,
        "menu_lines": menu_lines,
        "error_message": error_message,
    }
    return render(request, 'teams/team_kitajaki/today_menu.html', context)
