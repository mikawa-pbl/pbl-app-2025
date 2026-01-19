# (あなたのアプリ名)/views.py

from django.shortcuts import render, redirect, get_object_or_404
from .models import Member, Place
from django.views.decorators.http import require_POST # POSTメソッドのみ許可する
from django.utils import timezone


# データベースのエイリアスを定数にしておくと便利
DB_ALIAS = 'mori_doragon_yuhi_machi'

def index(request):
    """
    居場所ダッシュボード (メインページ)
    - メンバーごとの現在地と、それを変更するフォーム
    を表示します。
    """
    # 1. 全メンバーを「現在の場所」情報と一緒に取得
    all_members = Member.objects.using(DB_ALIAS).select_related('current_place').order_by('name')
    
    # 学年ごとにグループ化
    # 学年ごとにグループ化
    # 順番を定義: Staff -> Dr -> M2 -> M1 -> B4 -> Other
    # 列構成:
    # 1列目: Staff, Dr
    # 2列目: M2, M1
    # 3列目: B4, Other
    
    grade_columns_config = [
        ['Staff', 'Dr'],          # Col 1
        ['M2', 'M1'],             # Col 2
        ['B4', 'Other']           # Col 3
    ]

    columns = []
    
    # メンバーをリスト化して処理しやすくする
    members_list = list(all_members)

    for grade_group in grade_columns_config:
        current_column = []
        for grade in grade_group:
            # その学年のメンバーを抽出
            members_in_grade = [m for m in members_list if m.grade == grade]
            if members_in_grade:
                current_column.append((grade, members_in_grade))
        # カラムにデータがあれば追加（空でもレイアウト保持のため追加しても良いが、今回はデータがある場合のみとするか、空リストでも渡すか。
        # レイアウト崩れを防ぐなら、空でもカラム枠はあったほうがいいかもしれないが、
        # ここでは「データがあるグループ」のリストをカラムとして追加する。
        # ただし、カラム自体の存在は保証したいので、空リストでもappendする。
        columns.append(current_column)

    # 2. フォーム用に、全場所のリストも取得
    all_places = Place.objects.using(DB_ALIAS).order_by('name')

    # 3. テンプレートに渡すデータ（コンテキスト）
    context = {
        'columns': columns,  # 3列分のデータ [[(grade, members)...], [...], [...]]
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
        place_category = request.POST.get('place_category', 'Other')
        new_place = Place(name=place_name, category=place_category)
        
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

def add_member(request):
    """
    新しいメンバー (Member) をデータベースに追加するビュー
    """
    
    # テンプレート表示用の基本データ（エラー時や一覧表示用）
    all_members = Member.objects.using(DB_ALIAS).select_related('current_place').order_by('name')
    base_context = {
        'all_members': all_members,
    }
    
    if request.method == 'POST':
        # 1. フォームから名前を取得 (空白除去)
        member_name = request.POST.get('member_name', '').strip()
        member_photo = request.FILES.get('member_photo')
        
        # 2. 空チェック
        if not member_name:
            context = base_context.copy()
            context['error_message'] = 'メンバー名を入力してください。'
            return render(request, 'teams/mori_doragon_yuhi_machi/add_member.html', context)

        # 3. 重複チェック (大文字小文字を区別せず検索)
        if Member.objects.using(DB_ALIAS).filter(name__iexact=member_name).exists():
            context = base_context.copy()
            context['error_message'] = f'エラー: メンバー「{member_name}」はすでに登録済みです。'
            return render(request, 'teams/mori_doragon_yuhi_machi/add_member.html', context)

        # 4. 作成と保存
        grade = request.POST.get('grade', 'Other')
        new_member = Member(name=member_name, photo=member_photo, grade=grade)
        new_member.save(using=DB_ALIAS)
        
        # 5. 保存後、トップページ(index)に戻る
        # (続けて追加したい場合は 'mori_doragon_yuhi_machi:add_member' にリダイレクトでもOK)
        return redirect('mori_doragon_yuhi_machi:add_member')
    
    else:
        # GETリクエスト: フォームを表示
        return render(request, 'teams/mori_doragon_yuhi_machi/add_member.html', base_context)
    
@require_POST
def delete_member(request):
    """
    指定されたIDのメンバー (Member) をデータベースから削除する処理
    """
    try:
        # 1. POSTデータから削除対象のメンバーIDを取得
        member_id = request.POST.get('member_id')

        # 2. IDに基づいてMemberオブジェクトを取得
        member_to_delete = get_object_or_404(Member.objects.using(DB_ALIAS), id=member_id)

        # 3. 削除を実行
        member_to_delete.delete(using=DB_ALIAS)

    except Exception as e:
        print(f"メンバーの削除中にエラーが発生しました: {e}")

    # 4. 削除後は「メンバー追加画面」に戻ることで、連続して整理しやすくする
    return redirect('mori_doragon_yuhi_machi:add_member')

def reset_to_home(request):
    """
    全員の場所を「自宅」にリセットするビュー
    """
    if request.method == "POST":
        # 1. 'Home'カテゴリの場所を探す
        home_place = Place.objects.using(DB_ALIAS).filter(category='Home').first()
        
        # 2. なければ名前が「自宅」の場所を探す
        if not home_place:
            home_place = Place.objects.using(DB_ALIAS).filter(name='自宅').first()
            
        # 3. それでもなければ作成する
        if not home_place:
            home_place = Place.objects.using(DB_ALIAS).create(name='自宅', category='Home')
            
        # 全メンバーの場所を更新
        Member.objects.using(DB_ALIAS).all().update(current_place=home_place, updated_at=timezone.now())
        
    return redirect('mori_doragon_yuhi_machi:index')