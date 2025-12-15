# papers/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q

from .models import Paper
from .forms import PaperForm

# 一覧
def paper_list(request):
    papers = Paper.objects.all().order_by('-year', 'title')
    return render(request, 'teams/teachers/paper_list.html', {'paper': papers})

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
            paper = form.save()
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
    results = Paper.objects.all()

    if query:
        results = results.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(booktitle__icontains=query) |
            Q(doi__icontains=query) |
            Q(url__icontains=query) |
            Q(keywords__icontains=query) |
            Q(imp_overview__icontains=query) |
            Q(imp_comparison__icontains=query) |
            Q(imp_idea__icontains=query) |
            Q(imp_usefulness__icontains=query) |
            Q(imp_discussion__icontains=query) |
            Q(imp_relation__icontains=query) |
            Q(note__icontains=query)
        )

    return render(request, 'teams/teachers/paper_search.html', {
        'query': query,
        'results': results,
    })
