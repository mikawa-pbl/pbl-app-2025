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

def gikamap2(request):
    return render(request, "teams/agileca/gikamap2.html")

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

# タグ検索
def search_by_attributes(request):
    # 1. フォーム表示用に、すべての利用可能な属性タグを取得
    all_attributes = Attribute.objects.all()
    
    # 2. ユーザーが選択した属性IDのリストを取得
    # リクエストから 'attribute_ids' という名前の複数の値を取得 (GET.getlist)
    selected_ids = request.GET.getlist('attribute_ids')
    
    classrooms = Classroom.objects.all()

    if selected_ids:
        # 3. 選択されたIDを整数に変換 (セキュリティと確実性のため)
        try:
            selected_ids = [int(id) for id in selected_ids]
        except ValueError:
            selected_ids = []

        # 4. **AND検索**ロジックの実行 (フィルタのチェーン接続)
        for attr_id in selected_ids:
            # 各IDをAND条件としてQuerySetに適用
            classrooms = classrooms.filter(attributes__id=attr_id)
        
    context = {
        'all_attributes': all_attributes,      # UI表示用の全属性
        'selected_ids': [str(i) for i in selected_ids], # テンプレートのチェックボックス状態復元用
        'classrooms': classrooms               # 検索結果
    }
    
    return render(request, 'teams/agileca/search_by_attributes.html', context)

# 教授名検索
def search_by_professor(request):
    # フォームからキーワードを取得（name="q"）
    query = request.GET.get('q', '') 
    
    # Qオブジェクトは、教授名がNULLの場合も検索結果に影響を与えないようにするために便利
    # Classroom の Professor フィールドは null=True が許可されているため
    classrooms = Classroom.objects.all() 
    
    if query:
        # 教授名で部分一致検索 (icontains: 大文字小文字を区別しない)
        # 外部キーを辿る: professor__name
        search_filter = Q(professor__name__icontains=query)
        
        # フィルタを適用
        classrooms = classrooms.filter(search_filter).distinct()
        
    context = {
        'query': query, 
        'rooms': classrooms # テンプレートの変数名を 'rooms' に統一
    }
    return render(request, 'teams/agileca/search_by_professor.html', context)

# 教室名検索
def search_by_room_name(request):
    # フォームからキーワードを取得（name="q"）
    query = request.GET.get('q', '') 
    
    classrooms = Classroom.objects.all() 
    
    if query:
        # 部屋名 (room_name) で部分一致検索 (icontains: 大文字小文字を区別しない)
        classrooms = classrooms.filter(room_name__icontains=query)
        
    context = {
        'query': query, 
        'rooms': classrooms # テンプレートの変数名を 'rooms' に統一
    }
    
    return render(request, 'teams/agileca/search_by_classroom.html', context)

# 複合検索 (詳細検索)
def search_complex(request):
    # フォームから各検索条件を取得
    building_query = request.GET.get('building_name', '')
    room_query = request.GET.get('room_name', '')
    professor_query = request.GET.get('professor_name', '')
    selected_ids = request.GET.getlist('attribute_ids')

    # 初期クエリセット (全件)
    # allで引っ張っている点に不安あり
    rooms = Classroom.objects.all()

    # フィルタリングの適用 (条件が指定されている場合のみ適用)
    # ここでフィルターを分けていると計算量的によくないかも、現時点のサイズではおそらく問題にはならない
    
    # 1. 建物名
    if building_query:
        rooms = rooms.filter(building__name__contains=building_query)
    
    # 2. 部屋名
    if room_query:
        rooms = rooms.filter(room_name__icontains=room_query)
        
    # 3. 担当教授名
    if professor_query:
        rooms = rooms.filter(professor__name__icontains=professor_query)
        
    # 4. 属性 (タグ) - AND検索
    if selected_ids:
        try:
            selected_ids_int = [int(id) for id in selected_ids]
        except ValueError:
            selected_ids_int = []
            
        for attr_id in selected_ids_int:
            rooms = rooms.filter(attributes__id=attr_id)

    # 5. サイズ
    size_query = request.GET.get('size', '')
    if size_query:
        rooms = rooms.filter(size=size_query)
    
    # コンテキストの作成 (テンプレートへのデータの受け渡し)
    all_attributes = Attribute.objects.all()
    
    context = {
        'rooms': rooms,
        'all_attributes': all_attributes,
        # フォームの状態を維持するために、入力された値を返す
        'building_name': building_query,
        'room_name': room_query,
        'professor_name': professor_query,
        'selected_ids': selected_ids, # テンプレート側で stringformat:"s" と比較するため、文字列リストのままでOK
        'size': size_query,
    }
    
    return render(request, 'teams/agileca/search_complex.html', context)