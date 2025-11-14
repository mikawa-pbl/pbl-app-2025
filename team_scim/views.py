from django.shortcuts import render
from .models import Member

def index(request):
    return render(request, 'teams/team_scim/index.html')

def members(request):
    qs = Member.objects.using('team_scim').all()  # ← team_terrace DBを明示
    return render(request, 'teams/team_scim/members.html', {'members': qs})