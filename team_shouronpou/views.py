from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from django.core.signing import BadSignature, SignatureExpired
from .models import Post, Account, Application
from .forms import PostForm, AccountForm, LoginForm, ProfileForm

DB_ALIAS = 'team_shouronpou'
COOKIE_KEY = 'team_shouronpou_user_id'

class JSTMixin:
    def dispatch(self, request, *args, **kwargs):
        timezone.activate('Asia/Tokyo')
        return super().dispatch(request, *args, **kwargs)

def get_current_user(request):
    try:
        user_id = request.get_signed_cookie(COOKIE_KEY)
        return Account.objects.using(DB_ALIAS).get(pk=user_id)
    except (KeyError, BadSignature, SignatureExpired, Account.DoesNotExist):
        return None

# --- 一般ビュー ---
def index(request):
    return render(request, 'teams/team_shouronpou/index.html')

def members(request):
    try:
        from .models import Member
        qs = Member.objects.using(DB_ALIAS).all()
    except ImportError:
        qs = []
    return render(request, 'teams/team_shouronpou/members.html', {'members': qs})

# --- 掲示板機能 ---
class PostListView(JSTMixin, generic.ListView):
    model = Post
    template_name = 'teams/team_shouronpou/post_list.html'
    context_object_name = 'posts'

    def get_queryset(self):
        return Post.objects.using(DB_ALIAS).all().order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['login_user'] = get_current_user(self.request)
        return context

class PostDetailView(JSTMixin, generic.DetailView):
    model = Post
    template_name = 'teams/team_shouronpou/post_detail.html'

    def get_queryset(self):
        return Post.objects.using(DB_ALIAS).all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_current_user(self.request)
        context['login_user'] = user
        if user:
            # すでに応募しているかチェック
            context['is_applied'] = Application.objects.using(DB_ALIAS).filter(post=self.object, user=user).exists()
        return context

class PostCreateView(JSTMixin, generic.CreateView):
    model = Post
    form_class = PostForm
    template_name = 'teams/team_shouronpou/post_new.html'
    success_url = reverse_lazy('team_shouronpou:post_list')

    def form_valid(self, form):
        user = get_current_user(self.request)
        if user:
            form.instance.created_by = user
        return super().form_valid(form)

class PostUpdateView(JSTMixin, generic.UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'teams/team_shouronpou/post_edit.html'
    success_url = reverse_lazy('team_shouronpou:post_list')

    def get_queryset(self):
        return Post.objects.using(DB_ALIAS).all()

class PostDeleteView(JSTMixin, generic.DeleteView):
    model = Post
    template_name = 'teams/team_shouronpou/post_delete.html'
    success_url = reverse_lazy('team_shouronpou:post_list')

    def get_queryset(self):
        return Post.objects.using(DB_ALIAS).all()

# --- 応募・取消処理 ---
def apply_for_post(request, pk):
    if request.method == 'POST':
        user = get_current_user(request)
        post = get_object_or_404(Post.objects.using(DB_ALIAS), pk=pk)
        email = request.POST.get('applicant_email')

        if user and email:
            # 1人1回制限
            exists = Application.objects.using(DB_ALIAS).filter(post=post, user=user).exists()
            if not exists:
                Application.objects.using(DB_ALIAS).create(post=post, user=user, email=email)
                post.current_participants += 1
                post.save(using=DB_ALIAS)
    return redirect('team_shouronpou:post_detail', pk=pk)

def cancel_application(request, pk):
    if request.method == 'POST':
        user = get_current_user(request)
        post = get_object_or_404(Post.objects.using(DB_ALIAS), pk=pk)
        app = Application.objects.using(DB_ALIAS).filter(post=post, user=user).first()
        if app:
            app.delete(using=DB_ALIAS)
            post.current_participants = max(0, post.current_participants - 1)
            post.save(using=DB_ALIAS)
    return redirect('team_shouronpou:post_detail', pk=pk)

# --- 認証・マイページ ---
def signup(request):
    if request.method == 'POST':
        form = AccountForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.password = make_password(form.cleaned_data['password'])
            user.save(using=DB_ALIAS)
            return redirect('team_shouronpou:login')
    else:
        form = AccountForm()
    return render(request, 'teams/team_shouronpou/signup.html', {'form': form})

def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            try:
                user = Account.objects.using(DB_ALIAS).get(username=username)
                if check_password(password, user.password):
                    response = redirect('team_shouronpou:post_list')
                    response.set_signed_cookie(COOKIE_KEY, user.id, max_age=86400)
                    return response
                else:
                    form.add_error(None, "パスワードが違います")
            except Account.DoesNotExist:
                form.add_error(None, "ユーザーが見つかりません")
    else:
        form = LoginForm()
    return render(request, 'teams/team_shouronpou/login.html', {'form': form})

def logout(request):
    response = redirect('team_shouronpou:login')
    response.delete_cookie(COOKIE_KEY)
    return response

def mypage(request):
    user = get_current_user(request)
    if not user:
        return redirect('team_shouronpou:login')
    
    my_posts = Post.objects.using(DB_ALIAS).filter(created_by=user).order_by('-created_at')
    my_apps = Application.objects.using(DB_ALIAS).filter(user=user).select_related('post')
    
    return render(request, 'teams/team_shouronpou/mypage.html', {
        'user': user,
        'my_posts': my_posts,
        'my_applications': my_apps
    })

def profile_edit(request):
    user = get_current_user(request)
    if not user:
        return redirect('team_shouronpou:login')
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=user)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.save(using=DB_ALIAS)
            return redirect('team_shouronpou:mypage')
    else:
        form = ProfileForm(instance=user)
    return render(request, 'teams/team_shouronpou/profile_edit.html', {'form': form, 'user': user})