# Create your views here.
from django.shortcuts import render
from .models import Member

def index(request):
    return render(request, 'teams/shouronpou/index.html')

def members(request):
    qs = Member.objects.using('shouronpou').all()  # ← team_terrace DBを明示
    return render(request, 'teams/shouronpou/members.html', {'members': qs})
