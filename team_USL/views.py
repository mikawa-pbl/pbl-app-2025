from django.shortcuts import render
from .models import Member

def index(request):
    return render(request, 'teams/team_USL/index.html')

def members(request):
    qs = Member.objects.using('team_USL').all()  # ← team_USL DBを明示
    return render(request, 'teams/team_USL/members.html', {'members': qs})
# Create your views here.
