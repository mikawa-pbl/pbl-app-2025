from django.shortcuts import render
from .models import Member

def index(request):
    return render(request, 'teams/h34vvy_u53rzz/index.html')

def members(request):
    qs = Member.objects.using('h34vvy_u53rzz').all()  # ← h34vvy_u53rzz DBを明示
    return render(request, 'teams/h34vvy_u53rzz/members.html', {'members': qs})
