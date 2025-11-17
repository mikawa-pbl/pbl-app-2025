from django.shortcuts import render
from .models import Member, Main, Temp, url, main_select

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

def main_select(request,select):
    template_name = f'teams/team_TeXTeX/main/{select}.html'
    return render(request, template_name)

def url(request):
    qs = url.objects.using('team_TeXTeX').all()  # ← team_terrace DBを明示
    return render(request, 'teams/team_TeXTeX/main/url.html', {'temp': qs})


