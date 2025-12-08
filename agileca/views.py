from django.shortcuts import render

# Create your views here.
from .models import Member, Classroom

def index(request):
    return render(request, 'teams/agileca/index.html')

def members(request):
    qs = Member.objects.using('agileca').all()  # ← team_terrace DBを明示
    return render(request, 'teams/agileca/members.html', {'members': qs})

def gikamap(request):
    return render(request, "teams/agileca/gikamap.html")

def imc(request):
    return render(request, "teams/agileca/imc.html")

def secretariat(request):
    return render(request, "teams/agileca/secretariat.html")

def health(request):
    return render(request, "teams/agileca/health.html")

def welfare(request):
    return render(request, "teams/agileca/welfare.html")

def library(request):
    return render(request, "teams/agileca/library.html")

def classrooms(request):
    qs = Classroom.objects.using('agileca').all()  # ← team_terrace DBを明示
    return render(request, 'teams/agileca/classroom.html', {'classrooms': qs})
