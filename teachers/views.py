# papers/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q

from .models import Paper
from .forms import PaperForm

# 一覧
def paper_list(request):
    # 許可するソート項目（URLの?sort=... をDBのフィールド名にマップ）
    sort_map = {
        'title': 'title',
        'author': 'author',
        'year': 'year',
        'booktitle': 'booktitle',
        'submitter': 'submitter',
        'submit_time': 'submit_time',
    }

    sort_key = request.GET.get('sort', 'year')   # デフォルト
    direction = request.GET.get('dir', 'desc')   # 'asc' or 'desc'

    order_field = sort_map.get(sort_key, 'year')
    if direction == 'desc':
        order_field = '-' + order_field

    papers = Paper.objects.all().order_by(order_field, 'title')

    context = {
        'papers': papers,
        'sort': sort_key,
        'dir': direction,
    }
    return render(request, 'teams/teachers/paper_list.html', context)

# 詳細
def paper_detail(request, pk):
    paper = get_object_or_404(Paper, pk=pk)
    return render(request, 'teams/teachers/paper_detail.html', {'paper': paper})

# 登録（Create）
def paper_create(request):
    if request.method == 'POST':
        form = PaperForm(request.POST, request.FILES)  # ← FILES が重要
        if form.is_valid():
            paper = form.save()
            return redirect('teachers:paper_detail', pk=paper.pk)
    else:
        form = PaperForm()
    return render(request, 'teams/teachers/paper_form.html', {'form': form})

# 修正（Update）
def paper_update(request, pk):
    paper = get_object_or_404(Paper, pk=pk)
    if request.method == 'POST':
        form = PaperForm(request.POST, request.FILES, instance=paper)
        if form.is_valid():
            form.save()
            return redirect('teachers:paper_detail', pk=paper.pk)
    else:
        form = PaperForm(instance=paper)
    return render(request, 'teams/teachers/paper_form.html', {'form': form, 'paper': paper})

# 削除（Delete）
def paper_delete(request, pk):
    paper = get_object_or_404(Paper, pk=pk)
    if request.method == 'POST':
        paper.delete()
        return redirect('teachers:paper_list')
    return render(request, 'teams/teachers/paper_confirm_delete.html', {'paper': paper})

# 検索
def paper_search(request):
    query = request.GET.get('q', '')

    # 一覧と同じ sort 設定
    sort_map = {
        'title': 'title',
        'author': 'author',
        'year': 'year',
        'booktitle': 'booktitle',
        'submitter': 'submitter',
        'submit_time': 'submit_time',
    }

    sort_key = request.GET.get('sort', 'year')
    direction = request.GET.get('dir', 'desc')

    order_field = sort_map.get(sort_key, 'year')
    if direction == 'desc':
        order_field = '-' + order_field

    results = Paper.objects.all()

    if query:
        results = results.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(booktitle__icontains=query) |
            Q(keywords__icontains=query) |
            Q(year__icontains=query) |
            Q(submitter__icontains=query) |
            Q(submit_time__icontains=query) |
            Q(imp_overview__icontains=query) |
            Q(imp_comparison__icontains=query) |
            Q(imp_idea__icontains=query) |
            Q(imp_usefulness__icontains=query) |
            Q(imp_discussion__icontains=query) |
            Q(imp_relation__icontains=query) |
            Q(note__icontains=query)
        )

    results = results.order_by(order_field, 'title')

    context = {
        'query': query,
        'results': results,
        'sort': sort_key,
        'dir': direction,
    }
    return render(request, 'teams/teachers/paper_search.html', context)

