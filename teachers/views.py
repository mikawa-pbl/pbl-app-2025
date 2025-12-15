from django.shortcuts import render

# Create your views here.
from .models import Member

def index(request):
    return render(request, 'teams/teachers/index.html')

def members(request):
    qs = Member.objects.using('teachers').all()  # ← shiokara DBを明示
    return render(request, 'teams/teachers/members.html', {'members': qs})
