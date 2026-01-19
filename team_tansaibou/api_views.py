"""
Team Tansaibou ダッシュボード用APIビュー

各エンドポイント:
- today_sales: 本日の売上合計・件数
- hourly_stats: 時間帯別の売上・件数
- yearly_comparison: 年度比較（去年vs今年）
- daily_comparison: 日別比較（1日目vs2日目）
- product_ranking: 商品別売上ランキング
- stock_prediction: 売り切れ予測・ロス予測
"""

from django.http import JsonResponse
from django.db.models import Sum, Count, F
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from functools import wraps

from .models import Store, Product, ProductSet, Transaction, TransactionItem
from .views import get_current_store

DB = 'team_tansaibou'


def api_login_required(view_func):
    """API用のログイン必須デコレータ"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        store = get_current_store(request)
        if not store:
            return JsonResponse({'error': 'ログインが必要です'}, status=401)
        request.current_store = store
        return view_func(request, *args, **kwargs)
    return wrapper


def get_today_range():
    """今日の開始・終了時刻を取得"""
    today = timezone.localtime(timezone.now()).date()
    start = timezone.make_aware(datetime.combine(today, datetime.min.time()))
    end = timezone.make_aware(datetime.combine(today, datetime.max.time()))
    return start, end


@api_login_required
def today_sales(request):
    """本日の売上合計・件数"""
    store = request.current_store
    start, end = get_today_range()

    transactions = Transaction.objects.using(DB).filter(
        store=store,
        transaction_date__range=(start, end)
    )

    result = transactions.aggregate(
        total=Sum('total_amount'),
        count=Count('id')
    )

    return JsonResponse({
        'total_sales': int(result['total'] or 0),
        'transaction_count': result['count'] or 0,
    })


@api_login_required
def hourly_stats(request):
    """時間帯別の売上・件数（本日分）"""
    store = request.current_store
    start, end = get_today_range()

    transactions = Transaction.objects.using(DB).filter(
        store=store,
        transaction_date__range=(start, end)
    )

    # 時間帯別に集計
    hourly_data = {}
    for hour in range(9, 21):  # 9時〜20時
        hourly_data[hour] = {'sales': 0, 'count': 0}

    for trans in transactions:
        hour = timezone.localtime(trans.transaction_date).hour
        if hour in hourly_data:
            hourly_data[hour]['sales'] += int(trans.total_amount)
            hourly_data[hour]['count'] += 1

    # グラフ用にリスト形式に変換
    labels = [f'{h}:00' for h in range(9, 21)]
    sales = [hourly_data[h]['sales'] for h in range(9, 21)]
    counts = [hourly_data[h]['count'] for h in range(9, 21)]

    return JsonResponse({
        'labels': labels,
        'sales': sales,
        'counts': counts,
    })


@api_login_required
def yearly_comparison(request):
    """年度比較（去年vs今年）- 学祭期間の比較"""
    store = request.current_store

    # 今年と去年の同じ日付範囲で比較
    # 学祭は通常11月の土日に開催と仮定
    now = timezone.localtime(timezone.now())
    this_year = now.year
    last_year = this_year - 1

    def get_year_sales(year):
        """指定年の売上を取得"""
        year_start = timezone.make_aware(datetime(year, 1, 1))
        year_end = timezone.make_aware(datetime(year, 12, 31, 23, 59, 59))

        result = Transaction.objects.using(DB).filter(
            store=store,
            transaction_date__range=(year_start, year_end)
        ).aggregate(
            total=Sum('total_amount'),
            count=Count('id')
        )
        return {
            'sales': int(result['total'] or 0),
            'count': result['count'] or 0
        }

    this_year_data = get_year_sales(this_year)
    last_year_data = get_year_sales(last_year)

    return JsonResponse({
        'labels': [str(last_year), str(this_year)],
        'sales': [last_year_data['sales'], this_year_data['sales']],
        'counts': [last_year_data['count'], this_year_data['count']],
    })


@api_login_required
def daily_comparison(request):
    """日別比較（1日目vs2日目）- 学祭の日別比較"""
    store = request.current_store

    # 最初の取引日を1日目として、その翌日を2日目とする
    first_trans = Transaction.objects.using(DB).filter(
        store=store
    ).order_by('transaction_date').first()

    if not first_trans:
        return JsonResponse({
            'labels': ['1日目', '2日目'],
            'sales': [0, 0],
            'counts': [0, 0],
        })

    day1 = timezone.localtime(first_trans.transaction_date).date()
    day2 = day1 + timedelta(days=1)

    def get_day_sales(date):
        """指定日の売上を取得"""
        start = timezone.make_aware(datetime.combine(date, datetime.min.time()))
        end = timezone.make_aware(datetime.combine(date, datetime.max.time()))

        result = Transaction.objects.using(DB).filter(
            store=store,
            transaction_date__range=(start, end)
        ).aggregate(
            total=Sum('total_amount'),
            count=Count('id')
        )
        return {
            'sales': int(result['total'] or 0),
            'count': result['count'] or 0
        }

    day1_data = get_day_sales(day1)
    day2_data = get_day_sales(day2)

    return JsonResponse({
        'labels': [f'1日目 ({day1.strftime("%m/%d")})', f'2日目 ({day2.strftime("%m/%d")})'],
        'sales': [day1_data['sales'], day2_data['sales']],
        'counts': [day1_data['count'], day2_data['count']],
    })


@api_login_required
def product_ranking(request):
    """商品別売上ランキング（本日分）"""
    store = request.current_store
    start, end = get_today_range()

    # 通常商品の集計
    product_items = TransactionItem.objects.using(DB).filter(
        transaction__store=store,
        transaction__transaction_date__range=(start, end),
        product__isnull=False
    ).values(
        'product__id', 'product__name', 'product__stock', 'product__current_price'
    ).annotate(
        total_quantity=Sum('quantity'),
        total_sales=Sum('subtotal')
    )

    # セット商品の集計
    set_items = TransactionItem.objects.using(DB).filter(
        transaction__store=store,
        transaction__transaction_date__range=(start, end),
        product_set__isnull=False
    ).values(
        'product_set__id', 'product_set__name', 'product_set__price'
    ).annotate(
        total_quantity=Sum('quantity'),
        total_sales=Sum('subtotal')
    )

    ranking = []

    for item in product_items:
        ranking.append({
            'name': item['product__name'],
            'type': '通常',
            'quantity': item['total_quantity'],
            'sales': int(item['total_sales']),
            'stock': item['product__stock'],
            'price': int(item['product__current_price']),
        })

    for item in set_items:
        # セット商品の在庫は計算で取得
        try:
            product_set = ProductSet.objects.using(DB).get(id=item['product_set__id'])
            stock = product_set.get_stock_status()
        except ProductSet.DoesNotExist:
            stock = 0

        ranking.append({
            'name': item['product_set__name'],
            'type': 'セット',
            'quantity': item['total_quantity'],
            'sales': int(item['total_sales']),
            'stock': stock,
            'price': int(item['product_set__price']),
        })

    # 売上金額でソート
    ranking.sort(key=lambda x: x['sales'], reverse=True)

    return JsonResponse({
        'ranking': ranking[:10],  # 上位10件
    })


@api_login_required
def stock_prediction(request):
    """売り切れ予測・ロス予測"""
    store = request.current_store
    start, end = get_today_range()

    # 現在時刻と経過時間を計算
    now = timezone.localtime(timezone.now())
    hours_elapsed = max((now - start).total_seconds() / 3600, 0.1)  # 最低0.1時間

    # 営業終了時刻（20時と仮定）
    closing_hour = 20
    remaining_hours = max(closing_hour - now.hour - now.minute / 60, 0)

    # 本日の商品別販売数を取得
    product_sales = TransactionItem.objects.using(DB).filter(
        transaction__store=store,
        transaction__transaction_date__range=(start, end),
        product__isnull=False
    ).values('product__id').annotate(
        total_quantity=Sum('quantity')
    )

    product_sales_dict = {
        item['product__id']: item['total_quantity']
        for item in product_sales
    }

    # 全商品の予測を計算
    products = Product.objects.using(DB).filter(store=store, is_active=True)

    sellout_predictions = []
    loss_predictions = []

    for product in products:
        sold_qty = product_sales_dict.get(product.id, 0)
        sales_rate = sold_qty / hours_elapsed if hours_elapsed > 0 else 0  # 個/時間

        if sales_rate > 0:
            # 売り切れ予測時間
            time_to_sellout = product.stock / sales_rate

            if time_to_sellout < 0.5:
                status = 'critical'
            elif time_to_sellout < 1:
                status = 'warning'
            else:
                status = 'ok'

            sellout_predictions.append({
                'name': product.name,
                'current_stock': product.stock,
                'sales_rate': round(sales_rate, 1),
                'time_to_sellout': round(time_to_sellout, 1),
                'status': status,
            })

        # ロス予測（残り営業時間での予測残数）
        predicted_remaining = product.stock - (sales_rate * remaining_hours)
        if predicted_remaining > 0:
            loss_predictions.append({
                'name': product.name,
                'current_stock': product.stock,
                'predicted_remaining': max(0, round(predicted_remaining)),
                'loss_amount': max(0, round(predicted_remaining * float(product.current_price))),
            })

    # 売り切れ予測をステータス（危険度）順にソート
    status_order = {'critical': 0, 'warning': 1, 'ok': 2}
    sellout_predictions.sort(key=lambda x: (status_order[x['status']], x['time_to_sellout']))

    # ロス予測をロス金額順にソート
    loss_predictions.sort(key=lambda x: x['loss_amount'], reverse=True)

    return JsonResponse({
        'sellout_predictions': sellout_predictions[:10],
        'loss_predictions': loss_predictions[:10],
        'hours_elapsed': round(hours_elapsed, 1),
        'remaining_hours': round(remaining_hours, 1),
    })


@api_login_required
def profit_analysis(request):
    """損益分析（本日分）- 粗利益、利益率、商品別利益"""
    store = request.current_store
    start, end = get_today_range()

    # 通常商品の売上データを取得（原価情報含む）
    product_items = TransactionItem.objects.using(DB).filter(
        transaction__store=store,
        transaction__transaction_date__range=(start, end),
        product__isnull=False
    ).select_related('product')

    # 商品別の利益計算
    product_profits = {}
    total_revenue = Decimal('0')
    total_cost = Decimal('0')

    for item in product_items:
        product = item.product
        revenue = item.subtotal  # 販売価格 × 数量
        cost = product.cost_price * item.quantity  # 原価 × 数量
        profit = revenue - cost

        total_revenue += revenue
        total_cost += cost

        if product.id not in product_profits:
            product_profits[product.id] = {
                'name': product.name,
                'quantity': 0,
                'revenue': Decimal('0'),
                'cost': Decimal('0'),
                'profit': Decimal('0'),
                'price': product.current_price,
                'cost_price': product.cost_price,
            }

        product_profits[product.id]['quantity'] += item.quantity
        product_profits[product.id]['revenue'] += revenue
        product_profits[product.id]['cost'] += cost
        product_profits[product.id]['profit'] += profit

    # セット商品の利益計算（セットに含まれる商品の原価合計を使用）
    set_items = TransactionItem.objects.using(DB).filter(
        transaction__store=store,
        transaction__transaction_date__range=(start, end),
        product_set__isnull=False
    ).select_related('product_set')

    for item in set_items:
        product_set = item.product_set
        revenue = item.subtotal  # セット価格 × 数量

        # セット商品の原価を計算（セット内商品の原価合計）
        set_cost = Decimal('0')
        for set_item in product_set.productsetitem_set.using(DB).select_related('product'):
            set_cost += set_item.product.cost_price * set_item.quantity

        cost = set_cost * item.quantity
        profit = revenue - cost

        total_revenue += revenue
        total_cost += cost

        set_key = f'set_{product_set.id}'
        if set_key not in product_profits:
            product_profits[set_key] = {
                'name': f'{product_set.name} (セット)',
                'quantity': 0,
                'revenue': Decimal('0'),
                'cost': Decimal('0'),
                'profit': Decimal('0'),
                'price': product_set.price,
                'cost_price': set_cost,
            }

        product_profits[set_key]['quantity'] += item.quantity
        product_profits[set_key]['revenue'] += revenue
        product_profits[set_key]['cost'] += cost
        product_profits[set_key]['profit'] += profit

    # 利益率計算
    total_profit = total_revenue - total_cost
    profit_margin = 0
    if total_revenue > 0:
        profit_margin = round((total_profit / total_revenue) * 100, 1)

    # 在庫評価額（現在の在庫 × 仕入れ原価）を計算
    inventory_value = Decimal('0')
    products = Product.objects.using(DB).filter(store=store, is_active=True)
    for product in products:
        inventory_value += product.cost_price * product.stock

    # 商品別データをリストに変換（利益額でソート）
    product_list = []
    for data in product_profits.values():
        item_margin = 0
        if data['revenue'] > 0:
            item_margin = round((data['profit'] / data['revenue']) * 100, 1)

        product_list.append({
            'name': data['name'],
            'quantity': data['quantity'],
            'revenue': int(data['revenue']),
            'cost': int(data['cost']),
            'profit': int(data['profit']),
            'margin': item_margin,
            'unit_price': int(data['price']),
            'unit_cost': int(data['cost_price']),
        })

    product_list.sort(key=lambda x: x['profit'], reverse=True)

    return JsonResponse({
        'total_revenue': int(total_revenue),        # 売上高
        'total_cogs': int(total_cost),              # 売上原価（Cost of Goods Sold）
        'total_profit': int(total_profit),          # 粗利益
        'profit_margin': profit_margin,             # 粗利益率
        'inventory_value': int(inventory_value),    # 在庫評価額
        'products': product_list[:20],
    })
