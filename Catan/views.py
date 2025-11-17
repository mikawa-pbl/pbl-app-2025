from django.shortcuts import render
from .models import Member

def index(request):
    return render(request, 'teams/Catan/index.html')

def members(request):
    qs = Member.objects.using('Catan').all()  
    return render(request, 'teams/Catan/members.html', {'members': qs})

def shirushiru(request):
    # qs = Member.objects.using('Catan').all()
    return render(request, 'teams/Catan/shirushiru.html')