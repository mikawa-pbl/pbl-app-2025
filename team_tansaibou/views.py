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
from django.db import transaction as db_transaction
from django.utils import timezone
from decimal import Decimal
from functools import wraps

from .models import Member, Product, ProductSet, ProductSetItem, Transaction, TransactionItem


# チーム専用データベース名（設計方針: マルチデータベース対応）
DB_NAME = 'team_tansaibou'


def handle_errors(func):
    """
    ビュー関数用エラーハンドリングデコレータ

    設計方針:
    - エラーハンドリングロジックの共通化（DRY原則）
    - ユーザーフレンドリーなエラーメッセージ表示
    - 予期しないエラーのキャッチとログ記録

    使用例:
        @handle_errors
        def my_view(request):
            # ビュー処理
            pass
    """
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        try:
            return func(request, *args, **kwargs)
        except Exception as e:
            messages.error(request, f'エラーが発生しました: {str(e)}')
            # 本番環境ではロギング処理を追加することを推奨
            return redirect(request.META.get('HTTP_REFERER', '/'))
    return wrapper


def index(request):
    """
    旧ホーム画面（現在は使用されていません）

    注意: 現在のホーム画面は register_sale ビューに変更されています
    """
    return render(request, 'teams/team_tansaibou/index.html')


def members(request):
    """
    メンバー一覧表示

    Returns:
        HttpResponse: メンバー一覧を表示するHTMLページ

    設計方針:
    - 将来的にメンバー管理機能を追加する可能性を考慮
    """
    members_list = Member.objects.using(DB_NAME).all()
    return render(request, 'teams/team_tansaibou/members.html', {'members': members_list})


def register_sale(request):
    """
    販売登録画面（POSレジ）

    機能:
    - GET: POS画面を表示（商品ボタン、カート、会計フォーム）
    - POST: 複数商品の一括販売登録と在庫減算

    設計方針:
    - オフライン対応: JavaScriptでカート管理し、会計時のみサーバー通信
    - トランザクション保証: atomic()で在庫減算の一貫性を確保
    - 柔軟性: 個別商品とセット商品の混在購入に対応

    Args:
        request: HTTPリクエストオブジェクト
            POST時の必須パラメータ:
                - transaction_date: 取引日時（ISO形式）
                - payment_method: 支払方法
                - recorded_by: 担当者ID
                - cart_items: カート内商品のJSON配列
                    例: [{"type": "product", "id": 1, "price": 100, "quantity": 2}]

    Returns:
        HttpResponse: POS画面（GET時）または販売履歴へリダイレクト（POST成功時）

    Raises:
        ValueError: カート空、必須項目不足
        json.JSONDecodeError: カートデータ形式不正
        Product.DoesNotExist: 存在しない商品ID
        ProductSet.DoesNotExist: 存在しないセット商品ID
    """
    import json

    if request.method == 'POST':
        try:
            # フォームデータの取得
            transaction_date = request.POST.get('transaction_date')
            payment_method = request.POST.get('payment_method')
            recorded_by_id = request.POST.get('recorded_by')
            notes = request.POST.get('notes', '')
            cart_items = request.POST.get('cart_items')

            # バリデーション: カート空チェック
            if not cart_items or cart_items == '[]':
                messages.error(request, 'カートが空です。商品を選択してください')
                raise ValueError('カートが空です')

            # バリデーション: 必須項目チェック
            if not all([transaction_date, payment_method, recorded_by_id]):
                messages.error(request, '必須項目を全て入力してください')
                raise ValueError('必須項目が不足しています')

            # カートデータのパース
            cart_data = json.loads(cart_items)

            # データベーストランザクション開始（在庫減算の一貫性保証）
            with db_transaction.atomic(using=DB_NAME):
                # 合計金額を計算
                total_amount = sum(
                    Decimal(str(item['price'])) * int(item['quantity'])
                    for item in cart_data
                )

                # 販売トランザクション作成
                trans = Transaction.objects.using(DB_NAME).create(
                    transaction_date=transaction_date,
                    total_amount=total_amount,
                    recorded_by_id=recorded_by_id,
                    payment_method=payment_method,
                    notes=notes
                )

                # 各商品を取引明細として登録（在庫は TransactionItem.save() で自動減算）
                for item in cart_data:
                    item_type = item['type']
                    item_id = item['id']
                    quantity = int(item['quantity'])
                    price = Decimal(str(item['price']))

                    if item_type == 'product':
                        product = Product.objects.using(DB_NAME).get(id=item_id)
                        TransactionItem.objects.using(DB_NAME).create(
                            transaction=trans,
                            product=product,
                            quantity=quantity,
                            price_at_sale=price
                        )
                    else:  # product_set
                        product_set = ProductSet.objects.using(DB_NAME).get(id=item_id)
                        TransactionItem.objects.using(DB_NAME).create(
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
        'members': Member.objects.using(DB_NAME).all(),
        'products': Product.objects.using(DB_NAME).filter(is_active=True).order_by('name'),
        'product_sets': ProductSet.objects.using(DB_NAME).filter(is_active=True).order_by('name'),
        'payment_methods': Transaction.PAYMENT_METHOD_CHOICES,
        'today': timezone.now().date().isoformat(),
    }
    return render(request, 'teams/team_tansaibou/register_sale.html', context)


def sale_list(request):
    """
    販売履歴一覧表示

    機能:
    - 全販売トランザクションを新しい順に表示
    - 各取引の明細（商品・セット商品）を表示

    設計方針:
    - N+1問題対策: select_related/prefetch_relatedでクエリ最適化
    - パフォーマンス: 関連データを事前ロード

    Returns:
        HttpResponse: 販売履歴一覧ページ
    """
    transactions = Transaction.objects.using(DB_NAME).select_related(
        'recorded_by'
    ).prefetch_related(
        'items__product',
        'items__product_set'
    ).order_by('-transaction_date', '-created_at')

    context = {
        'transactions': transactions,
    }
    return render(request, 'teams/team_tansaibou/sale_list.html', context)


# ===== 商品管理 =====

def product_list(request):
    """
    商品一覧表示

    機能:
    - 全商品を名前順に表示
    - 各商品の価格、在庫、状態を確認可能
    - 編集・在庫補充へのリンク提供

    Returns:
        HttpResponse: 商品一覧ページ
    """
    products = Product.objects.using(DB_NAME).all().order_by('name')

    context = {
        'products': products,
    }
    return render(request, 'teams/team_tansaibou/product_list.html', context)


def product_add(request):
    """
    商品登録

    機能:
    - GET: 商品登録フォーム表示
    - POST: 新規商品をデータベースに登録

    Args:
        request: HTTPリクエストオブジェクト
            POST時の必須パラメータ:
                - name: 商品名
                - current_price: 価格
                - stock: 在庫数（デフォルト: 0）
                - description: 説明（オプション）
                - is_active: 販売中フラグ（チェックボックス）

    Returns:
        HttpResponse: 登録フォーム（GET時）または商品一覧へリダイレクト（POST成功時）

    設計方針:
    - 初期在庫は0でも登録可能（後から在庫補充）
    - is_activeでアクティブな商品のみPOS画面に表示
    """
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
                is_active=is_active
            )

            messages.success(request, f'商品「{name}」を登録しました')
            return redirect('team_tansaibou:product_list')

        except Exception as e:
            messages.error(request, f'エラーが発生しました: {str(e)}')

    return render(request, 'teams/team_tansaibou/product_add.html')


def product_edit(request, product_id):
    """
    商品編集

    機能:
    - GET: 既存商品の編集フォーム表示
    - POST: 商品情報の更新

    Args:
        request: HTTPリクエストオブジェクト
        product_id: 編集対象の商品ID

    Returns:
        HttpResponse: 編集フォーム（GET時）または商品一覧へリダイレクト（POST成功時）
                     商品が見つからない場合も商品一覧へリダイレクト

    設計方針:
    - get_object_or_404でシンプルなエラーハンドリング
    - 在庫数も編集可能（直接調整が必要な場合に対応）
    """
    # get_object_or_404は使えない（マルチDBのため）ので手動実装
    try:
        product = Product.objects.using(DB_NAME).get(id=product_id)
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


def product_restock(request, product_id):
    """
    在庫補充

    機能:
    - GET: 在庫補充フォーム表示（現在の在庫数も表示）
    - POST: 指定数量を現在の在庫に追加

    Args:
        request: HTTPリクエストオブジェクト
        product_id: 在庫補充対象の商品ID
            POST時のパラメータ:
                - add_quantity: 追加する在庫数（1以上）

    Returns:
        HttpResponse: 在庫補充フォーム（GET時）または商品一覧へリダイレクト（POST成功時）

    設計方針:
    - 加算方式: 現在の在庫に追加（絶対値設定ではない）
    - バリデーション: 1以上の数値のみ受付
    - ユーザーフィードバック: 追加後の合計在庫数を表示
    """
    try:
        product = Product.objects.using(DB_NAME).get(id=product_id)
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

def productset_list(request):
    """
    セット商品一覧表示

    機能:
    - 全セット商品を名前順に表示
    - 各セットの構成商品と在庫状況を表示

    設計方針:
    - N+1問題対策: prefetch_relatedで構成商品を事前ロード
    - 在庫表示: get_stock_status()で計算された在庫数を表示

    Returns:
        HttpResponse: セット商品一覧ページ
    """
    product_sets = ProductSet.objects.using(DB_NAME).prefetch_related(
        'items__product'
    ).all().order_by('name')

    context = {
        'product_sets': product_sets,
    }
    return render(request, 'teams/team_tansaibou/productset_list.html', context)


def productset_add(request):
    """
    セット商品登録

    機能:
    - GET: セット商品登録フォーム表示（構成商品選択UI含む）
    - POST: 新規セット商品と構成商品の一括登録

    Args:
        request: HTTPリクエストオブジェクト
            POST時のパラメータ:
                - name: セット商品名
                - price: セット価格
                - description: 説明（オプション）
                - is_active: 販売中フラグ
                - product_id[]: 構成商品IDの配列
                - quantity[]: 各構成商品の数量配列

    Returns:
        HttpResponse: 登録フォーム（GET時）またはセット一覧へリダイレクト（POST成功時）

    設計方針:
    - トランザクション保証: atomic()でセット本体と構成商品を同時作成
    - 柔軟性: 複数の構成商品を動的に追加可能（JavaScript連携）
    - バリデーション: 空の商品IDや数量は無視
    """
    if request.method == 'POST':
        try:
            with db_transaction.atomic(using=DB_NAME):
                # セット商品の基本情報
                name = request.POST.get('name')
                price = request.POST.get('price')
                description = request.POST.get('description', '')
                is_active = request.POST.get('is_active') == 'on'

                # セット商品を作成
                product_set = ProductSet.objects.using(DB_NAME).create(
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
                        ProductSetItem.objects.using(DB_NAME).create(
                            product_set=product_set,
                            product_id=product_id,
                            quantity=int(quantity)
                        )

                messages.success(request, f'セット商品「{name}」を登録しました')
                return redirect('team_tansaibou:productset_list')

        except Exception as e:
            messages.error(request, f'エラーが発生しました: {str(e)}')

    products = Product.objects.using(DB_NAME).filter(is_active=True).order_by('name')
    context = {
        'products': products,
    }
    return render(request, 'teams/team_tansaibou/productset_add.html', context)


def productset_edit(request, productset_id):
    """
    セット商品編集

    機能:
    - GET: 既存セット商品の編集フォーム表示
    - POST: セット情報と構成商品の更新

    Args:
        request: HTTPリクエストオブジェクト
        productset_id: 編集対象のセット商品ID

    Returns:
        HttpResponse: 編集フォーム（GET時）またはセット一覧へリダイレクト（POST成功時）

    設計方針:
    - トランザクション保証: atomic()で基本情報と構成商品を同時更新
    - 更新方式: 構成商品を全削除→再作成（シンプルで確実）
    - 代替案: 差分更新も可能だが、複雑性を避けて全削除方式を採用
    """
    try:
        product_set = ProductSet.objects.using(DB_NAME).prefetch_related(
            'items__product'
        ).get(id=productset_id)
    except ProductSet.DoesNotExist:
        messages.error(request, 'セット商品が見つかりません')
        return redirect('team_tansaibou:productset_list')

    if request.method == 'POST':
        try:
            with db_transaction.atomic(using=DB_NAME):
                # 基本情報の更新
                product_set.name = request.POST.get('name')
                product_set.price = request.POST.get('price')
                product_set.description = request.POST.get('description', '')
                product_set.is_active = request.POST.get('is_active') == 'on'
                product_set.save(using=DB_NAME)

                # 既存の構成商品を削除
                ProductSetItem.objects.using(DB_NAME).filter(product_set=product_set).delete()

                # 新しい構成商品を追加
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

    products = Product.objects.using(DB_NAME).filter(is_active=True).order_by('name')
    context = {
        'product_set': product_set,
        'products': products,
    }
    return render(request, 'teams/team_tansaibou/productset_edit.html', context)