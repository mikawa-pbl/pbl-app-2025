# Create your views here.
from django.shortcuts import render
from .models import Member

def index(request):
    return render(request, 'teams/team_giryulink/index.html')


def members(request):
    qs = Member.objects.using('team_giryulink').all()  # ← Chỉ định rõ DB team_giryulink
    return render(request, 'teams/team_giryulink/members.html', {'members': qs})