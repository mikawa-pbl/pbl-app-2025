# (あなたのアプリ名)/views.py

from django.shortcuts import render, redirect, get_object_or_404
from .models import Member, Place
from django.views.decorators.http import require_POST # POSTメソッドのみ許可する


# データベースのエイリアスを定数にしておくと便利
DB_ALIAS = 'mori_doragon_yuhi_machi'

def index(request):
    """
    居場所ダッシュボード (メインページ)
    - メンバーごとの現在地と、それを変更するフォーム
    を表示します。
    """
    
    # 1. 全メンバーを「現在の場所」情報と一緒に取得 (select_relatedで効率化)
    #    .order_by('name') で名前順に並べます
    all_members = Member.objects.using(DB_ALIAS).select_related('current_place').order_by('name')
    
    # 2. フォーム用に、全場所のリストも取得
    all_places = Place.objects.using(DB_ALIAS).order_by('name')

    # 3. テンプレートに渡すデータ（コンテキスト）
    context = {
        'all_members': all_members,  # メンバー一覧 (更新フォーム兼用)
        'all_places': all_places,    # フォームの<option>用
    }
    
    # index.html をレンダリング
    return render(request, 'teams/mori_doragon_yuhi_machi/index.html', context)


@require_POST
def update_location(request):
    """
    メンバーの居場所を更新する処理
    (このビューは変更不要です)
    """
    try:
        member_id = request.POST.get('member_id')
        place_id = request.POST.get('place_id')

        member = get_object_or_404(Member.objects.using(DB_ALIAS), id=member_id)
        
        if not place_id:
            place = None
        else:
            place = get_object_or_404(Place.objects.using(DB_ALIAS), id=place_id)

        member.current_place = place
        member.save(using=DB_ALIAS)

    except Exception as e:
        print(f"エラーが発生しました: {e}")

    return redirect('mori_doragon_yuhi_machi:index')

def members(request):
    """
    （ご提示いただいたビュー）
    単純な全メンバーのリストを表示します。
    """
    qs = Member.objects.using(DB_ALIAS).all()
    return render(request, 'teams/mori_doragon_yuhi_machi/members.html', {'members': qs})





# def add_place(request):
#     """
#     新しい場所 (Place) をデータベースに追加するビュー
#     - GET: 場所名を入力するフォームを表示
#     - POST: フォームデータを取得し、新しいPlaceオブジェクトを作成して保存
#     """

#     # 1. 全メンバーを「現在の場所」情報と一緒に取得 (select_relatedで効率化)
#     #    .order_by('name') で名前順に並べます
#     all_members = Member.objects.using(DB_ALIAS).select_related('current_place').order_by('name')
    
#     # 2. フォーム用に、全場所のリストも取得
#     all_places = Place.objects.using(DB_ALIAS).order_by('name')

#     # 3. テンプレートに渡すデータ（コンテキスト）
#     context = {
#         'all_members': all_members,  # メンバー一覧 (更新フォーム兼用)
#         'all_places': all_places,    # フォームの<option>用
#     }

#     if request.method == 'POST':
#         # 1. POSTデータから場所名を取得
#         # フォームの入力フィールドのname属性が 'place_name' であると仮定
#         place_name = request.POST.get('place_name') 
        
#         # 2. 場所名が空でないかバリデーション
#         if place_name:
#             # 3. 新しいPlaceオブジェクトを作成
#             new_place = Place(name=place_name)
            
#             # 4. 指定されたデータベースエイリアスを使用して保存 (追加)
#             new_place.save(using=DB_ALIAS)
            
#             # 5. 保存後、一覧画面などにリダイレクト
#             # 'mori_doragon_yuhi_machi:index' はあなたが定義したURL名に合わせる
#             return redirect('mori_doragon_yuhi_machi:index') 
#         else:
#             # エラーメッセージをテンプレートに渡す処理などを追加できます
#             context = {
#                 'error_message': '場所名を入力してください。', 
#                 'all_members': all_members,  # メンバー一覧 (更新フォーム兼用)
#                 'all_places': all_places,    # フォームの<option>用
#             }
#             return render(request, 'teams/mori_doragon_yuhi_machi/add_place.html', context)
    
#     else:
#         # GETリクエストの場合: フォームを表示するテンプレートをレンダリング
#         # このテンプレート (add_place.html) は別途作成が必要です
#         return render(request, 'teams/mori_doragon_yuhi_machi/add_place.html', context)

# (あなたのアプリ名)/views.py

# ... (既存のインポートと定義: DB_ALIAS) ...

# ... (index, update_location ビューなど) ...

def add_place(request):
    """
    新しい場所 (Place) をデータベースに追加するビュー
    - GET: 場所名を入力するフォームを表示
    - POST: フォームデータを取得し、重複をチェックした後、新しいPlaceオブジェクトを作成して保存
    """
    
    # テンプレートに渡すための基本データを取得（エラー時にも必要）
    # indexビューと同じ処理
    all_members = Member.objects.using(DB_ALIAS).select_related('current_place').order_by('name')
    all_places = Place.objects.using(DB_ALIAS).order_by('name')
    base_context = {
        'all_members': all_members,
        'all_places': all_places,
    }
    
    if request.method == 'POST':
        # 1. POSTデータから場所名を取得し、前後の空白を除去
        place_name = request.POST.get('place_name', '').strip() 
        
        # 2. 場所名が空でないかバリデーション
        if not place_name:
            # 場所名が空の場合
            context = base_context.copy()
            context['error_message'] = '場所名を入力してください。'
            return render(request, 'teams/mori_doragon_yuhi_machi/add_place.html', context)

        # ★ 3. 重複チェックの追加 ★
        # 大文字・小文字を区別せず、同じ名前の場所がすでに存在するか検索 (Djangoの__iexactを使用)
        if Place.objects.using(DB_ALIAS).filter(name__iexact=place_name).exists():
            # 重複が見つかった場合
            context = base_context.copy()
            context['error_message'] = f'エラー: 場所「{place_name}」はすでに登録済みです。'
            return render(request, 'teams/mori_doragon_yuhi_machi/add_place.html', context)

        # 4. 新しいPlaceオブジェクトを作成
        new_place = Place(name=place_name)
        
        # 5. 指定されたデータベースエイリアスを使用して保存 (追加)
        new_place.save(using=DB_ALIAS)
        
        # 6. 保存後、一覧画面などにリダイレクト
        return redirect('mori_doragon_yuhi_machi:add_place') 
    
    else:
        # GETリクエストの場合: フォームを表示するテンプレートをレンダリング
        return render(request, 'teams/mori_doragon_yuhi_machi/add_place.html', base_context)

# ... (delete_place ビューなど、既存のコードはそのまま) ...


@require_POST
def delete_place(request):
    """
    指定されたIDの場所 (Place) をデータベースから削除する処理。
    """
    try:
        # 1. POSTデータから削除対象の場所のIDを取得
        # フォームの入力フィールドのname属性が 'place_id' であると仮定
        place_id = request.POST.get('place_id')

        # 2. IDに基づいてPlaceオブジェクトを取得（見つからない場合は404エラー）
        place_to_delete = get_object_or_404(Place.objects.using(DB_ALIAS), id=place_id)

        # 3. 削除を実行
        place_to_delete.delete(using=DB_ALIAS)
        
        # 補足: 関連するMemberの current_place が自動的に NULL に設定されます（ForeignKeyのon_delete設定によりますが、通常はNULL）

    except Exception as e:
        print(f"場所の削除中にエラーが発生しました: {e}")

    # 4. 削除後、一覧画面などにリダイレクト
    return redirect('mori_doragon_yuhi_machi:index')
