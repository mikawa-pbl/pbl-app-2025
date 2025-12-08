from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme

from .doors import DOORS
from .forms import EntryForm, NamespacedLoginForm, SignupForm
from .models import AppAccount, Entry


LOGIN_REDIRECT_FALLBACK = reverse_lazy("h34vvy_u53rzz:index")
LOGIN_URL = reverse_lazy("h34vvy_u53rzz:login")


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
    form.fields["local_username"].widget.attrs.update(
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
        form = _style_auth_form(NamespacedLoginForm(request, data=request.POST))
        if form.is_valid():
            login(request, form.get_user())
            return redirect(redirect_to)
    else:
        form = _style_auth_form(NamespacedLoginForm(request))

    return render(
        request,
        "teams/h34vvy_u53rzz/login.html",
        {
            "form": form,
            "next": redirect_to,
            "nav_active": None,
        },
    )


def signup_view(request):
    redirect_to = _get_safe_redirect(request)
    if request.user.is_authenticated:
        return redirect(redirect_to)

    def style_signup(form):
        base_attrs = {
            "class": "w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/40",
        }
        form.fields["local_username"].widget.attrs.update(
            {**base_attrs, "placeholder": "アプリ内で使うユーザー名"}
        )
        form.fields["password1"].widget.attrs.update(
            {**base_attrs, "placeholder": "パスワード"}
        )
        form.fields["password2"].widget.attrs.update(
            {**base_attrs, "placeholder": "パスワード（確認）"}
        )
        return form

    if request.method == "POST":
        form = style_signup(SignupForm(request.POST))
        if form.is_valid():
            local_username = form.cleaned_data["local_username"]
            password = form.cleaned_data["password1"]
            # auth_user側のユーザー名は衝突を避けるために接頭辞を付与
            auth_username = f"h34vvy_{local_username}"
            if len(auth_username) > 150:
                form.add_error(
                    "local_username",
                    "ユーザー名が長すぎます（プレフィックス込み150文字以内）。",
                )
            else:
                UserModel = get_user_model()
                # 共有ユーザー表側の重複チェック
                if UserModel.objects.using("default").filter(username=auth_username).exists():
                    form.add_error(
                        "local_username",
                        "このユーザー名は既に使用されています。別の名前を入力してください。",
                    )
                # アプリ内ローカル名の重複チェック
                elif AppAccount.objects.using("h34vvy_u53rzz").filter(
                    app_code="h34vvy", local_username=local_username
                ).exists():
                    form.add_error(
                        "local_username",
                        "このユーザー名は既に登録されています。別の名前を入力してください。",
                    )
                else:
                    user = UserModel._default_manager.db_manager("default").create_user(
                        username=auth_username,
                        password=password,
                    )
                    try:
                        AppAccount.objects.using("h34vvy_u53rzz").create(
                            app_code="h34vvy",
                            local_username=local_username,
                            user_id=user.id,
                        )
                    except Exception:
                        # AppAccount作成に失敗したらユーザーを削除しておく
                        user.delete(using="default")
                        form.add_error(None, "登録に失敗しました。時間をおいて再度お試しください。")
                    else:
                        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
                        return redirect(redirect_to)
    else:
        form = style_signup(SignupForm())

    return render(
        request,
        "teams/h34vvy_u53rzz/signup.html",
        {
            "form": form,
            "next": redirect_to,
            "nav_active": None,
        },
    )


def logout_view(request):
    logout(request)
    return redirect(LOGIN_REDIRECT_FALLBACK)


@login_required(login_url=LOGIN_URL)
def ranking_view(request):
    accounts = list(
        AppAccount.objects.using("h34vvy_u53rzz")
        .order_by("-points", "local_username")
        .all()
    )
    rankings = []
    last_points = None
    last_rank = 0
    for idx, account in enumerate(accounts, start=1):
        if account.points == last_points:
            rank = last_rank
        else:
            rank = idx
        rankings.append({"account": account, "rank": rank})
        last_points = account.points
        last_rank = rank
    return render(
        request,
        "teams/h34vvy_u53rzz/ranking.html",
        {
            "rankings": rankings,
            "nav_active": "ranking",
            "current_user_id": request.user.id,
        },
    )


@login_required(login_url=LOGIN_URL)
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


@login_required(login_url=LOGIN_URL)
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


@login_required(login_url=LOGIN_URL)
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


@login_required(login_url=LOGIN_URL)
def timeline_view(request):
    if request.method == "POST":
        entry_id = request.POST.get("entry_id")
        if entry_id:
            entry = get_object_or_404(Entry, pk=entry_id)
            if entry.helper_confirmed_at is None:
                entry.helper_confirmed_at = timezone.now()
                entry.save(update_fields=["helper_confirmed_at"])
                # 助けたユーザーにポイントを付与
                AppAccount.objects.using("h34vvy_u53rzz").filter(
                    app_code="h34vvy", user_id=request.user.id
                ).update(points=F("points") + 1)
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
