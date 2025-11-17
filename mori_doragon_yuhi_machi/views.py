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