from django.shortcuts import render

def index(request):
    teams = [
        # データサンプル
        # {"name": "Team A", "url": "/team_a/"},
        {"name": "Team Empiricism", "url": "/team_empiricism/"},  # ← 新チームを追加
    ]
    return render(request, "top.html", {"teams": teams})
