from django.shortcuts import render

def index(request):
    teams = [
        # データサンプル
        # {"name": "Team A", "url": "/team_a/"},
        {"name": "Team Northcliff", "url": "/team_northcliff/"},  # ← 新チームを追加
    ]
    return render(request, "top.html", {"teams": teams})
