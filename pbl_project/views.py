from django.shortcuts import render

def index(request):
    teams = [
        # データサンプル
        # {"name": "Team A", "url": "/team_a/"},
        {"name": "SHIOKARA", "url": "/shiokara/"},  # ← 新チームを追加
    ]
    return render(request, "top.html", {"teams": teams})
