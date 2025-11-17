from django.shortcuts import render
from .models import Member

def index(request):
    return render(request, 'teams/ssk/index.html')

def members(request):
    qs = Member.objects.using('ssk').all()  # ← ssk DBを明示
    return render(request, 'teams/ssk/members.html', {'members': qs})