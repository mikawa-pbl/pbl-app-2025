from django.shortcuts import render, redirect
from .models import Good
from .forms import GoodsForm
from types import SimpleNamespace
from django.db import connections
import uuid

# def index(request):
#     return render(request, 'teams/team_cake/index.html')

def index(request):
    try:
        # 通常はORMで取得（UUIDField の変換が走る）
        qs = Good.objects.using('team_cake').all()
        return render(request, 'teams/team_cake/index.html', {'goods': qs})
    except ValueError:
        # DB に古い整数 ID 等、UUID として変換できない値が入っている場合のフォールバック。
        # テンプレートは objects の `.name` / `.price` を参照する想定のため SimpleNamespace を作る。
        conn = connections['team_cake']
        with conn.cursor() as cur:
            cur.execute('SELECT id, name, price FROM team_cake_good')
            rows = cur.fetchall()

        goods = [SimpleNamespace(id=row[0], name=row[1], price=row[2]) for row in rows]
        return render(request, 'teams/team_cake/index.html', {'goods': goods})

def registration_goods(request):
    if request.method == 'POST':
        form = GoodsForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('team_cake:registration_goods')  # 適切な名前のURLに変更
    else:
        form = GoodsForm()
    return render(request, 'teams/team_cake/registrationGoods.html', {'form': form})