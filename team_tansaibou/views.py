from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction as db_transaction
from django.utils import timezone
from decimal import Decimal

from .models import Member, Product, ProductSet, ProductSetItem, Transaction, TransactionItem


def index(request):
    return render(request, 'teams/team_tansaibou/index.html')

def members(request):
    qs = Member.objects.all()
    return render(request, 'teams/team_tansaibou/members.html', {'members': qs})


def register_sale(request):
    """販売登録画面（POSレジ）"""
    DB = 'team_tansaibou'

    if request.method == 'POST':
        try:
            # フォームデータの取得
            transaction_date = request.POST.get('transaction_date')
            payment_method = request.POST.get('payment_method')
            recorded_by_id = request.POST.get('recorded_by')
            notes = request.POST.get('notes', '')

            # カート内の商品情報を取得
            cart_items = request.POST.get('cart_items')  # JSON文字列

            if not cart_items or cart_items == '[]':
                messages.error(request, 'カートが空です。商品を選択してください')
                raise ValueError('カートが空です')

            # バリデーション
            if not all([transaction_date, payment_method, recorded_by_id]):
                messages.error(request, '必須項目を全て入力してください')
                raise ValueError('必須項目が不足しています')

            # JSONをパース
            import json
            cart_data = json.loads(cart_items)

            # トランザクション開始
            with db_transaction.atomic():
                # 合計金額を計算
                total_amount = Decimal('0')
                for item in cart_data:
                    total_amount += Decimal(str(item['price'])) * int(item['quantity'])

                # Transactionの作成
                trans = Transaction.objects.using(DB).create(
                    transaction_date=transaction_date,
                    total_amount=total_amount,
                    recorded_by_id=recorded_by_id,
                    payment_method=payment_method,
                    notes=notes
                )

                # 各商品をTransactionItemとして作成
                for item in cart_data:
                    item_type = item['type']
                    item_id = item['id']
                    quantity = int(item['quantity'])
                    price = Decimal(str(item['price']))

                    if item_type == 'product':
                        product = Product.objects.using(DB).get(id=item_id)
                        TransactionItem.objects.using(DB).create(
                            transaction=trans,
                            product=product,
                            quantity=quantity,
                            price_at_sale=price
                        )
                    else:  # product_set
                        product_set = ProductSet.objects.using(DB).get(id=item_id)
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
            messages.error(request, f'エラー: {str(e)}')
        except Exception as e:
            messages.error(request, f'エラーが発生しました: {str(e)}')

    # GETリクエストまたはエラー時: フォーム表示
    context = {
        'members': Member.objects.using(DB).all(),
        'products': Product.objects.using(DB).filter(is_active=True).order_by('name'),
        'product_sets': ProductSet.objects.using(DB).filter(is_active=True).order_by('name'),
        'payment_methods': Transaction.PAYMENT_METHOD_CHOICES,
        'today': timezone.now().date().isoformat(),
    }
    return render(request, 'teams/team_tansaibou/register_sale.html', context)


def sale_list(request):
    """販売履歴一覧"""
    DB = 'team_tansaibou'

    transactions = Transaction.objects.using(DB).select_related('recorded_by').prefetch_related(
        'items__product', 'items__product_set'
    ).order_by('-transaction_date', '-created_at')

    context = {
        'transactions': transactions,
    }
    return render(request, 'teams/team_tansaibou/sale_list.html', context)


# ===== 商品管理 =====

def product_list(request):
    """商品一覧"""
    DB = 'team_tansaibou'
    products = Product.objects.using(DB).all().order_by('name')

    context = {
        'products': products,
    }
    return render(request, 'teams/team_tansaibou/product_list.html', context)


def product_add(request):
    """商品登録"""
    DB = 'team_tansaibou'

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
                is_active=is_active
            )

            messages.success(request, f'商品「{name}」を登録しました')
            return redirect('team_tansaibou:product_list')

        except Exception as e:
            messages.error(request, f'エラーが発生しました: {str(e)}')

    return render(request, 'teams/team_tansaibou/product_add.html')


def product_edit(request, product_id):
    """商品編集"""
    DB = 'team_tansaibou'

    try:
        product = Product.objects.using(DB).get(id=product_id)
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
        'product': product,
    }
    return render(request, 'teams/team_tansaibou/product_edit.html', context)


def product_restock(request, product_id):
    """在庫補充"""
    DB = 'team_tansaibou'

    try:
        product = Product.objects.using(DB).get(id=product_id)
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
        'product': product,
    }
    return render(request, 'teams/team_tansaibou/product_restock.html', context)


# ===== セット商品管理 =====

def productset_list(request):
    """セット商品一覧"""
    DB = 'team_tansaibou'
    product_sets = ProductSet.objects.using(DB).prefetch_related('items__product').all().order_by('name')

    context = {
        'product_sets': product_sets,
    }
    return render(request, 'teams/team_tansaibou/productset_list.html', context)


def productset_add(request):
    """セット商品登録"""
    DB = 'team_tansaibou'

    if request.method == 'POST':
        try:
            with db_transaction.atomic():
                # セット商品の基本情報
                name = request.POST.get('name')
                price = request.POST.get('price')
                description = request.POST.get('description', '')
                is_active = request.POST.get('is_active') == 'on'

                # セット商品を作成
                product_set = ProductSet.objects.using(DB).create(
                    name=name,
                    price=price,
                    description=description,
                    is_active=is_active
                )

                # 構成商品を追加
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

    products = Product.objects.using(DB).filter(is_active=True).order_by('name')
    context = {
        'products': products,
    }
    return render(request, 'teams/team_tansaibou/productset_add.html', context)


def productset_edit(request, productset_id):
    """セット商品編集"""
    DB = 'team_tansaibou'

    try:
        product_set = ProductSet.objects.using(DB).prefetch_related('items__product').get(id=productset_id)
    except ProductSet.DoesNotExist:
        messages.error(request, 'セット商品が見つかりません')
        return redirect('team_tansaibou:productset_list')

    if request.method == 'POST':
        try:
            with db_transaction.atomic():
                # 基本情報の更新
                product_set.name = request.POST.get('name')
                product_set.price = request.POST.get('price')
                product_set.description = request.POST.get('description', '')
                product_set.is_active = request.POST.get('is_active') == 'on'
                product_set.save(using=DB)

                # 既存の構成商品を削除
                ProductSetItem.objects.using(DB).filter(product_set=product_set).delete()

                # 新しい構成商品を追加
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

    products = Product.objects.using(DB).filter(is_active=True).order_by('name')
    context = {
        'product_set': product_set,
        'products': products,
    }
    return render(request, 'teams/team_tansaibou/productset_edit.html', context)