from django.shortcuts import render
from .models import Member

def index(request):
    return render(request, 'teams/shiokara/index.html')

def members(request):
    qs = Member.objects.using('shiokara').all()  # ← shiokar DBを明示
    return render(request, 'teams/shiokara/members.html', {'members': qs})