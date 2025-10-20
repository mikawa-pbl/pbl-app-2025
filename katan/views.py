from django.shortcuts import render
from .models import Member

def index(request):
    return render(request, 'teams/katan/index.html')

def members(request):
    qs = Member.objects.using('katan').all()  # ← katan DBを明示
    return render(request, 'teams/katan/members.html', {'members': qs})