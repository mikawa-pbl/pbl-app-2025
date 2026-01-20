from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy, reverse
from django.db.models import Q
from django.contrib import messages
from .models import ExperimentPost
from .forms import ExperimentPostForm, PasswordConfirmForm

# テンプレートの格納パス定数 (変更が容易なように)
TEMPLATE_DIR = 'teams/team_empiricism/'

class ExperimentListView(ListView):
    """
    3.2 掲示板(一覧)機能
    ・記事一覧表示、検索、フィルタリング、ソート、ページネーション
    """
    model = ExperimentPost # models.py
    template_name = TEMPLATE_DIR + 'experiment_list.html'
    context_object_name = 'posts'
    paginate_by = 10  # ページネーション

    def get_queryset(self):
        # 一覧表示時に自動処理を実行（要件3.6）
        ExperimentPost.process_automatic_updates()
        
        queryset = ExperimentPost.objects.all()
        
        # --- フィルタリング (検索) 機能 ---
        # キーワード検索 (タイトル・本文)
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(organizer_name__icontains=query) # 主催者名でも検索可能に(V3)
            )
        
        # カテゴリフィルタ (Laboratory ID)
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(laboratory__id=category)
            
        # ステータスフィルタ
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        # --- ソート機能 ---
        sort_by = self.request.GET.get('sort', 'newest')
        
        if sort_by == 'newest':
            # 投稿日時順 (新しい順)
            queryset = queryset.order_by('-created_at')
        elif sort_by == 'oldest':
            # 投稿日時順 (古い順)
            queryset = queryset.order_by('created_at')
        elif sort_by == 'schedule_near':
            # 実験実施日順 (近い順、ただし過去のものは除外または後ろにするなどの調整が可能)
            # ここでは単純に募集開始日昇順
            queryset = queryset.order_by('start_date')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 検索条件を保持するためにコンテキストに追加
        context['current_sort'] = self.request.GET.get('sort', 'newest')
        context['current_category'] = self.request.GET.get('category', '')
        context['current_q'] = self.request.GET.get('q', '')
        
        # フィルタ用研究室一覧 (Ver 5.0)
        from .models import Laboratory
        context['laboratories'] = Laboratory.objects.all()
        return context

class ExperimentDetailView(DetailView):
    """
    3.3 投稿詳細・応募機能
    誰でも閲覧可能(V3)
    """
    model = ExperimentPost
    template_name = TEMPLATE_DIR + 'experiment_detail.html'
    context_object_name = 'post'

class ExperimentCreateView(CreateView):
    """
    3.4 投稿機能
    ログイン不要、誰でも投稿可能(V3)
    """
    model = ExperimentPost
    form_class = ExperimentPostForm
    template_name = TEMPLATE_DIR + 'experiment_form.html'
    success_url = reverse_lazy('experiment_list')

class PasswordConfirmView(FormView):
    """
    編集・削除前のパスワード確認画面
    """
    template_name = TEMPLATE_DIR + 'password_confirm.html'
    form_class = PasswordConfirmForm

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.post_obj = get_object_or_404(ExperimentPost, pk=self.kwargs['pk'])
        self.action = self.kwargs.get('action') # 'edit' or 'delete'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = self.post_obj
        context['action'] = self.action
        return context

    def form_valid(self, form):
        input_password = form.cleaned_data['password']
        
        # パスワード照合
        if input_password == self.post_obj.edit_password:
            # 認証成功: セッションにフラグを立てる
            # キー: verified_post_{pk}
            self.request.session[f'verified_post_{self.post_obj.pk}'] = True
            
            if self.action == 'edit':
                return redirect('experiment_edit', pk=self.post_obj.pk)
            elif self.action == 'delete':
                return redirect('experiment_delete', pk=self.post_obj.pk)
        
        # 認証失敗
        form.add_error('password', 'パスワードが間違っています。')
        return self.form_invalid(form)

class ExperimentUpdateView(UpdateView):
    """
    3.4 編集機能
    パスワード確認済みの場合のみアクセス可(V3)
    """
    model = ExperimentPost
    form_class = ExperimentPostForm
    template_name = TEMPLATE_DIR + 'experiment_form.html'

    def dispatch(self, request, *args, **kwargs):
        # セッション確認
        pk = self.kwargs['pk']
        if not request.session.get(f'verified_post_{pk}'):
            # 未認証ならパスワード確認画面へ
            return redirect('password_confirm', pk=pk, action='edit')
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        # 編集完了後はセッションから認証情報を消しても良いが、
        # 続けて編集する可能性も考慮して保持するか、あるいは削除するか。
        # ここでは保持する。
        return reverse('experiment_detail', kwargs={'pk': self.object.pk})

class ExperimentDeleteView(DeleteView):
    """
    3.4 削除機能
    パスワード確認済みの場合のみアクセス可(V3)
    """
    model = ExperimentPost
    template_name = TEMPLATE_DIR + 'experiment_confirm_delete.html'
    success_url = reverse_lazy('experiment_list')

    def dispatch(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        if not request.session.get(f'verified_post_{pk}'):
            return redirect('password_confirm', pk=pk, action='delete')
        return super().dispatch(request, *args, **kwargs)

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import IntegrityError
import json
from .models import Laboratory

@require_POST
def add_laboratory(request):
    """
    研究室を動的に追加するAPI (Ver 5.0)
    """
    try:
        data = json.loads(request.body)
        name = data.get('name')
        if not name:
            return JsonResponse({'error': 'Name is required'}, status=400)
        
        lab, created = Laboratory.objects.get_or_create(name=name)
        
        return JsonResponse({
            'id': lab.id,
            'name': lab.name,
            'created': created
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except IntegrityError:
        return JsonResponse({'error': 'Database error'}, status=500)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)