from django.shortcuts import render
from .models import Member

def index(request):
    return render(request, 'teams/team_northcliff/index.html')

def members(request):
    qs = Member.objects.using('team_northcliff').all()  # ← team_northcliff DBを明示
    return render(request, 'teams/team_northcliff/members.html', {'members': qs})