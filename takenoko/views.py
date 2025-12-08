from django.shortcuts import render
from .models import Member

def index(request):
    return render(request, 'teams/takenoko/product_details.html')

def members(request):
    qs = Member.objects.using('takenoko').all()  # ← team_terrace DBを明示
    return render(request, 'teams/takenoko/members.html', {'members': qs})
# Create your views here.
