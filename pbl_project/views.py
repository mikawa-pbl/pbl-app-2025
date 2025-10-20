from django.shortcuts import render


def index(request):
    teams = [
        # データサンプル
        # {"name": "Team A", "url": "/team_a/"},
        {"name": "Team Terrace", "url": "/team_terrace/"},  # ← 新チームを追加
        {"name": "Team Tansaibou", "url": "/team_tansaibou/"},
    ]
    return render(request, "top.html", {"teams": teams})
