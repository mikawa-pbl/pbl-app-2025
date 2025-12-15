from django.shortcuts import render, get_object_or_404, redirect
from .models import MyPage, Member
from .forms import MyPageEditForm, UserRegisterForm, LoginForm

def index(request):
    # ログイン済みならホームへリダイレクト
    if 'user_id' in request.session:
        return redirect('nanakorobiyaoki:home')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user_id = form.cleaned_data['user_id']
            password = form.cleaned_data['password']
            
            try:
                user = MyPage.objects.get(user_id=user_id, password=password)
                request.session['user_id'] = user.user_id
                return redirect('nanakorobiyaoki:home')
            except MyPage.DoesNotExist:
                form.add_error(None, 'ユーザーIDまたはパスワードが間違っています。')
    else:
        form = LoginForm()

    return render(request, 'teams/nanakorobiyaoki/index.html', {'form': form})

from .models import Community, Post, Comment
from .forms import CommunityForm, PostForm, CommentForm

def home(request):
    if 'user_id' not in request.session:
        return redirect('nanakorobiyaoki:index')
        
    # 参加しているコミュニティ
    joined_communities = []
    user = MyPage.objects.filter(user_id=request.session['user_id']).first()
    if user:
        joined_communities = user.communities.all().order_by('-created_at')
    
    # 全コミュニティ一覧 (community_listの内容も統合)
    all_communities = Community.objects.all().order_by('-created_at')
            
    return render(request, 'teams/nanakorobiyaoki/home.html', {
        'joined_communities': joined_communities,
        'communities': all_communities
    })

def members(request):
    qs = Member.objects.using('nanakorobiyaoki').all()  # ← team_terrace DBを明示
    return render(request, 'teams/nanakorobiyaoki/members.html', {'members': qs})

# ... existing code ...

# login_viewはindexに統合されたのでリダイレクトさせる（URL互換性のため残す場合）
def login_view(request):
    return redirect('nanakorobiyaoki:index')

def logout_view(request):
    request.session.flush() # セッションをクリア
    return redirect('nanakorobiyaoki:index')

# community_list は home に統合されたが、一応残しておくか、homeにリダイレクトでもよい
# 今回は要望により「ホーム画面でコミュニティ一覧を表示」なので、homeでカバーする
def community_list(request):
    return redirect('nanakorobiyaoki:home')


def mypage(request):
    qs = MyPage.objects.using('nanakorobiyaoki').all()
    return render(request, 'teams/nanakorobiyaoki/mypage.html', {'mypage': qs})

def register(request):
    qs = MyPage.objects.using('nanakorobiyaoki').all()
    return render(request, 'teams/nanakorobiyaoki/register.html', {'register': qs})

# 【追加】 詳細ページ用のビュー関数
def user_profile(request, user_id):
    if 'user_id' not in request.session:
        return redirect('nanakorobiyaoki:index')

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
            request.session['user_id'] = user.user_id # 自動ログイン
            return redirect('nanakorobiyaoki:user_profile_edit', user_id=user.user_id)  # user_id を渡してリダイレクト
    else:
        form = UserRegisterForm()
    return render(request, 'teams/nanakorobiyaoki/user_register.html', {'form': form})


from .models import Community, Post, Comment
from .forms import CommunityForm, PostForm, CommentForm

def community_create(request):
    # ログインチェック（簡易）
    if 'user_id' not in request.session:
        return redirect('nanakorobiyaoki:login')
    
    if request.method == 'POST':
        form = CommunityForm(request.POST, request.FILES)
        if form.is_valid():
            community = form.save(commit=False)
            community.save()
            # 作成者をメンバーに追加
            user = get_object_or_404(MyPage, user_id=request.session['user_id'])
            community.members.add(user)
            return redirect('nanakorobiyaoki:community_list')
    else:
        form = CommunityForm()
    return render(request, 'teams/nanakorobiyaoki/community_form.html', {'form': form})

def community_detail(request, community_id):
    community = get_object_or_404(Community, id=community_id)
    posts = community.posts.all().order_by('-created_at')
    
    # 参加メンバーかチェック
    is_member = False
    if 'user_id' in request.session:
        user = get_object_or_404(MyPage, user_id=request.session['user_id'])
        if user in community.members.all():
            is_member = True
            
    return render(request, 'teams/nanakorobiyaoki/community_detail.html', {
        'community': community, 
        'posts': posts,
        'is_member': is_member
    })

def community_join(request, community_id):
    if 'user_id' not in request.session:
        return redirect('nanakorobiyaoki:login')
        
    community = get_object_or_404(Community, id=community_id)
    user = get_object_or_404(MyPage, user_id=request.session['user_id'])
    
    community.members.add(user)
    return redirect('nanakorobiyaoki:community_detail', community_id=community_id)

def post_create(request, community_id):
    if 'user_id' not in request.session:
        return redirect('nanakorobiyaoki:login')
    
    community = get_object_or_404(Community, id=community_id)
    user = get_object_or_404(MyPage, user_id=request.session['user_id'])
    
    # メンバーでないと投稿できない
    if user not in community.members.all():
        return redirect('nanakorobiyaoki:community_detail', community_id=community_id)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.community = community
            post.author = user
            post.save()
            return redirect('nanakorobiyaoki:community_detail', community_id=community_id)
    
    return redirect('nanakorobiyaoki:community_detail', community_id=community_id)

def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all().order_by('created_at')
    comment_form = CommentForm()
    
    return render(request, 'teams/nanakorobiyaoki/post_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form
    })

def comment_create(request, post_id):
    if 'user_id' not in request.session:
        return redirect('nanakorobiyaoki:login')
        
    post = get_object_or_404(Post, id=post_id)
    user = get_object_or_404(MyPage, user_id=request.session['user_id'])
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = user
            comment.save()
            
    return redirect('nanakorobiyaoki:post_detail', post_id=post_id)

def login_view(request):
    return redirect('nanakorobiyaoki:index')

def logout_view(request):
    request.session.flush()
    return redirect('nanakorobiyaoki:index')

def community_list(request):
    communities = Community.objects.all().order_by('-created_at')
    return render(request, 'teams/nanakorobiyaoki/community_list.html', {'communities': communities})
