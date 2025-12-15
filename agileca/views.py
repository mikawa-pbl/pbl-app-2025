from django.shortcuts import render

# Create your views here.
from .models import Member, Classroom

from django.db.models import Q # 複雑なクエリ（OR検索など）に使う
from .models import * # 検索対象のモデルをインポート

def index(request):
    return render(request, 'teams/agileca/index.html')

def members(request):
    qs = Member.objects.using('agileca').all()  # ← team_terrace DBを明示
    return render(request, 'teams/agileca/members.html', {'members': qs})

def gikamap(request):
    return render(request, "teams/agileca/gikamap.html")

def imc(request):
    return render(request, "teams/agileca/imc.html")

def secretariat(request):
    return render(request, "teams/agileca/secretariat.html")

def health(request):
    return render(request, "teams/agileca/health.html")

def welfare(request):
    return render(request, "teams/agileca/welfare.html")

def library(request):
    return render(request, "teams/agileca/library.html")

def classrooms(request):
    qs = Classroom.objects.using('agileca').all()  # ← team_terrace DBを明示
    return render(request, 'teams/agileca/classroom.html', {'classrooms': qs})

# 建物名検索
def search_by_buildings(request):
    # 1. request.GET から検索キーワードを取得
    # キーワードは name="q" で指定したので 'q' を使う
    query = request.GET.get('q') 
    
    rooms = Classroom.objects.all() # 初期値は全て
    print(len(rooms))
    
    if query is not None:
        # 2. キーワードが存在する場合、データベースをフィルタリング
        rooms = rooms.filter(building__name__contains=query)
        
    context = {
        'query': query, # テンプレートにキーワードを渡し、フォームに再表示させる
        'rooms': rooms
    }
    return render(request, "teams/agileca/search_by_buildings.html", context)
