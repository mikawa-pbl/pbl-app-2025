from django.shortcuts import render, get_object_or_404, redirect
from .models import Paper
from .forms import PaperForm 

# Create your views here.
from .models import Member

def index(request):
    return render(request, 'teams/teachers/index.html')

def members(request):
    qs = Member.objects.using('teachers').all()  # ← shiokara DBを明示
    return render(request, 'teams/teachers/members.html', {'members': qs})

############
# 論文リスト
def paper_list(request):
    papers = Paper.objects.all().order_by('-year', 'title')
    return render(request, 'teams/teachers/paper_list.html', {'papers': papers})

############
# 論文単体
def paper_detail(request, pk):
    paper = get_object_or_404(Paper, pk=pk)
    return render(request, 'teams/teachers/paper_detail.html', {'paper': paper})

############
# 入力画面
def paper_create(request):
    if request.method == 'POST':
        form = PaperForm(request.POST)
        if form.is_valid():
            paper = form.save()
            return redirect('teachers:paper_detail', pk=paper.pk)
    else:
        form = PaperForm()
    return render(request, 'teams/teachers/paper_form.html', {'form': form})


############
# 検索画面
from django.db.models import Q

def paper_search(request):
    query = request.GET.get('q', '')
    results = Paper.objects.all()

    if query:
        results = results.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(booktitle__icontains=query) |
            Q(year__icontains=query)
        )

    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'teams/teachers/paper_search.html', context)
