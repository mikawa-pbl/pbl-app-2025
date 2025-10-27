from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from .models import Member

def index(request):
    return render(request, 'teams/graphics/index.html')

def members(request):
    qs = Member.objects.using('graphics').all()  # ← team_terrace DBを明示
    return render(request, 'teams/graphics/members.html', {'members': qs})