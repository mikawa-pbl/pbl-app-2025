from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .doors import DOORS
from .forms import EntryForm
from .models import Entry


def index(request):
    return render(
        request,
        "teams/h34vvy_u53rzz/index.html",
        {
            "nav_active": "index",
        },
    )


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
            return redirect("h34vvy_u53rzz:waiting", entry_id=entry.pk)
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
            "nav_active": "help",
        },
    )


def waiting_view(request, entry_id):
    entry = get_object_or_404(Entry, pk=entry_id)
    return render(
        request,
        "teams/h34vvy_u53rzz/waiting.html",
        {
            "entry": entry,
            "nav_active": None,
        },
    )


def waiting_status(request, entry_id):
    entry = get_object_or_404(Entry, pk=entry_id)
    return JsonResponse(
        {
            "helper_confirmed": entry.helper_confirmed_at is not None,
            "helper_confirmed_at": entry.helper_confirmed_at.isoformat()
            if entry.helper_confirmed_at
            else None,
        }
    )


def timeline_view(request):
    if request.method == "POST":
        entry_id = request.POST.get("entry_id")
        if entry_id:
            entry = get_object_or_404(Entry, pk=entry_id)
            if entry.helper_confirmed_at is None:
                entry.helper_confirmed_at = timezone.now()
                entry.save(update_fields=["helper_confirmed_at"])
        return redirect("h34vvy_u53rzz:timeline")
    entries = Entry.objects.all()  # Meta.ordering で新しい順
    return render(
        request,
        "teams/h34vvy_u53rzz/timeline.html",
        {
            "entries": entries,
            "nav_active": "timeline",
        },
    )
