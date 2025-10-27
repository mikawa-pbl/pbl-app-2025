from django.shortcuts import render

def index(request):
    teams = [
        # データサンプル
        # {"name": "Team A", "url": "/team_a/"},
        {"name": "Team Terrace", "url": "/team_terrace/"},  # ← 新チームを追加
        {"name": "Agileca", "url": "/agileca/"},  # ← アジャイルカ(Agileca)を追加
    ]
    return render(request, "top.html", {"teams": teams})
