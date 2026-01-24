"""
Team Tansaibou POS システムのビューモジュール

このモジュールは以下の機能を提供します:
- 販売登録（POSレジ機能）
- 商品管理（CRUD操作）
- セット商品管理（CRUD操作）
- 販売履歴表示

設計方針:
- マルチデータベース対応（'team_tansaibou' データベースを使用）
- 独自認証（Django authに依存しない）
- トランザクション管理（在庫減算の一貫性保証）
- エラーハンドリング（ユーザーフレンドリーなメッセージ）
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction as db_transaction
from django.utils import timezone
from decimal import Decimal
from functools import wraps

from .models import Store, Member, Product, ProductSet, ProductSetItem, Transaction, TransactionItem

DB = 'team_tansaibou'
LOGIN_URL = 'team_tansaibou:login'
SESSION_KEY = 'tansaibou_store_id'


def get_current_store(request):
    """現在のログイン店舗を取得"""
    store_id = request.session.get(SESSION_KEY)
    if not store_id:
        return None
    try:
        return Store.objects.using(DB).get(id=store_id, is_active=True)
    except Store.DoesNotExist:
        return None


def tansaibou_login_required(view_func):
    """team_tansaibou用のログイン必須デコレータ"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        store = get_current_store(request)
        if not store:
            messages.warning(request, 'ログインが必要です')
            return redirect(LOGIN_URL)
        request.current_store = store
        return view_func(request, *args, **kwargs)
    return wrapper


# ===== 認証機能 =====

def signup(request):
    """店舗登録（サインアップ）"""
    if get_current_store(request):
        return redirect('team_tansaibou:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        store_name = request.POST.get('store_name', '').strip()
        description = request.POST.get('description', '').strip()

        errors = []
        if not username:
            errors.append('ログインIDを入力してください')
        elif len(username) < 3:
            errors.append('ログインIDは3文字以上で入力してください')
        elif Store.objects.using(DB).filter(username=username).exists():
            errors.append('このログインIDは既に使用されています')

        if not password1:
            errors.append('パスワードを入力してください')
        elif len(password1) < 4:
            errors.append('パスワードは4文字以上で入力してください')
        elif password1 != password2:
            errors.append('パスワードが一致しません')

        if not store_name:
            errors.append('店舗名を入力してください')

        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            store = Store(
                username=username,
                name=store_name,
                description=description
            )
            store.set_password(password1)
            store.save(using=DB)
            request.session[SESSION_KEY] = store.id
            messages.success(request, f'店舗「{store.name}」を登録しました！')
            return redirect('team_tansaibou:dashboard')

    return render(request, 'teams/team_tansaibou/auth/signup.html')


def login_view(request):
    """ログイン"""
    if get_current_store(request):
        return redirect('team_tansaibou:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        try:
            store = Store.objects.using(DB).get(username=username, is_active=True)
            if store.check_password(password):
                request.session[SESSION_KEY] = store.id
                messages.success(request, 'ログインしました')
                next_url = request.GET.get('next', 'team_tansaibou:dashboard')
                return redirect(next_url)
            else:
                messages.error(request, 'パスワードが正しくありません')
        except Store.DoesNotExist:
            messages.error(request, 'ログインIDが見つかりません')

    return render(request, 'teams/team_tansaibou/auth/login.html')


def logout_view(request):
    """ログアウト"""
    if request.method == 'POST':
        if SESSION_KEY in request.session:
            del request.session[SESSION_KEY]
        messages.success(request, 'ログアウトしました')
    return redirect('team_tansaibou:login')


@tansaibou_login_required
def dashboard(request):
    """ダッシュボード"""
    store = request.current_store
    return render(request, 'teams/team_tansaibou/auth/dashboard.html', {'store': store})


# ===== POS機能 =====

@tansaibou_login_required
def index(request):
    return redirect('team_tansaibou:register_sale')


@tansaibou_login_required
def member_list(request):
    """担当者一覧"""
    store = request.current_store
    members = Member.objects.using(DB).filter(store=store).order_by('student_id', 'name')
    context = {
        'store': store,
        'members': members,
    }
    return render(request, 'teams/team_tansaibou/member_list.html', context)


@tansaibou_login_required
def member_add(request):
    """担当者登録"""
    store = request.current_store
    if request.method == 'POST':
        try:
            name = request.POST.get('name', '').strip()
            student_id = request.POST.get('student_id', '').strip()
            email = request.POST.get('email', '').strip()

            if not name:
                messages.error(request, '名前を入力してください')
            else:
                Member.objects.using(DB).create(
                    store=store,
                    name=name,
                    student_id=student_id,
                    email=email
                )
                messages.success(request, f'担当者「{name}」を登録しました')
                return redirect('team_tansaibou:member_list')

        except Exception as e:
            messages.error(request, f'エラーが発生しました: {str(e)}')

    return render(request, 'teams/team_tansaibou/member_add.html', {'store': store})


@tansaibou_login_required
def member_edit(request, pk):
    """担当者編集"""
    store = request.current_store
    try:
        member = Member.objects.using(DB).get(id=pk, store=store)
    except Member.DoesNotExist:
        messages.error(request, '担当者が見つかりません')
        return redirect('team_tansaibou:member_list')

    if request.method == 'POST':
        try:
            name = request.POST.get('name', '').strip()
            student_id = request.POST.get('student_id', '').strip()
            email = request.POST.get('email', '').strip()

            if not name:
                messages.error(request, '名前を入力してください')
            else:
                member.name = name
                member.student_id = student_id
                member.email = email
                member.save(using=DB)
                messages.success(request, f'担当者「{name}」を更新しました')
                return redirect('team_tansaibou:member_list')

        except Exception as e:
            messages.error(request, f'エラーが発生しました: {str(e)}')

    context = {
        'store': store,
        'member': member,
    }
    return render(request, 'teams/team_tansaibou/member_edit.html', context)


@tansaibou_login_required
def member_delete(request, pk):
    """担当者削除"""
    store = request.current_store
    try:
        member = Member.objects.using(DB).get(id=pk, store=store)
    except Member.DoesNotExist:
        messages.error(request, '担当者が見つかりません')
        return redirect('team_tansaibou:member_list')

    if request.method == 'POST':
        try:
            name = member.name
            member.delete(using=DB)
            messages.success(request, f'担当者「{name}」を削除しました')
        except Exception as e:
            messages.error(request, f'この担当者は販売履歴があるため削除できません')

    return redirect('team_tansaibou:member_list')


@tansaibou_login_required
def register_sale(request):
    """販売登録画面（POSレジ）"""
    store = request.current_store
    if request.method == 'POST':
        try:
            transaction_date = request.POST.get('transaction_date')
            payment_method = request.POST.get('payment_method')
            recorded_by_id = request.POST.get('recorded_by')
            notes = request.POST.get('notes', '')
            cart_items = request.POST.get('cart_items')

            if not cart_items or cart_items == '[]':
                messages.error(request, 'カートが空です。商品を選択してください')
                raise ValueError('カートが空です')

            if not all([transaction_date, payment_method, recorded_by_id]):
                messages.error(request, '必須項目を全て入力してください')
                raise ValueError('必須項目が不足しています')

            import json
            cart_data = json.loads(cart_items)

            with db_transaction.atomic():
                total_amount = Decimal('0')
                for item in cart_data:
                    total_amount += Decimal(str(item['price'])) * int(item['quantity'])

                trans = Transaction.objects.using(DB).create(
                    transaction_date=transaction_date,
                    total_amount=total_amount,
                    recorded_by_id=recorded_by_id,
                    payment_method=payment_method,
                    notes=notes,
                    store=store
                )

                for item in cart_data:
                    item_type = item['type']
                    item_id = item['id']
                    quantity = int(item['quantity'])
                    price = Decimal(str(item['price']))

                    if item_type == 'product':
                        product = Product.objects.using(DB).get(id=item_id, store=store)
                        TransactionItem.objects.using(DB).create(
                            transaction=trans,
                            product=product,
                            quantity=quantity,
                            price_at_sale=price
                        )
                    else:
                        product_set = ProductSet.objects.using(DB).get(id=item_id, store=store)
                        TransactionItem.objects.using(DB).create(
                            transaction=trans,
                            product_set=product_set,
                            quantity=quantity,
                            price_at_sale=price
                        )

                messages.success(request, f'販売を登録しました（合計: ¥{total_amount:,}、商品数: {len(cart_data)}）')
                return redirect('team_tansaibou:register_sale')

        except json.JSONDecodeError:
            messages.error(request, 'カートデータの形式が不正です')
        except Product.DoesNotExist:
            messages.error(request, '選択した商品が見つかりません')
        except ProductSet.DoesNotExist:
            messages.error(request, '選択した商品セットが見つかりません')
        except ValueError as e:
            pass  # Already handled above
        except Exception as e:
            messages.error(request, f'エラーが発生しました: {str(e)}')

    context = {
        'store': store,
        'members': Member.objects.using(DB).filter(store=store),
        'products': Product.objects.using(DB).filter(store=store, is_active=True).order_by('name'),
        'product_sets': ProductSet.objects.using(DB).filter(store=store, is_active=True).order_by('name'),
        'payment_methods': Transaction.PAYMENT_METHOD_CHOICES,
        'today': timezone.now().date().isoformat(),
    }
    return render(request, 'teams/team_tansaibou/register_sale.html', context)


@tansaibou_login_required
def sale_list(request):
    """販売履歴一覧"""
    store = request.current_store
    transactions = Transaction.objects.using(DB).filter(store=store).select_related('recorded_by').prefetch_related(
        'items__product', 'items__product_set'
    ).order_by('-transaction_date', '-created_at')

    context = {
        'store': store,
        'transactions': transactions,
    }
    return render(request, 'teams/team_tansaibou/sale_list.html', context)


@tansaibou_login_required
def sale_edit(request, pk):
    """販売履歴編集"""
    store = request.current_store
    try:
        transaction = Transaction.objects.using(DB).select_related('recorded_by').get(id=pk, store=store)
    except Transaction.DoesNotExist:
        messages.error(request, '販売履歴が見つかりません')
        return redirect('team_tansaibou:sale_list')

    if request.method == 'POST':
        try:
            transaction_date = request.POST.get('transaction_date')
            payment_method = request.POST.get('payment_method')
            recorded_by_id = request.POST.get('recorded_by')
            notes = request.POST.get('notes', '')

            if not all([transaction_date, payment_method, recorded_by_id]):
                messages.error(request, '必須項目を全て入力してください')
            else:
                # 編集ログを備考に追記
                now = timezone.localtime(timezone.now())
                editor = Member.objects.using(DB).get(id=recorded_by_id)
                edit_log = f"\n[{now.strftime('%m/%d %H:%M')} {editor.name}により編集]"

                transaction.transaction_date = transaction_date
                transaction.payment_method = payment_method
                transaction.recorded_by_id = recorded_by_id
                transaction.notes = notes + edit_log
                transaction.save(using=DB)

                messages.success(request, '販売履歴を更新しました')
                return redirect('team_tansaibou:sale_list')

        except Member.DoesNotExist:
            messages.error(request, '担当者が見つかりません')
        except Exception as e:
            messages.error(request, f'エラーが発生しました: {str(e)}')

    context = {
        'store': store,
        'transaction': transaction,
        'members': Member.objects.using(DB).filter(store=store),
        'payment_methods': Transaction.PAYMENT_METHOD_CHOICES,
    }
    return render(request, 'teams/team_tansaibou/sale_edit.html', context)


# ===== 商品管理 =====

@tansaibou_login_required
def product_list(request):
    """商品一覧"""
    store = request.current_store
    products = Product.objects.using(DB).filter(store=store).order_by('name')
    context = {
        'store': store,
        'products': products,
    }
    return render(request, 'teams/team_tansaibou/product_list.html', context)


@tansaibou_login_required
def product_add(request):
    """商品登録"""
    store = request.current_store
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            current_price = request.POST.get('current_price')
            stock = request.POST.get('stock', 0)
            description = request.POST.get('description', '')
            is_active = request.POST.get('is_active') == 'on'

            Product.objects.using(DB).create(
                name=name,
                current_price=current_price,
                stock=stock,
                description=description,
                is_active=is_active,
                store=store
            )

            messages.success(request, f'商品「{name}」を登録しました')
            return redirect('team_tansaibou:product_list')

        except Exception as e:
            messages.error(request, f'エラーが発生しました: {str(e)}')

    return render(request, 'teams/team_tansaibou/product_add.html', {'store': store})


@tansaibou_login_required
def product_edit(request, product_id):
    """商品編集"""
    store = request.current_store
    try:
        product = Product.objects.using(DB).get(id=product_id, store=store)
    except Product.DoesNotExist:
        messages.error(request, '商品が見つかりません')
        return redirect('team_tansaibou:product_list')

    if request.method == 'POST':
        try:
            product.name = request.POST.get('name')
            product.current_price = request.POST.get('current_price')
            product.stock = request.POST.get('stock')
            product.description = request.POST.get('description', '')
            product.is_active = request.POST.get('is_active') == 'on'
            product.save(using=DB)

            messages.success(request, f'商品「{product.name}」を更新しました')
            return redirect('team_tansaibou:product_list')

        except Exception as e:
            messages.error(request, f'エラーが発生しました: {str(e)}')

    context = {
        'store': store,
        'product': product,
    }
    return render(request, 'teams/team_tansaibou/product_edit.html', context)


@tansaibou_login_required
def product_restock(request, product_id):
    """在庫補充"""
    store = request.current_store
    try:
        product = Product.objects.using(DB).get(id=product_id, store=store)
    except Product.DoesNotExist:
        messages.error(request, '商品が見つかりません')
        return redirect('team_tansaibou:product_list')

    if request.method == 'POST':
        try:
            add_quantity = int(request.POST.get('add_quantity', 0))
            if add_quantity > 0:
                product.stock += add_quantity
                product.save(using=DB)
                messages.success(request, f'商品「{product.name}」の在庫を{add_quantity}個追加しました（合計: {product.stock}個）')
            else:
                messages.error(request, '追加数量は1以上を指定してください')

            return redirect('team_tansaibou:product_list')

        except Exception as e:
            messages.error(request, f'エラーが発生しました: {str(e)}')

    context = {
        'store': store,
        'product': product,
    }
    return render(request, 'teams/team_tansaibou/product_restock.html', context)


# ===== セット商品管理 =====

@tansaibou_login_required
def productset_list(request):
    """セット商品一覧"""
    store = request.current_store
    product_sets = ProductSet.objects.using(DB).filter(store=store).prefetch_related('items__product').order_by('name')
    context = {
        'store': store,
        'product_sets': product_sets,
    }
    return render(request, 'teams/team_tansaibou/productset_list.html', context)


@tansaibou_login_required
def productset_add(request):
    """セット商品登録"""
    store = request.current_store
    if request.method == 'POST':
        try:
            with db_transaction.atomic():
                name = request.POST.get('name')
                price = request.POST.get('price')
                description = request.POST.get('description', '')
                is_active = request.POST.get('is_active') == 'on'

                product_set = ProductSet.objects.using(DB).create(
                    name=name,
                    price=price,
                    description=description,
                    is_active=is_active,
                    store=store
                )

                product_ids = request.POST.getlist('product_id[]')
                quantities = request.POST.getlist('quantity[]')

                for product_id, quantity in zip(product_ids, quantities):
                    if product_id and quantity:
                        ProductSetItem.objects.using(DB).create(
                            product_set=product_set,
                            product_id=product_id,
                            quantity=int(quantity)
                        )

                messages.success(request, f'セット商品「{name}」を登録しました')
                return redirect('team_tansaibou:productset_list')

        except Exception as e:
            messages.error(request, f'エラーが発生しました: {str(e)}')

    products = Product.objects.using(DB).filter(store=store, is_active=True).order_by('name')
    context = {
        'store': store,
        'products': products,
    }
    return render(request, 'teams/team_tansaibou/productset_add.html', context)


@tansaibou_login_required
def productset_edit(request, productset_id):
    """セット商品編集"""
    store = request.current_store
    try:
        product_set = ProductSet.objects.using(DB).prefetch_related('items__product').get(id=productset_id, store=store)
    except ProductSet.DoesNotExist:
        messages.error(request, 'セット商品が見つかりません')
        return redirect('team_tansaibou:productset_list')

    if request.method == 'POST':
        try:
            with db_transaction.atomic():
                product_set.name = request.POST.get('name')
                product_set.price = request.POST.get('price')
                product_set.description = request.POST.get('description', '')
                product_set.is_active = request.POST.get('is_active') == 'on'
                product_set.save(using=DB)

                ProductSetItem.objects.using(DB).filter(product_set=product_set).delete()

                product_ids = request.POST.getlist('product_id[]')
                quantities = request.POST.getlist('quantity[]')

                for product_id, quantity in zip(product_ids, quantities):
                    if product_id and quantity:
                        ProductSetItem.objects.using(DB).create(
                            product_set=product_set,
                            product_id=product_id,
                            quantity=int(quantity)
                        )

                messages.success(request, f'セット商品「{product_set.name}」を更新しました')
                return redirect('team_tansaibou:productset_list')

        except Exception as e:
            messages.error(request, f'エラーが発生しました: {str(e)}')

    products = Product.objects.using(DB).filter(store=store, is_active=True).order_by('name')
    context = {
        'store': store,
        'product_set': product_set,
        'products': products,
    }
    return render(request, 'teams/team_tansaibou/productset_edit.html', context)
