from django.shortcuts import render
from .models import Member

def index(request):
    return render(request, 'teams/team_akb5/index.html')

def members(request):
    qs = Member.objects.using('team_akb5').all()  # ← team_terrace DBを明示
    return render(request, 'teams/team_akb5/members.html', {'members': qs})
