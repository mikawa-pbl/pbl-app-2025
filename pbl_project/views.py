from django.shortcuts import render

def index(request):
    teams = [
        # データサンプル
        # {"name": "Team A", "url": "/team_a/"},
        {"name": "Team Terrace", "url": "/team_terrace/"},  # ← 新チームを追加
        {"name": "H34VVY U53RZZ", "url": "/h34vvy_u53rzz/"},
    ]
    return render(request, "top.html", {"teams": teams})
