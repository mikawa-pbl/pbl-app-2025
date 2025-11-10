from django.shortcuts import render
from .models import Good

def index(request):
    return render(request, 'teams/team_cake/index.html')

def goods(request):
    qs = Good.objects.using('team_cake').all()  # ← team_cake DBを明示
    return render(request, 'teams/team_cake/goods.html', {'goods': qs})