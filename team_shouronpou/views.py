from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.urls import reverse_lazy
from django.utils import timezone
from .models import Member, Post
from .forms import PostForm

DB_ALIAS = 'team_shouronpou'

class JSTMixin:
    def dispatch(self, request, *args, **kwargs):
        timezone.activate('Asia/Tokyo')
        return super().dispatch(request, *args, **kwargs)

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

class PostDetailView(JSTMixin, generic.DetailView):
    model = Post
    template_name = 'teams/team_shouronpou/post_detail.html'

    def get_queryset(self):
        return Post.objects.using(DB_ALIAS).all()

# 新規投稿
class PostCreateView(JSTMixin, generic.CreateView):
    model = Post
    template_name = 'teams/team_shouronpou/post_new.html'
    form_class = PostForm
    success_url = reverse_lazy('team_shouronpou:post_list')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save(using=DB_ALIAS)
        return super().form_valid(form)

# 投稿編集 (シンプルになりました)
class PostUpdateView(JSTMixin, generic.UpdateView):
    model = Post
    template_name = 'teams/team_shouronpou/post_edit.html'
    form_class = PostForm

    def get_queryset(self):
        return Post.objects.using(DB_ALIAS).all()
    
    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save(using=DB_ALIAS)
        return super().form_valid(form)

class PostDeleteView(JSTMixin, generic.DeleteView):
    model = Post
    template_name = 'teams/team_shouronpou/post_delete.html'
    success_url = reverse_lazy('team_shouronpou:post_list') 

    def get_queryset(self):
        return Post.objects.using(DB_ALIAS).all()

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