from django.shortcuts import render
from .models import Member

def index(request):
    return render(request, 'teams/nanakorobiyaoki/index.html')

def members(request):
    qs = Member.objects.using('nanakorobiyaoki').all()  # ← team_terrace DBを明示
    return render(request, 'teams/nanakorobiyaoki/members.html', {'members': qs})