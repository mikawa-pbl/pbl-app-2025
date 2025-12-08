from django.shortcuts import render
from .models import Member

# Create your views here.

def index(request):
    return render(request, 'teams/mori_doragon_yuhi_machi/index.html')

def members(request):
    qs = Member.objects.using('mori_doragon_yuhi_machi').all()  # ← mori_doragon_yuhi_machi DBを明示
    return render(request, 'teams/mori_doragon_yuhi_machi/members.html', {'members': qs})