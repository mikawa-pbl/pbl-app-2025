from .models import Member
from django.shortcuts import render, redirect
from .models import Entry
from .forms import EntryForm

def index(request):
    return render(request, 'teams/h34vvy_u53rzz/index.html')

def help(request):
    return render(request, 'teams/h34vvy_u53rzz/help.html')

def timeline_view(request):
    if request.method == "POST":
        form = EntryForm(request.POST)
        if form.is_valid():
            form.save()  # created_at は auto_now_add で自動
            return redirect(".")  # F5連打での二重投稿防止
    else:
        form = EntryForm()

    entries = Entry.objects.all()  # Meta.ordering で新しい順
    return render(request, "teams/h34vvy_u53rzz/timeline.html", {
        "form": form,
        "entries": entries,
    })
