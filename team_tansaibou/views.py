from django.shortcuts import render

from .models import Member


def index(request):
    return render(request, 'teams/team_tansaibou/index.html')

def members(request):
    qs = Member.objects.all()
    return render(request, 'teams/team_tansaibou/members.html', {'members': qs})