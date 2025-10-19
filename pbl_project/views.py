# myproject/views.py
from django.shortcuts import render

def index(request):
    teams = [
        # {"name": "Team A", "url": "/team-a/"}
    ]
    return render(request, "top.html", {"teams": teams})
