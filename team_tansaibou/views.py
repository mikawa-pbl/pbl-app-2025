"""
Team Tansaibou POS システムのビューモジュール

このモジュールは以下の機能を提供します:
- 販売登録（POSレジ機能）
- 商品管理（CRUD操作）
- セット商品管理（CRUD操作）
- 販売履歴表示

設計方針:
- マルチデータベース対応（'team_tansaibou' データベースを使用）
- トランザクション管理（在庫減算の一貫性保証）
- エラーハンドリング（ユーザーフレンドリーなメッセージ）
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db import transaction as db_transaction
from django.utils import timezone
from decimal import Decimal
from functools import wraps

from .models import Store, Member, Product, ProductSet, ProductSetItem, Transaction, TransactionItem
from .forms import StoreSignUpForm, StoreLoginForm

DB = 'team_tansaibou'
LOGIN_URL = 'team_tansaibou:login'


def get_current_store(request):
    """現在のログインユーザーの店舗を取得"""
    if not request.user.is_authenticated:
        return None
    try:
        return Store.objects.using(DB).get(user_id=request.user.id)
    except Store.DoesNotExist:
        return None


def tansaibou_login_required(view_func):
    """team_tansaibou用のログイン必須デコレータ"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'ログインが必要です')
            return redirect(LOGIN_URL)
        return view_func(request, *args, **kwargs)
    return wrapper


# ===== 認証機能 =====

def signup(request):
    """店舗登録（サインアップ）"""
    if request.user.is_authenticated:
        return redirect('team_tansaibou:dashboard')

    if request.method == 'POST':
        form = StoreSignUpForm(request.POST)
        if form.is_valid():
            user = form.save(using=DB)
            login(request, user)
            store = Store.objects.using(DB).get(user_id=user.id)
            messages.success(request, f'店舗「{store.name}」を登録しました！')
            return redirect('team_tansaibou:dashboard')
    else:
        form = StoreSignUpForm()

    return render(request, 'teams/team_tansaibou/auth/signup.html', {'form': form})


def login_view(request):
    """ログイン"""
    if request.user.is_authenticated:
        return redirect('team_tansaibou:dashboard')

    if request.method == 'POST':
        form = StoreLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'ログインしました')
            next_url = request.GET.get('next', 'team_tansaibou:dashboard')
            return redirect(next_url)
    else:
        form = StoreLoginForm()

    return render(request, 'teams/team_tansaibou/auth/login.html', {'form': form})


def logout_view(request):
    """ログアウト"""
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'ログアウトしました')
    return redirect('team_tansaibou:login')


@tansaibou_login_required
def dashboard(request):
    """ダッシュボード"""
    store = get_current_store(request)
    return render(request, 'teams/team_tansaibou/auth/dashboard.html', {'store': store})


# ===== POS機能 =====

@tansaibou_login_required
def index(request):
    return redirect('team_tansaibou:register_sale')


@tansaibou_login_required
def members(request):
    store = get_current_store(request)
    qs = Member.objects.using(DB).filter(store=store)
    return render(request, 'teams/team_tansaibou/members.html', {'members': qs})


@tansaibou_login_required
def register_sale(request):
    """販売登録画面（POSレジ）"""
    store = get_current_store(request)
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
                return redirect('team_tansaibou:sale_list')

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
    store = get_current_store(request)
    transactions = Transaction.objects.using(DB).filter(store=store).select_related('recorded_by').prefetch_related(
        'items__product', 'items__product_set'
    ).order_by('-transaction_date', '-created_at')

    context = {
        'transactions': transactions,
    }
    return render(request, 'teams/team_tansaibou/sale_list.html', context)


# ===== 商品管理 =====

@tansaibou_login_required
def product_list(request):
    """商品一覧"""
    store = get_current_store(request)
    products = Product.objects.using(DB).filter(store=store).order_by('name')
    context = {
        'products': products,
    }
    return render(request, 'teams/team_tansaibou/product_list.html', context)


@tansaibou_login_required
def product_add(request):
    """商品登録"""
    store = get_current_store(request)
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            current_price = request.POST.get('current_price')
            stock = request.POST.get('stock', 0)
            description = request.POST.get('description', '')
            is_active = request.POST.get('is_active') == 'on'

            Product.objects.using(DB_NAME).create(
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

    return render(request, 'teams/team_tansaibou/product_add.html')


@tansaibou_login_required
def product_edit(request, product_id):
    """商品編集"""
    store = get_current_store(request)
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
            product.save(using=DB_NAME)

            messages.success(request, f'商品「{product.name}」を更新しました')
            return redirect('team_tansaibou:product_list')

        except Exception as e:
            messages.error(request, f'エラーが発生しました: {str(e)}')

    context = {
        'product': product,
    }
    return render(request, 'teams/team_tansaibou/product_edit.html', context)


@tansaibou_login_required
def product_restock(request, product_id):
    """在庫補充"""
    store = get_current_store(request)
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
                product.save(using=DB_NAME)
                messages.success(request, f'商品「{product.name}」の在庫を{add_quantity}個追加しました（合計: {product.stock}個）')
            else:
                messages.error(request, '追加数量は1以上を指定してください')

            return redirect('team_tansaibou:product_list')

        except Exception as e:
            messages.error(request, f'エラーが発生しました: {str(e)}')

    context = {
        'product': product,
    }
    return render(request, 'teams/team_tansaibou/product_restock.html', context)


# ===== セット商品管理 =====

@tansaibou_login_required
def productset_list(request):
    """セット商品一覧"""
    store = get_current_store(request)
    product_sets = ProductSet.objects.using(DB).filter(store=store).prefetch_related('items__product').order_by('name')
    context = {
        'product_sets': product_sets,
    }
    return render(request, 'teams/team_tansaibou/productset_list.html', context)


@tansaibou_login_required
def productset_add(request):
    """セット商品登録"""
    store = get_current_store(request)
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
                        ProductSetItem.objects.using(DB_NAME).create(
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
        'products': products,
    }
    return render(request, 'teams/team_tansaibou/productset_add.html', context)


@tansaibou_login_required
def productset_edit(request, productset_id):
    """セット商品編集"""
    store = get_current_store(request)
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
                product_set.save(using=DB_NAME)

                ProductSetItem.objects.using(DB).filter(product_set=product_set).delete()

                product_ids = request.POST.getlist('product_id[]')
                quantities = request.POST.getlist('quantity[]')

                for product_id, quantity in zip(product_ids, quantities):
                    if product_id and quantity:
                        ProductSetItem.objects.using(DB_NAME).create(
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
        'product_set': product_set,
        'products': products,
    }
    return render(request, 'teams/team_tansaibou/productset_edit.html', context)
