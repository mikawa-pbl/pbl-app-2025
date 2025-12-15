from django.shortcuts import render
from .models import Member

def main(request):
    return render(request, 'teams/takenoko/main.html')

def members(request):
    qs = Member.objects.using('takenoko').all()  # ← team_terrace DBを明示
    return render(request, 'teams/takenoko/members.html', {'members': qs})

def purchased_items(request):
    return render(request, 'teams/takenoko/purchased_items.html')

def listing_items(request):
    return render(request, 'teams/takenoko/listing_items.html')

def product_details(request):
    return render(request, 'teams/takenoko/product_details.html')

def login(request):
    return render(request, 'teams/takenoko/login.html')

def signup(request):
    return render(request, 'teams/takenoko/signup.html')

def item_create(request):
    return render(request, 'teams/takenoko/item_create.html')
