from django.shortcuts import redirect, render

from .doors import DOORS
from .forms import EntryForm
from .models import Entry


def index(request):
    return render(request, "teams/h34vvy_u53rzz/index.html")


def help(request):
    doors_by_id = {door.id: door for door in DOORS}
    selected_door_id = None

    if request.method == "POST":
        form = EntryForm(request.POST)
        selected_door_id = request.POST.get("door_id")
        selected_door = doors_by_id.get(selected_door_id)
        is_valid = form.is_valid()
        if not selected_door:
            form.add_error(None, "ドアが選択されていません。")
        if is_valid and selected_door:
            entry = form.save(commit=False)
            entry.door_id = selected_door.id
            entry.save()
            return redirect("h34vvy_u53rzz:help")
    else:
        form = EntryForm()
        selected_door = None

    return render(
        request,
        "teams/h34vvy_u53rzz/help.html",
        {
            "doors": DOORS,
            "form": form,
            "selected_door": selected_door,
            "entries": Entry.objects.all(),
        },
    )


def timeline_view(request):
    if request.method == "POST":
        form = EntryForm(request.POST)
        if form.is_valid():
            form.save()  # created_at は auto_now_add で自動
            return redirect(".")  # F5連打での二重投稿防止
    else:
        form = EntryForm()

    entries = Entry.objects.all()  # Meta.ordering で新しい順
    return render(
        request,
        "teams/h34vvy_u53rzz/timeline.html",
        {
            "form": form,
            "entries": entries,
        },
    )
