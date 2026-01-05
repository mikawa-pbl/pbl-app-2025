from django.shortcuts import render
from .models import Member, User

def index(request):
    users = User.objects.using('team_northcliff').all()
    return render(request, 'teams/team_northcliff/index.html', {'users': users})

def members(request):
    qs = Member.objects.using('team_northcliff').all()  # ← team_northcliff DBを明示
    return render(request, 'teams/team_northcliff/members.html', {'members': qs})

def ui(request, username):
    return render(request, 'teams/team_northcliff/ui.html', {'username': username})

# 追加: map_ui ページを username コンテキストで表示
def map_ui(request, username):
    return render(request, 'teams/team_northcliff/map_ui.html', {'username': username})