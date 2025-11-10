from django.shortcuts import render
from .models import Member

def index(request):
    return render(request, 'teams/team_shouronpou/index.html')

def members(request):
    qs = Member.objects.using('team_shouronpou').all()  # ← team_terrace DBを明示
    return render(request, 'teams/team_shouronpou/members.html', {'members': qs})
