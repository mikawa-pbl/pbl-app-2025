from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import TakenokoSignupForm
from .models import TakenokoUser

SESSION_KEY = "takenoko_user_id"


def get_current_user(request):
    user_id = request.session.get(SESSION_KEY)
    if not user_id:
        return None
    try:
        return TakenokoUser.objects.get(user_id=user_id)
    except TakenokoUser.DoesNotExist:
        return None


def takenoko_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not get_current_user(request):
            messages.error(request, "ログインしてください。")
            return redirect("takenoko:login")
        return view_func(request, *args, **kwargs)
    return wrapper


def main(request):
    return render(request, 'teams/takenoko/main.html')

def purchased_items(request):
    return render(request, 'teams/takenoko/purchased_items.html')

def listing_items(request):
    return render(request, 'teams/takenoko/listing_items.html')

def product_details(request):
    return render(request, 'teams/takenoko/product_details.html')

def login(request):
    # すでにログイン済みならメインページへリダイレクト
    if get_current_user(request):
        return redirect("takenoko:main")

    if request.method == "POST":
        email = (request.POST.get("email") or "").strip().lower()
        password = request.POST.get("pass") or ""
        try:
            user = TakenokoUser.objects.get(email__iexact=email)
            if user.check_password(password):
                request.session[SESSION_KEY] = user.user_id
                messages.success(request, "ログインしました。")
                return redirect("takenoko:main")
            else:
                messages.error(request, "メールアドレスまたはパスワードが違います。")
        except TakenokoUser.DoesNotExist:
            messages.error(request, "メールアドレスまたはパスワードが違います。")

    return render(request, 'teams/takenoko/login.html')

def signup(request):
    if request.method == "POST":
        form = TakenokoSignupForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "ユーザー登録が完了しました。")
            return redirect("takenoko:login")
        else:
            messages.error(request, "入力内容を確認してください。")
    else:
        form = TakenokoSignupForm()
    return render(request, 'teams/takenoko/signup.html', {"form": form})

@takenoko_login_required
def item_create(request):
    return render(request, 'teams/takenoko/item_create.html')

def create_complete(request):
    return render(request, 'teams/takenoko/create_complete.html')

def start_trading(request):
    return render(request, 'teams/takenoko/start_trading.html')

def item_delete(request):
    return render(request, 'teams/takenoko/item_delete.html')

def item_edit(request):
    return render(request, 'teams/takenoko/item_edit.html')

def edit_complete(request):
    return render(request, 'teams/takenoko/edit_complete.html')

def logout(request):
    if SESSION_KEY in request.session:
        request.session.pop(SESSION_KEY, None)
    messages.success(request, "ログアウトしました。")
    return redirect("takenoko:main")