from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.urls import reverse_lazy
from django.utils import timezone  # ← これをインポート
from .models import Member, Post
from .forms import PostForm

# データベース名を定数化
DB_ALIAS = 'team_shouronpou'

# --- 【重要】日本時間にするためのMixin ---
class JSTMixin:
    """
    このクラスを継承したビューは、処理中にタイムゾーンが
    強制的に 'Asia/Tokyo' (日本時間) になります。
    """
    def dispatch(self, request, *args, **kwargs):
        timezone.activate('Asia/Tokyo')
        return super().dispatch(request, *args, **kwargs)

# --- メンバー一覧 (関数ベースビュー) ---
def index(request):
    return render(request, 'teams/team_shouronpou/index.html')

def members(request):
    qs = Member.objects.using(DB_ALIAS).all()
    return render(request, 'teams/team_shouronpou/members.html', {'members': qs})


# --- 掲示板ビュー (Mixinを追加) ---

# 投稿一覧 (JSTMixin を最初に追加)
class PostListView(JSTMixin, generic.ListView):
    model = Post
    template_name = 'teams/team_shouronpou/post_list.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        return Post.objects.using(DB_ALIAS).order_by('-created_at')

# 投稿詳細 (JSTMixin を追加)
class PostDetailView(JSTMixin, generic.DetailView):
    model = Post
    template_name = 'teams/team_shouronpou/post_detail.html'

    def get_queryset(self):
        return Post.objects.using(DB_ALIAS).all()

# 新規投稿 (JSTMixin を追加)
class PostCreateView(JSTMixin, generic.CreateView):
    model = Post
    template_name = 'teams/team_shouronpou/post_new.html'
    form_class = PostForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save(using=DB_ALIAS)
        return super().form_valid(form)

# 投稿編集 (JSTMixin を追加)
class PostUpdateView(JSTMixin, generic.UpdateView):
    model = Post
    template_name = 'teams/team_shouronpou/post_edit.html'
    form_class = PostForm

    def get_queryset(self):
        return Post.objects.using(DB_ALIAS).all()

# 投稿削除 (JSTMixin を追加)
class PostDeleteView(JSTMixin, generic.DeleteView):
    model = Post
    template_name = 'teams/team_shouronpou/post_delete.html'
    success_url = reverse_lazy('team_shouronpou:post_list') 

    def get_queryset(self):
        return Post.objects.using(DB_ALIAS).all()

# --- 応募ボタンの処理 (関数ベースビュー) ---
def apply_for_post(request, pk):
    # 関数ベースビューの場合は、処理の先頭でタイムゾーンを変更
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
