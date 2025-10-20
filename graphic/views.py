from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from .models import Member

def index(request):
    return render(request, 'teams/graphic/index.html')

def members(request):
    qs = Member.objects.using('graphic').all()  # ← team_terrace DBを明示
    return render(request, 'teams/graphic/members.html', {'members': qs})