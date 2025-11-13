from django.shortcuts import render
from .models import Member, Main, Temp

def index(request):
    return render(request, 'teams/team_TeXTeX/index.html')

def members(request):
    qs = Member.objects.using('team_TeXTeX').all()  # ← team_terrace DBを明示
    return render(request, 'teams/team_TeXTeX/members.html', {'members': qs})

def main(request):
    qs = Main.objects.using('team_TeXTeX').all()  # ← team_terrace DBを明示
    return render(request, 'teams/team_TeXTeX/main.html', {'main': qs})

def temp(request):
    qs = Temp.objects.using('team_TeXTeX').all()  # ← team_terrace DBを明示
    return render(request, 'teams/team_TeXTeX/temp.html', {'temp': qs})