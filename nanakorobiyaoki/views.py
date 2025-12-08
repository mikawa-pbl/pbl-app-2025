from django.shortcuts import render, get_object_or_404, redirect
from .models import MyPage, Member
from .forms import MyPageEditForm,UserRegisterForm

def index(request):
    return render(request, 'teams/nanakorobiyaoki/index.html')

def members(request):
    qs = Member.objects.using('nanakorobiyaoki').all()  # ← team_terrace DBを明示
    return render(request, 'teams/nanakorobiyaoki/members.html', {'members': qs})

def mypage(request):
    qs = MyPage.objects.using('nanakorobiyaoki').all()
    return render(request, 'teams/nanakorobiyaoki/mypage.html', {'mypage': qs})

def register(request):
    qs = MyPage.objects.using('nanakorobiyaoki').all()
    return render(request, 'teams/nanakorobiyaoki/register.html', {'register': qs})

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

def user_profile_edit(request, user_id):
    # 編集対象のユーザーデータを取得 (見つからなければ404)
    user_data = get_object_or_404(MyPage, user_id=user_id)
    
    # === POSTリクエスト (フォーム送信時) の処理 ===
    if request.method == 'POST':
        # 既存のデータ(instance)を、送信されたデータ(request.POST, FILES)で上書きする
        form = MyPageEditForm(request.POST, request.FILES, instance=user_data)
        
        if form.is_valid():  # データが有効かチェック
            form.save()      # 有効ならデータベースに保存
            
            # 保存後、そのユーザーの詳細ページにリダイレクト
            return redirect('nanakorobiyaoki:user_profile', user_id=user_data.user_id)
    
    # === GETリクエスト (ページ表示時) の処理 ===
    else:
        # 既存のデータをフォームにセットして表示
        form = MyPageEditForm(instance=user_data)

    # 'form' と 'user' をテンプレートに渡す
    context = {
        'form': form,
        'user': user_data  # ページのタイトルなどで使うため
    }
    return render(request, 'teams/nanakorobiyaoki/user_profile_edit.html', context)

def user_register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()  # フォームのデータを保存し、保存されたインスタンスを取得
            return redirect('nanakorobiyaoki:user_profile_edit', user_id=user.user_id)  # user_id を渡してリダイレクト
    else:
        form = UserRegisterForm()
    return render(request, 'teams/nanakorobiyaoki/user_register.html', {'form': form})
