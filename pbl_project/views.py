from django.shortcuts import render


def index(request):
    teams = [
        # データサンプル
        # {"name": "Team A", "url": "/team_a/"},
        {"name": "nanakorobiyaoki", "url": "/nanakorobiyaoki/"},  # ← 新チームを追加
        {"name": "Team AKB5", "url": "/team_akb5/"},  # ← 新チームを追加
        {"name": "Team TMR", "url": "/team_TMR/"},  # ← 新チームを追加
        {"name": "Graphics", "url": "/graphics/"},  # ← 新チームを追加
        {"name": "Team Terrace", "url": "/team_terrace/"},  # ← 新チームを追加
        {"name": "takenoko", "url": "/takenoko/"},
        {"name": "Team UDuv run python manage.py makemigrations", "url": "/team_UD/"},
        {"name": "Team TeXTeX", "url": "/team_TeXTeX/"},
        {"name": "Team Cake", "url": "/team_cake/"},
        {"name": "Team Shouronpou", "url": "/team_shouronpou/"},
        {"name": "H34VVY U53RZZ", "url": "/h34vvy_u53rzz/"},
    ]
    return render(request, "top.html", {"teams": teams})
