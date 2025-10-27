from django.shortcuts import render

def index(request):
    teams = [
        # データサンプル
        # {"name": "Team A", "url": "/team_a/"},
        {"name": "Team Terrace", "url": "/team_terrace/"},  # ← 新チームを追加
        {"name": "Team Cake", "url": "/team_cake/"},
        {"name": "Team Shouronpou", "url": "/team_shouronpou/"},
        {"name": "H34VVY U53RZZ", "url": "/h34vvy_u53rzz/"},
    ]
    return render(request, "top.html", {"teams": teams})
