from django.shortcuts import render
from .models import Member

def main(request):
    return render(request, 'teams/takenoko/main.html')

def members(request):
    qs = Member.objects.using('takenoko').all()  # ← team_terrace DBを明示
    return render(request, 'teams/takenoko/members.html', {'members': qs})

def product_details(request):
    return render(request, 'teams/takenoko/product_details.html')
