from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import TakenokoSignupForm, ItemCreateForm
from .models import TakenokoUser, Item, ItemImage, TargetGrade, Tag

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
    # GETパラメータからタグを取得
    selected_tag = request.GET.get('tag')
    
    # アクティブな商品を取得（新着順）
    items = Item.objects.filter(status='active').order_by('-created_at')
    
    # タグでフィルタリング
    if selected_tag:
        items = items.filter(tags__name=selected_tag).distinct()
    
    items = items[:12]
    
    # 登録されているすべてのタグを取得
    tags = Tag.objects.all()
    
    return render(request, 'teams/takenoko/main.html', {
        "items": items,
        "tags": tags,
        "selected_tag": selected_tag
    })

def purchased_items(request):
    return render(request, 'teams/takenoko/purchased_items.html')

@takenoko_login_required
def listing_items(request):
    user = get_current_user(request)
    # ログインユーザーが出品した商品を取得（新着順）
    items = Item.objects.filter(seller=user).order_by('-created_at')
    return render(request, 'teams/takenoko/listing_items.html', {"items": items})

def product_details(request):
    item_id = request.GET.get('id')
    if not item_id:
        messages.error(request, "商品が見つかりません。")
        return redirect("takenoko:main")
    item = get_object_or_404(Item, pk=item_id)
    return render(request, 'teams/takenoko/product_details.html', {"item": item})

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
    user = get_current_user(request)
    
    if request.method == "POST":
        form = ItemCreateForm(request.POST)
        images = request.FILES.getlist('images')
        image_errors = form.validate_images(images) if images else []
        
        if form.is_valid() and not image_errors:
            item = form.save(commit=False)
            item.seller = user
            item.status = 'active'
            item.save()

            # 対象学年
            grades = request.POST.getlist('grades')
            for grade_code in grades:
                try:
                    grade = TargetGrade.objects.get(code=grade_code)
                    item.target_grades.add(grade)
                except TargetGrade.DoesNotExist:
                    pass

            # タグ
            tags = request.POST.getlist('tags')
            for tag_name in tags:
                try:
                    tag = Tag.objects.get(name=tag_name)
                    item.tags.add(tag)
                except Tag.DoesNotExist:
                    pass

            # 画像
            for order, image in enumerate(images, start=1):
                ItemImage.objects.create(item=item, image=image, order=order)

            messages.success(request, "商品を出品しました。")
            return redirect("takenoko:create_complete")
        else:
            if image_errors:
                for error in image_errors:
                    messages.error(request, error)
            if form.errors:
                messages.error(request, "入力内容を確認してください。")
            # ここで再選択値を渡す
            return render(request, 'teams/takenoko/item_create.html', {
                "form": form,
                "selected_grades": request.POST.getlist('grades'),
                "selected_tags": request.POST.getlist('tags'),
            })
    else:
        form = ItemCreateForm()
    
    return render(request, 'teams/takenoko/item_create.html', {
        "form": form,
        "selected_grades": [],
        "selected_tags": [],
    })

@takenoko_login_required
def create_complete(request):
    return render(request, 'teams/takenoko/create_complete.html')

@takenoko_login_required
def start_trading(request):
    item_id = request.GET.get('id')
    if not item_id:
        messages.error(request, "商品が見つかりません。")
        return redirect("takenoko:main")
    
    item = get_object_or_404(Item, pk=item_id)
    current_user = get_current_user(request)
    
    # 自分の商品は取引開始できない
    if item.seller == current_user:
        messages.error(request, "自分の商品は取引開始できません。")
        return redirect(f"/takenoko/product_details/?id={item_id}")
    
    return render(request, 'teams/takenoko/start_trading.html', {
        "item": item,
        "seller": item.seller,
        "current_user": current_user
    })

@takenoko_login_required
def item_delete(request):
    return render(request, 'teams/takenoko/item_delete.html')

@takenoko_login_required
def item_edit(request):
    return render(request, 'teams/takenoko/item_edit.html')

@takenoko_login_required
def edit_complete(request):
    return render(request, 'teams/takenoko/edit_complete.html')

@takenoko_login_required
def logout(request):
    if SESSION_KEY in request.session:
        request.session.pop(SESSION_KEY, None)
    messages.success(request, "ログアウトしました。")
    return redirect("takenoko:main")