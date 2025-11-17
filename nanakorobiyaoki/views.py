from django.shortcuts import render, get_object_or_404
from .models import Member,MyPage

def index(request):
    return render(request, 'teams/nanakorobiyaoki/index.html')

def members(request):
    qs = Member.objects.using('nanakorobiyaoki').all()  # ← team_terrace DBを明示
    return render(request, 'teams/nanakorobiyaoki/members.html', {'members': qs})

def mypage(request):
    qs = MyPage.objects.using('nanakorobiyaoki').all()
    return render(request, 'teams/nanakorobiyaoki/mypage.html', {'mypage': qs})

# 【追加】 詳細ページ用のビュー関数
def user_profile(request, user_id):
    # 1. URLから渡された user_id を使って、MyPageモデルからデータを1件取得
    #    (user_id=user_id は「モデルのuser_idフィールドが、引数のuser_idと一致するもの」)
    user_data = get_object_or_404(MyPage, user_id=user_id)
    
    # 2. 取得したデータを 'user' という名前でテンプレートに渡す
    context = {
        'user': user_data
    }
    
    # 3. 専用のテンプレート 'user_profile.html' を表示
    return render(request, 'teams/nanakorobiyaoki/mypage.html', context)

# メンバー一覧ページ用のビュー
def users(request):
    # MyPage モデルから全てのオブジェクトを取得する
    all_users = MyPage.objects.all()
    
    # 取得したリストを 'mypage' という名前でテンプレートに渡す
    context = {
        'users': all_users
    }
    return render(request, 'teams/nanakorobiyaoki/users.html', context)