from django.shortcuts import render


def index(request):
    teams = [
        {"name": "Team USL", "url": "/team_USL/"},  # ← 新チームを追加
        {"name": "Team Empiricism", "url": "/team_empiricism/"},  # ← 新チームを追加
        {"name": "Team Kitajaki", "url": "/team_kitajaki/"},  # ← 新チームを追加
        {"name": "Catan", "url": "/Catan/"},  # ← 新チームを追加
        {"name": "SHIOKARA", "url": "/shiokara/"},  # ← 新チームを追加
        {"name": "Team Northcliff", "url": "/team_northcliff/"},  # ← 新チームを追加
        {"name": "nanakorobiyaoki", "url": "/nanakorobiyaoki/"},  # ← 新チームを追加
        {"name": "Team AKB5", "url": "/team_akb5/"},  # ← 新チームを追加
        {"name": "Team TMR", "url": "/team_TMR/"},  # ← 新チームを追加
        {"name": "Graphics", "url": "/graphics/"},  # ← 新チームを追加
        {"name": "Team Terrace", "url": "/team_terrace/"},  # ← 新チームを追加
        {"name": "Agileca", "url": "/agileca/"},  # ← アジャイルカ(Agileca)を追加
        {"name": "Team SCIM", "url": "/team_scim/"},  # ← 新チームを追加
        {"name": "ssk", "url": "/ssk/"},
        {"name": "Team Tansaibou", "url": "/team_tansaibou/"},
        {"name": "mori_doragon_yuhi_machi", "url": "/mori_doragon_yuhi_machi/"},  # ← 新チームを追加
        {"name": "Team Giryulink", "url": "/team_giryulink/"},
        {"name": "takenoko", "url": "/takenoko/"},
        {"name": "Team UD", "url": "/team_UD/"},
        {"name": "Team TeXTeX", "url": "/team_TeXTeX/"},
        {"name": "Team Cake", "url": "/team_cake/"},
        {"name": "Team Shouronpou", "url": "/team_shouronpou/"},
        {"name": "H34VVY U53RZZ", "url": "/h34vvy_u53rzz/"},
        {"name": "Teachers", "url": "/teachers/"},
    ]
    return render(request, "top.html", {"teams": teams})
