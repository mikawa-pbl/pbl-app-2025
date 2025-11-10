from django.shortcuts import render

# Create your views here.
from .models import Member

def index(request):
    return render(request, 'teams/agileca/index.html')

def members(request):
    qs = Member.objects.using('agileca').all()  # ← team_terrace DBを明示
    return render(request, 'teams/agileca/members.html', {'members': qs})

def gikamap(request):
    return render(request, "teams/agileca/gikamap.html")

def imc(request):
    return render(request, "teams/agileca/imc.html")