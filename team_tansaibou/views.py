from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction as db_transaction
from django.utils import timezone
from decimal import Decimal

from .models import Member, Product, ProductSet, Transaction, TransactionItem


def index(request):
    return render(request, 'teams/team_tansaibou/index.html')

def members(request):
    qs = Member.objects.all()
    return render(request, 'teams/team_tansaibou/members.html', {'members': qs})


def register_sale(request):
    """販売登録画面"""
    DB = 'team_tansaibou'

    if request.method == 'POST':
        try:
            # フォームデータの取得
            transaction_date = request.POST.get('transaction_date')
            payment_method = request.POST.get('payment_method')
            recorded_by_id = request.POST.get('recorded_by')
            item_type = request.POST.get('item_type')  # 'product' or 'product_set'
            item_id = request.POST.get('item_id')
            quantity = int(request.POST.get('quantity', 1))
            notes = request.POST.get('notes', '')

            # バリデーション
            if not all([transaction_date, payment_method, recorded_by_id, item_type, item_id]):
                messages.error(request, '必須項目を全て入力してください')
                raise ValueError('必須項目が不足しています')

            if quantity <= 0:
                messages.error(request, '数量は1以上を入力してください')
                raise ValueError('数量が不正です')

            # トランザクション開始
            with db_transaction.atomic():
                # 商品情報の取得
                if item_type == 'product':
                    item = Product.objects.using(DB).get(id=item_id)
                    price = item.current_price
                else:  # product_set
                    item = ProductSet.objects.using(DB).get(id=item_id)
                    price = item.price

                # 合計金額の計算
                total_amount = price * quantity

                # Transactionの作成
                trans = Transaction.objects.using(DB).create(
                    transaction_date=transaction_date,
                    total_amount=total_amount,
                    recorded_by_id=recorded_by_id,
                    payment_method=payment_method,
                    notes=notes
                )

                # TransactionItemの作成（在庫チェックと減少は自動で行われる）
                if item_type == 'product':
                    TransactionItem.objects.using(DB).create(
                        transaction=trans,
                        product=item,
                        quantity=quantity,
                        price_at_sale=price
                    )
                else:
                    TransactionItem.objects.using(DB).create(
                        transaction=trans,
                        product_set=item,
                        quantity=quantity,
                        price_at_sale=price
                    )

                messages.success(request, f'販売を登録しました（合計: ¥{total_amount:,}）')
                return redirect('team_tansaibou:sale_list')

        except Product.DoesNotExist:
            messages.error(request, '選択した商品が見つかりません')
        except ProductSet.DoesNotExist:
            messages.error(request, '選択した商品セットが見つかりません')
        except ValueError as e:
            messages.error(request, f'在庫が不足しています: {str(e)}')
        except Exception as e:
            messages.error(request, f'エラーが発生しました: {str(e)}')

    # GETリクエストまたはエラー時: フォーム表示
    context = {
        'members': Member.objects.using(DB).all(),
        'products': Product.objects.using(DB).filter(is_active=True),
        'product_sets': ProductSet.objects.using(DB).filter(is_active=True),
        'payment_methods': Transaction.PAYMENT_METHODS,
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