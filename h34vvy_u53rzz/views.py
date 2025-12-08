from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme

from .doors import DOORS
from .forms import EntryForm
from .models import Entry


LOGIN_REDIRECT_FALLBACK = reverse_lazy("h34vvy_u53rzz:index")


def index(request):
    return render(
        request,
        "teams/h34vvy_u53rzz/index.html",
        {
            "nav_active": "index",
        },
    )


def _get_safe_redirect(request):
    target = request.POST.get("next") or request.GET.get("next")
    if target and url_has_allowed_host_and_scheme(target, allowed_hosts={request.get_host()}):
        return target
    return str(LOGIN_REDIRECT_FALLBACK)


def _style_auth_form(form):
    # Tailwind風の見た目を既存フォームと揃える
    base_attrs = {
        "class": "w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/40",
    }
    form.fields["username"].widget.attrs.update(
        {
            **base_attrs,
            "placeholder": "ユーザー名",
            "autocomplete": "username",
        }
    )
    form.fields["password"].widget.attrs.update(
        {
            **base_attrs,
            "placeholder": "パスワード",
            "autocomplete": "current-password",
        }
    )
    return form


def login_view(request):
    redirect_to = _get_safe_redirect(request)
    if request.user.is_authenticated:
        return redirect(redirect_to)

    if request.method == "POST":
        form = _style_auth_form(AuthenticationForm(request, data=request.POST))
        if form.is_valid():
            login(request, form.get_user())
            return redirect(redirect_to)
    else:
        form = _style_auth_form(AuthenticationForm(request))

    return render(
        request,
        "teams/h34vvy_u53rzz/login.html",
        {
            "form": form,
            "next": redirect_to,
            "nav_active": None,
        },
    )


@login_required(login_url=LOGIN_REDIRECT_FALLBACK)
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


@login_required(login_url=LOGIN_REDIRECT_FALLBACK)
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


@login_required(login_url=LOGIN_REDIRECT_FALLBACK)
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


@login_required(login_url=LOGIN_REDIRECT_FALLBACK)
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
