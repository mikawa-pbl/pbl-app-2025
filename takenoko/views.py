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

    # すでに別の人と交渉中の場合は弾く
    if item.status == 'negotiation' and item.buyer and item.buyer != current_user:
        messages.error(request, "この商品は現在ほかのユーザーと交渉中です。")
        return redirect(f"/takenoko/product_details/?id={item_id}")

    # 売り切れは開始できない
    if item.status == 'sold':
        messages.error(request, "この商品は売り切れです。")
        return redirect(f"/takenoko/product_details/?id={item_id}")

    # アクティブなら交渉中に切り替え、buyer 記録
    if item.status == 'active':
        item.status = 'negotiation'
        item.buyer = current_user
        item.save(update_fields=['status', 'buyer'])
        messages.success(request, "取引開始しました。")
    elif item.status == 'negotiation' and not item.buyer:
        item.buyer = current_user
        item.save(update_fields=['buyer'])

    # 画面を表示（同じ購入者が再訪問した場合もここに来る）
    return render(request, 'teams/takenoko/start_trading.html', {
        "item": item,
        "seller": item.seller,
        "current_user": current_user
    })

@takenoko_login_required
def item_delete(request):
    item_id = request.GET.get("id")
    if not item_id:
        messages.error(request, "商品が見つかりません。")
        return redirect("takenoko:listing_items")

    user = get_current_user(request)
    item = Item.objects.filter(pk=item_id, seller=user).first()
    if not item:
        messages.error(request, "この商品が見つからないか、操作権限がありません。")
        return redirect("takenoko:listing_items")

    if request.method == "POST":
        item.delete()
        messages.success(request, "商品を削除しました。")
        return redirect("takenoko:listing_items")

    return render(request, "teams/takenoko/item_delete.html", {"item": item})

@takenoko_login_required
def item_edit(request):
    item_id = request.GET.get("id")
    if not item_id:
        messages.error(request, "商品が見つかりません。")
        return redirect("takenoko:listing_items")

    user = get_current_user(request)
    item = Item.objects.filter(pk=item_id, seller=user).first()
    if not item:
        messages.error(request, "この商品が見つからないか、操作権限がありません。")
        return redirect("takenoko:listing_items")

    if request.method == "POST":
        form = ItemCreateForm(request.POST, instance=item)
        new_images = request.FILES.getlist('images')
        delete_ids = request.POST.getlist('delete_images')

        # 画像枚数チェック（削除後の残数 + 追加 <= 5）
        remaining = item.images.exclude(id__in=delete_ids).count()
        if remaining + len(new_images) > 5:
            messages.error(request, "画像は最大5枚までです。")
            return render(request, "teams/takenoko/item_edit.html", {
                "form": form,
                "item": item,
                "selected_grades": request.POST.getlist('grades'),
                "selected_tags": request.POST.getlist('tags'),
                "delete_images": request.POST.getlist('delete_images'),
            })

        # バリデーション（任意）
        image_errors = []
        for img in new_images:
            if img.size > 5 * 1024 * 1024:
                image_errors.append(f"{img.name}: 5MB以下にしてください。")
            if not getattr(img, "content_type", "").startswith("image/"):
                image_errors.append(f"{img.name}: 画像ファイルのみアップロード可能です。")
        if image_errors:
            for e in image_errors:
                messages.error(request, e)
            return render(request, "teams/takenoko/item_edit.html", {
                "form": form,
                "item": item,
                "selected_grades": request.POST.getlist('grades'),
                "selected_tags": request.POST.getlist('tags'),
                "delete_images": request.POST.getlist('delete_images'),
            })

        if form.is_valid():
            item = form.save(commit=False)
            item.seller = user
            item.save()

            # 学年
            item.target_grades.clear()
            for code in request.POST.getlist('grades'):
                grade = TargetGrade.objects.filter(code=code).first()
                if grade:
                    item.target_grades.add(grade)

            # タグ
            item.tags.clear()
            for name in request.POST.getlist('tags'):
                tag = Tag.objects.filter(name=name).first()
                if tag:
                    item.tags.add(tag)

            # 画像削除
            if delete_ids:
                item.images.filter(id__in=delete_ids).delete()

            # 画像追加（連番付け直し）
            current = list(item.images.order_by('order'))
            order_start = 1
            for existing in current:
                existing.order = order_start
                existing.save(update_fields=['order'])
                order_start += 1
            for img in new_images:
                ItemImage.objects.create(item=item, image=img, order=order_start)
                order_start += 1

            messages.success(request, "商品を更新しました。")
            return redirect(f"/takenoko/item_delete/?id={item.pk}")
        else:
            messages.error(request, "入力内容を確認してください。")
    else:
        initial = {
            "grades": list(item.target_grades.values_list("code", flat=True)),
            "tags": list(item.tags.values_list("name", flat=True)),
        }
        form = ItemCreateForm(instance=item, initial=initial)

    return render(request, "teams/takenoko/item_edit.html", {
        "form": form,
        "item": item,
        "selected_grades": request.POST.getlist('grades') if request.method == "POST" else list(item.target_grades.values_list("code", flat=True)),
        "selected_tags": request.POST.getlist('tags') if request.method == "POST" else list(item.tags.values_list("name", flat=True)),
        "delete_images": request.POST.getlist('delete_images') if request.method == "POST" else [],
    })

@takenoko_login_required
def edit_complete(request):
    return render(request, 'teams/takenoko/edit_complete.html')

@takenoko_login_required
def toggle_item_status(request):
    """
    出品者がステータスを切り替え（'negotiation' → 'active' または 'sold'）
    POST リクエスト必須
    """
    if request.method != 'POST':
        return redirect("takenoko:main")
    
    item_id = request.POST.get('item_id')
    new_status = request.POST.get('status')  # 'active' または 'sold'
    
    if not item_id or new_status not in ['active', 'sold']:
        messages.error(request, "不正なリクエストです。")
        return redirect("takenoko:listing_items")
    
    user = get_current_user(request)
    item = Item.objects.filter(pk=item_id, seller=user).first()
    
    if not item:
        messages.error(request, "この商品が見つからないか、操作権限がありません。")
        return redirect("takenoko:listing_items")
    
    # 'negotiation' ステータスからのみ変更可能
    if item.status != 'negotiation':
        messages.error(request, "交渉中の商品のみステータスを変更できます。")
        return redirect(f"/takenoko/item_delete/?id={item_id}")
    
    # ステータス変更
    item.status = new_status
    
    # 'sold' にする場合、sold_at を記録
    if new_status == 'sold':
        from django.utils import timezone
        item.sold_at = timezone.now()
    
    # 'active' に戻す場合、buyer を削除
    if new_status == 'active':
        item.buyer = None
        item.sold_at = None
    
    item.save()
    
    if new_status == 'sold':
        messages.success(request, "商品を売却確定しました。")
    else:
        messages.success(request, "商品を販売再開しました。")
    
    return redirect(f"/takenoko/item_delete/?id={item_id}")

@takenoko_login_required
def logout(request):
    if SESSION_KEY in request.session:
        request.session.pop(SESSION_KEY, None)
    messages.success(request, "ログアウトしました。")
    return redirect("takenoko:main")
