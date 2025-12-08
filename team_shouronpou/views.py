from django.shortcuts import render
from django.views import generic  
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Member, Post

def index(request):
    return render(request, 'teams/team_shouronpou/index.html')

def members(request):
    qs = Member.objects.using('team_shouronpou').all()  # ← team_terrace DBを明示
    return render(request, 'teams/team_shouronpou/members.html', {'members': qs})


# 投稿一覧
class PostListView(generic.ListView):
    model = Post
    template_name = 'teams/team_shouronpou/post_list.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        # .using() でDBを明示
        return Post.objects.using('team_shouronpou').order_by('-created_at')

# 投稿詳細
class PostDetailView(generic.DetailView):
    model = Post
    template_name = 'teams/team_shouronpou/post_detail.html'

    def get_queryset(self):
        # .using() でDBを明示
        return Post.objects.using('team_shouronpou').all()

# 新規投稿 (LoginRequiredMixin を削除)
class PostCreateView(generic.CreateView):
    model = Post
    template_name = 'teams/team_shouronpou/post_new.html'
    fields = [
        'title', 
        'content', 
        'recruitment_start_date', 
        'recruitment_end_date', 
        'max_participants'
    ]
    
    # ログイン不要のため author へのセット処理はなし

# 投稿編集 (LoginRequiredMixin, UserPassesTestMixin を削除)
class PostUpdateView(generic.UpdateView):
    model = Post
    template_name = 'teams/team_shouronpou/post_edit.html'
    fields = [
        'title', 
        'content', 
        'recruitment_start_date', 
        'recruitment_end_date', 
        'max_participants'
    ]

    def get_queryset(self):
        return Post.objects.using('team_shouronpou').all()

    # ログイン不要のため test_func はなし

# 投稿削除 (LoginRequiredMixin, UserPassesTestMixin を削除)
class PostDeleteView(generic.DeleteView):
    model = Post
    template_name = 'teams/team_shouronpou/post_delete.html'
    success_url = reverse_lazy('team_shouronpou:post_list') 

    def get_queryset(self):
        return Post.objects.using('team_shouronpou').all()