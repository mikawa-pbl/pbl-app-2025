from django.shortcuts import render

def index(request):
    teams = [
        # データサンプル
        # {"name": "Team A", "url": "/team_a/"},
        
        {"name": "Team AKB5", "url": "/team_akb5/"},  # ← 新チームを追加
        {"name": "Team Terrace", "url": "/team_terrace/"},  # ← 新チームを追加
    ]
    return render(request, "top.html", {"teams": teams})
