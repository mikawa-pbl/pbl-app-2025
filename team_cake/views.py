from django.shortcuts import render, redirect
from .models import Good
from .forms import GoodsForm

def index(request):
    return render(request, 'teams/team_cake/index.html')

def goods(request):
    qs = Good.objects.using('team_cake').all()  # ← team_cake DBを明示
    return render(request, 'teams/team_cake/goods.html', {'goods': qs})

def registration_goods(request):
    if request.method == 'POST':
        form = GoodsForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('team_cake:registration_goods')  # 適切な名前のURLに変更
    else:
        form = GoodsForm()
    return render(request, 'teams/team_cake/registrationGoods.html', {'form': form})