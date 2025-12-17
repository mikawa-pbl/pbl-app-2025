from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import TakenokoSignupForm

def main(request):
    return render(request, 'teams/takenoko/main.html')

def purchased_items(request):
    return render(request, 'teams/takenoko/purchased_items.html')

def listing_items(request):
    return render(request, 'teams/takenoko/listing_items.html')

def product_details(request):
    return render(request, 'teams/takenoko/product_details.html')

def login(request):
    return render(request, 'teams/takenoko/login.html')

def signup(request):
    if request.method == "POST":
        form = TakenokoSignupForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "ユーザー登録が完了しました。")
            return redirect("takenoko:login")
        else:
            messages.error(request, "入力内容を確認してください。")
    else:
        form = TakenokoSignupForm()
    return render(request, 'teams/takenoko/signup.html', {"form": form})

def item_create(request):
    return render(request, 'teams/takenoko/item_create.html')

def create_complete(request):
    return render(request, 'teams/takenoko/create_complete.html')

def start_trading(request):
    return render(request, 'teams/takenoko/start_trading.html')

def item_delete(request):
    return render(request, 'teams/takenoko/item_delete.html')

def item_edit(request):
    return render(request, 'teams/takenoko/item_edit.html')

def edit_complete(request):
    return render(request, 'teams/takenoko/edit_complete.html')