from django.shortcuts import render
from .models import Item

def index(request):
    return render(request, 'teams/team_terrace/index.html')

def items(request):
    qs = Item.objects.using('team_terrace').all()  # ← team_c DBを明示
    return render(request, 'teams/team_terrace/items.html', {'items': qs})