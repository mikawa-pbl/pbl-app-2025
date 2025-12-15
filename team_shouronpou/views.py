from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from django.core.signing import BadSignature, SignatureExpired
from .models import Post, Account
from .forms import PostForm, AccountForm, LoginForm, ProfileForm
from django.urls import reverse_lazy

DB_ALIAS = 'team_shouronpou'
COOKIE_KEY = 'team_shouronpou_user_id'

class JSTMixin:
    def dispatch(self, request, *args, **kwargs):
        timezone.activate('Asia/Tokyo')
        return super().dispatch(request, *args, **kwargs)

# --- 便利な関数：ログイン中のユーザー情報を取得 ---
def get_current_user(request):
    try:
        # 署名付きCookieからユーザーIDを取り出す
        user_id = request.get_signed_cookie(COOKIE_KEY)
        return Account.objects.using(DB_ALIAS).get(pk=user_id)
    except (KeyError, BadSignature, SignatureExpired, Account.DoesNotExist):
        # Cookieがない、改ざんされている、ユーザーが消えている場合は未ログイン扱い
        return None

# --- 一般ビュー ---
def index(request):
    return render(request, 'teams/team_shouronpou/index.html')

def members(request):
    qs = Member.objects.using(DB_ALIAS).all()
    return render(request, 'teams/team_shouronpou/members.html', {'members': qs})

# --- 掲示板ビュー ---
class PostListView(JSTMixin, generic.ListView):
    model = Post
    template_name = 'teams/team_shouronpou/post_list.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        return Post.objects.using(DB_ALIAS).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # ここで「ログイン中のユーザー情報」をHTMLに渡しています
        context['login_user'] = get_current_user(self.request) 
        return context

class PostDetailView(JSTMixin, generic.DetailView):
    model = Post
    template_name = 'teams/team_shouronpou/post_detail.html'

    def get_queryset(self):
        return Post.objects.using(DB_ALIAS).all()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # これがないと、詳細画面で「自分かどうか」の判定ができません
        context['login_user'] = get_current_user(self.request)
        return context

# 新規投稿
class PostCreateView(JSTMixin, generic.CreateView):
    model = Post
    template_name = 'teams/team_shouronpou/post_new.html'
    form_class = PostForm
    success_url = reverse_lazy('team_shouronpou:post_list')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        
        # ★追加: ログイン中なら、投稿者をセットする
        current_user = get_current_user(self.request)
        if current_user:
            self.object.created_by = current_user
            
        self.object.save(using=DB_ALIAS)
        return super().form_valid(form)

# 投稿編集 (シンプルになりました)
class PostUpdateView(JSTMixin, generic.UpdateView):
    model = Post
    template_name = 'teams/team_shouronpou/post_edit.html'
    form_class = PostForm

    def get_queryset(self):
        return Post.objects.using(DB_ALIAS).all()
    
    def dispatch(self, request, *args, **kwargs):
        # 編集対象の投稿を取得
        obj = self.get_object() 
        
        # 投稿者が記録されている場合のみチェック
        if obj.created_by:
            current_user = get_current_user(request)
            # 「未ログイン」または「投稿者本人でない」場合は編集させない
            if not current_user or current_user.id != obj.created_by.id:
                # 詳細画面に強制リダイレクト（あるいはエラー画面）
                return redirect('team_shouronpou:post_detail', pk=obj.pk)
        
        # 投稿者が記録されていない(None)場合は、今まで通り誰でも編集OK
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save(using=DB_ALIAS)
        return super().form_valid(form)
    
    def get_success_url(self):
        # 編集完了後、その投稿の詳細ページへ移動する
        from django.urls import reverse
        return reverse('team_shouronpou:post_detail', kwargs={'pk': self.object.pk})

class PostDeleteView(JSTMixin, generic.DeleteView):
    model = Post
    template_name = 'teams/team_shouronpou/post_delete.html'
    success_url = reverse_lazy('team_shouronpou:post_list') 

    def get_queryset(self):
        return Post.objects.using(DB_ALIAS).all()
    
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.created_by:
            current_user = get_current_user(request)
            if not current_user or current_user.id != obj.created_by.id:
                return redirect('team_shouronpou:post_detail', pk=obj.pk)
        return super().dispatch(request, *args, **kwargs)

# --- 応募処理 ---
def apply_for_post(request, pk):
    timezone.activate('Asia/Tokyo')
    post = get_object_or_404(Post.objects.using(DB_ALIAS), pk=pk)
    if request.method == 'POST':
        if post.max_participants is not None:
            if post.current_participants < post.max_participants:
                post.current_participants += 1
                post.save(using=DB_ALIAS)
        else:
            post.current_participants += 1
            post.save(using=DB_ALIAS)
    return redirect('team_shouronpou:post_detail', pk=pk)


# 1. ユーザー登録
def signup(request):
    if request.method == 'POST':
        form = AccountForm(request.POST)
        if form.is_valid():
            account = form.save(commit=False)
            account.password = make_password(form.cleaned_data['password'])
            account.save(using=DB_ALIAS)
            return redirect('team_shouronpou:login')
    else:
        form = AccountForm()
    return render(request, 'teams/team_shouronpou/signup.html', {'form': form})

# 2. ログイン
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            try:
                user = Account.objects.using(DB_ALIAS).get(username=username)
                if check_password(password, user.password):
                    # ★変更点: セッションではなくCookieにIDを保存
                    response = redirect('team_shouronpou:post_list')
                    # 署名付きCookieをセット (有効期限: 1日 = 86400秒)
                    response.set_signed_cookie(COOKIE_KEY, user.id, max_age=86400)
                    return response
                else:
                    form.add_error(None, "パスワードが違います")
            except Account.DoesNotExist:
                form.add_error(None, "ユーザーが見つかりません")
    else:
        form = LoginForm()
    
    return render(request, 'teams/team_shouronpou/login.html', {'form': form})

# Cookieを削除するログアウト
def logout_view(request):
    response = redirect('team_shouronpou:login')
    # Cookieを削除
    response.delete_cookie(COOKIE_KEY)
    return response

def mypage(request):
    # ログイン中のユーザーを取得
    user = get_current_user(request)
    
    # ログインしていなければログイン画面へ強制移動
    if not user:
        return redirect('team_shouronpou:login')
    
    return render(request, 'teams/team_shouronpou/mypage.html', {'user': user})

def profile_edit(request):
    user = get_current_user(request)
    if not user:
        return redirect('team_shouronpou:login')

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=user)
        if form.is_valid():
            profile = form.save(commit=False)  # まず保存前のデータを受け取る
            profile.save(using=DB_ALIAS) # DBを指定して保存
            return redirect('team_shouronpou:mypage')
    else:
        # 既存のデータをフォームに入れた状態で表示
        form = ProfileForm(instance=user)

    return render(request, 'teams/team_shouronpou/profile_edit.html', {'form': form})