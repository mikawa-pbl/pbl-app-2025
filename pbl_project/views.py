from django.shortcuts import render

def index(request):
    teams = [
        # データサンプル
        # {"name": "Team A", "url": "/team_a/"},
        {"name": "Team TMR", "url": "/team_TMR/"},  # ← 新チームを追加
    ]
    return render(request, "top.html", {"teams": teams})
