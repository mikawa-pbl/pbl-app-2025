from django.shortcuts import render
from .models import Member

def index(request):
    return render(request, 'teams/team_cake/index.html')

def members(request):
    qs = Member.objects.using('team_cake').all()  # ← team_cake DBを明示
    return render(request, 'teams/team_cake/members.html', {'members': qs})