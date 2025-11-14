from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from .models import Member

def index(request):
    return render(request, 'teams/team_empiricism/index.html')

def members(request):
    qs = Member.objects.using('team_empiricism').all()  # ← team_empiricism DBを明示
    return render(request, 'teams/team_empiricism/members.html', {'members': qs})