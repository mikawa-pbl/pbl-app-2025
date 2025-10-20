from django.shortcuts import render

def index(request):
    teams = [
        # データサンプル
        # {"name": "Team A", "url": "/team_a/"},
        {"name": "Team Terrace", "url": "/team_terrace/"},  # ← 新チームを追加
	{"name": "Team Shouronpou", "url": "/team_shouronpou/"},
    ]
    return render(request, "top.html", {"teams": teams})
