"""
Team Tansaibou POS システムの包括的なテストスイート

このテストスイートは以下をカバーします:
- モデルのビジネスロジック（在庫管理、価格計算）
- ビューの機能（CRUD操作、POS登録）
- 統合テスト（販売フロー全体）
- エッジケース（在庫不足、バリデーションエラー）
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
import json

from team_tansaibou.models import (
    Member,
    Product,
    ProductSet,
    ProductSetItem,
    Transaction,
    TransactionItem,
    PriceHistory,
)


class ProductModelTest(TestCase):
    """Product モデルのテスト"""

    databases = ['team_tansaibou']

    def setUp(self):
        """テストデータの準備"""
        self.product = Product.objects.using('team_tansaibou').create(
            name='テスト商品',
            current_price=Decimal('100'),
            stock=10,
            description='テスト用の商品です',
            is_active=True
        )

    def test_product_creation(self):
        """商品の作成テスト"""
        self.assertEqual(self.product.name, 'テスト商品')
        self.assertEqual(self.product.current_price, Decimal('100'))
        self.assertEqual(self.product.stock, 10)
        self.assertTrue(self.product.is_active)

    def test_product_str(self):
        """__str__メソッドのテスト"""
        expected = 'テスト商品 (100円) - 在庫10'
        self.assertEqual(str(self.product), expected)

    def test_check_stock_sufficient(self):
        """在庫が十分な場合のcheck_stockテスト"""
        self.assertTrue(self.product.check_stock(5))
        self.assertTrue(self.product.check_stock(10))

    def test_check_stock_insufficient(self):
        """在庫が不足する場合のcheck_stockテスト"""
        self.assertFalse(self.product.check_stock(11))
        self.assertFalse(self.product.check_stock(100))

    def test_check_stock_zero(self):
        """在庫ゼロの場合のcheck_stockテスト"""
        self.product.stock = 0
        self.product.save(using='team_tansaibou')
        self.assertFalse(self.product.check_stock(1))
        self.assertTrue(self.product.check_stock(0))


class ProductSetModelTest(TestCase):
    """ProductSet モデルのテスト"""

    databases = ['team_tansaibou']

    def setUp(self):
        """テストデータの準備"""
        # 個別商品を作成
        self.product1 = Product.objects.using('team_tansaibou').create(
            name='商品A',
            current_price=Decimal('100'),
            stock=20,
            is_active=True
        )
        self.product2 = Product.objects.using('team_tansaibou').create(
            name='商品B',
            current_price=Decimal('150'),
            stock=15,
            is_active=True
        )

        # セット商品を作成
        self.product_set = ProductSet.objects.using('team_tansaibou').create(
            name='セットC',
            price=Decimal('200'),
            description='お得なセット',
            is_active=True
        )

        # セット構成商品を追加（商品A x2, 商品B x1）
        ProductSetItem.objects.using('team_tansaibou').create(
            product_set=self.product_set,
            product=self.product1,
            quantity=2
        )
        ProductSetItem.objects.using('team_tansaibou').create(
            product_set=self.product_set,
            product=self.product2,
            quantity=1
        )

    def test_product_set_creation(self):
        """セット商品の作成テスト"""
        self.assertEqual(self.product_set.name, 'セットC')
        self.assertEqual(self.product_set.price, Decimal('200'))
        self.assertEqual(self.product_set.items.count(), 2)

    def test_product_set_str(self):
        """__str__メソッドのテスト"""
        expected = '[セット] セットC (200円)'
        self.assertEqual(str(self.product_set), expected)

    def test_get_total_component_price(self):
        """構成商品の合計価格計算テスト"""
        # 商品A(100円) x2 + 商品B(150円) x1 = 350円
        total = self.product_set.get_total_component_price()
        self.assertEqual(total, Decimal('350'))

    def test_get_discount_amount(self):
        """割引額の計算テスト"""
        # 350円 - 200円 = 150円の割引
        discount = self.product_set.get_discount_amount()
        self.assertEqual(discount, Decimal('150'))

    def test_get_stock_status(self):
        """在庫状況の計算テスト（最小値を返す）"""
        # 商品A: 20個 ÷ 2 = 10セット
        # 商品B: 15個 ÷ 1 = 15セット
        # 最小値は10セット
        stock_status = self.product_set.get_stock_status()
        self.assertEqual(stock_status, 10)

    def test_get_stock_status_limiting_product(self):
        """制限商品による在庫状況テスト"""
        # 商品Bの在庫を減らす
        self.product2.stock = 5
        self.product2.save(using='team_tansaibou')

        # 商品A: 20個 ÷ 2 = 10セット
        # 商品B: 5個 ÷ 1 = 5セット
        # 最小値は5セット
        stock_status = self.product_set.get_stock_status()
        self.assertEqual(stock_status, 5)

    def test_get_stock_status_zero(self):
        """在庫ゼロの場合のテスト"""
        self.product1.stock = 0
        self.product1.save(using='team_tansaibou')

        stock_status = self.product_set.get_stock_status()
        self.assertEqual(stock_status, 0)

    def test_get_stock_status_empty_set(self):
        """構成商品がない場合のテスト"""
        empty_set = ProductSet.objects.using('team_tansaibou').create(
            name='空セット',
            price=Decimal('100')
        )
        self.assertEqual(empty_set.get_stock_status(), 0)

    def test_check_stock_sufficient(self):
        """在庫が十分な場合のcheck_stockテスト"""
        # 10セット分の在庫がある
        self.assertTrue(self.product_set.check_stock(5))
        self.assertTrue(self.product_set.check_stock(10))

    def test_check_stock_insufficient(self):
        """在庫が不足する場合のcheck_stockテスト"""
        self.assertFalse(self.product_set.check_stock(11))
        self.assertFalse(self.product_set.check_stock(100))


class TransactionItemModelTest(TestCase):
    """TransactionItem モデルのテスト"""

    databases = ['team_tansaibou']

    def setUp(self):
        """テストデータの準備"""
        self.member = Member.objects.using('team_tansaibou').create(
            name='山田 太郎'
        )

        self.product = Product.objects.using('team_tansaibou').create(
            name='商品X',
            current_price=Decimal('500'),
            stock=10,
            is_active=True
        )

        self.transaction = Transaction.objects.using('team_tansaibou').create(
            transaction_date=timezone.now(),
            total_amount=Decimal('1000'),
            recorded_by=self.member,
            payment_method='cash'
        )

    def test_transaction_item_subtotal_calculation(self):
        """小計の自動計算テスト"""
        item = TransactionItem.objects.using('team_tansaibou').create(
            transaction=self.transaction,
            product=self.product,
            quantity=3,
            price_at_sale=Decimal('500')
        )
        # 500円 × 3 = 1500円
        self.assertEqual(item.subtotal, Decimal('1500'))

    def test_transaction_item_stock_reduction(self):
        """在庫減算のテスト"""
        initial_stock = self.product.stock

        TransactionItem.objects.using('team_tansaibou').create(
            transaction=self.transaction,
            product=self.product,
            quantity=3,
            price_at_sale=Decimal('500')
        )

        # 在庫が3減っているか確認
        self.product.refresh_from_db(using='team_tansaibou')
        self.assertEqual(self.product.stock, initial_stock - 3)

    def test_transaction_item_stock_insufficient_error(self):
        """在庫不足時のエラーテスト"""
        self.product.stock = 2
        self.product.save(using='team_tansaibou')

        with self.assertRaises(ValidationError) as context:
            TransactionItem.objects.using('team_tansaibou').create(
                transaction=self.transaction,
                product=self.product,
                quantity=5,
                price_at_sale=Decimal('500')
            )

        self.assertIn('在庫が不足', str(context.exception))

    def test_transaction_item_xor_validation(self):
        """product と product_set のXOR制約テスト"""
        product_set = ProductSet.objects.using('team_tansaibou').create(
            name='セット',
            price=Decimal('1000')
        )

        # 両方設定した場合
        item = TransactionItem(
            transaction=self.transaction,
            product=self.product,
            product_set=product_set,
            quantity=1,
            price_at_sale=Decimal('500')
        )

        with self.assertRaises(ValidationError):
            item.clean()

        # 両方未設定の場合
        item2 = TransactionItem(
            transaction=self.transaction,
            quantity=1,
            price_at_sale=Decimal('500')
        )

        with self.assertRaises(ValidationError):
            item2.clean()

    def test_transaction_item_product_set_stock_reduction(self):
        """セット商品の在庫減算テスト"""
        # セット商品を作成
        product1 = Product.objects.using('team_tansaibou').create(
            name='構成商品1',
            current_price=Decimal('100'),
            stock=20
        )
        product2 = Product.objects.using('team_tansaibou').create(
            name='構成商品2',
            current_price=Decimal('200'),
            stock=15
        )

        product_set = ProductSet.objects.using('team_tansaibou').create(
            name='テストセット',
            price=Decimal('250')
        )

        ProductSetItem.objects.using('team_tansaibou').create(
            product_set=product_set,
            product=product1,
            quantity=2
        )
        ProductSetItem.objects.using('team_tansaibou').create(
            product_set=product_set,
            product=product2,
            quantity=1
        )

        # セット商品を2つ販売
        TransactionItem.objects.using('team_tansaibou').create(
            transaction=self.transaction,
            product_set=product_set,
            quantity=2,
            price_at_sale=Decimal('250')
        )

        # 構成商品の在庫確認
        product1.refresh_from_db(using='team_tansaibou')
        product2.refresh_from_db(using='team_tansaibou')

        # 商品1: 20 - (2 × 2) = 16
        # 商品2: 15 - (1 × 2) = 13
        self.assertEqual(product1.stock, 16)
        self.assertEqual(product2.stock, 13)


class RegisterSaleViewTest(TestCase):
    """販売登録ビューのテスト"""

    databases = ['team_tansaibou']

    def setUp(self):
        """テストデータの準備"""
        self.client = Client()

        self.member = Member.objects.using('team_tansaibou').create(
            name='佐藤 花子'
        )

        self.product1 = Product.objects.using('team_tansaibou').create(
            name='商品1',
            current_price=Decimal('300'),
            stock=50,
            is_active=True
        )

        self.product2 = Product.objects.using('team_tansaibou').create(
            name='商品2',
            current_price=Decimal('500'),
            stock=30,
            is_active=True
        )

    def test_register_sale_get(self):
        """GETリクエストでフォーム表示"""
        response = self.client.get(reverse('team_tansaibou:index'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '商品1')
        self.assertContains(response, '商品2')
        self.assertContains(response, self.member.name)

    def test_register_sale_post_single_product(self):
        """単一商品の販売登録テスト"""
        cart_data = [
            {
                'type': 'product',
                'id': self.product1.id,
                'name': '商品1',
                'price': 300,
                'quantity': 2
            }
        ]

        response = self.client.post(reverse('team_tansaibou:index'), {
            'transaction_date': timezone.now().isoformat(),
            'payment_method': 'cash',
            'recorded_by': self.member.id,
            'cart_items': json.dumps(cart_data),
            'notes': 'テスト販売'
        })

        # リダイレクトを確認
        self.assertEqual(response.status_code, 302)

        # トランザクションが作成されたか確認
        transaction = Transaction.objects.using('team_tansaibou').first()
        self.assertIsNotNone(transaction)
        self.assertEqual(transaction.total_amount, Decimal('600'))

        # 在庫が減っているか確認
        self.product1.refresh_from_db(using='team_tansaibou')
        self.assertEqual(self.product1.stock, 48)

    def test_register_sale_post_multiple_products(self):
        """複数商品の販売登録テスト"""
        cart_data = [
            {'type': 'product', 'id': self.product1.id, 'name': '商品1', 'price': 300, 'quantity': 3},
            {'type': 'product', 'id': self.product2.id, 'name': '商品2', 'price': 500, 'quantity': 2}
        ]

        response = self.client.post(reverse('team_tansaibou:index'), {
            'transaction_date': timezone.now().isoformat(),
            'payment_method': 'card',
            'recorded_by': self.member.id,
            'cart_items': json.dumps(cart_data)
        })

        self.assertEqual(response.status_code, 302)

        # トランザクションの確認
        transaction = Transaction.objects.using('team_tansaibou').first()
        # 300×3 + 500×2 = 1900
        self.assertEqual(transaction.total_amount, Decimal('1900'))
        self.assertEqual(transaction.items.count(), 2)

        # 在庫確認
        self.product1.refresh_from_db(using='team_tansaibou')
        self.product2.refresh_from_db(using='team_tansaibou')
        self.assertEqual(self.product1.stock, 47)
        self.assertEqual(self.product2.stock, 28)

    def test_register_sale_empty_cart(self):
        """空カートでのエラーテスト"""
        response = self.client.post(reverse('team_tansaibou:index'), {
            'transaction_date': timezone.now().isoformat(),
            'payment_method': 'cash',
            'recorded_by': self.member.id,
            'cart_items': '[]'
        })

        # エラーメッセージを確認
        messages = list(response.context['messages'])
        self.assertTrue(any('カートが空' in str(m) for m in messages))

    def test_register_sale_missing_required_fields(self):
        """必須項目不足のエラーテスト"""
        cart_data = [
            {'type': 'product', 'id': self.product1.id, 'name': '商品1', 'price': 300, 'quantity': 1}
        ]

        response = self.client.post(reverse('team_tansaibou:index'), {
            # transaction_date を省略
            'payment_method': 'cash',
            'cart_items': json.dumps(cart_data)
        })

        messages = list(response.context['messages'])
        self.assertTrue(any('必須項目' in str(m) for m in messages))


class ProductCRUDViewTest(TestCase):
    """商品CRUD操作のテスト"""

    databases = ['team_tansaibou']

    def setUp(self):
        """テストデータの準備"""
        self.client = Client()

        self.product = Product.objects.using('team_tansaibou').create(
            name='既存商品',
            current_price=Decimal('1000'),
            stock=25,
            description='既存商品の説明',
            is_active=True
        )

    def test_product_list(self):
        """商品一覧表示テスト"""
        response = self.client.get(reverse('team_tansaibou:product_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '既存商品')
        self.assertContains(response, '1000')

    def test_product_add(self):
        """商品追加テスト"""
        response = self.client.post(reverse('team_tansaibou:product_add'), {
            'name': '新商品',
            'current_price': '2000',
            'stock': '100',
            'description': '新商品の説明',
            'is_active': 'on'
        })

        self.assertEqual(response.status_code, 302)

        # 商品が作成されたか確認
        new_product = Product.objects.using('team_tansaibou').filter(name='新商品').first()
        self.assertIsNotNone(new_product)
        self.assertEqual(new_product.current_price, Decimal('2000'))
        self.assertEqual(new_product.stock, 100)

    def test_product_edit(self):
        """商品編集テスト"""
        response = self.client.post(
            reverse('team_tansaibou:product_edit', args=[self.product.id]),
            {
                'name': '更新商品',
                'current_price': '1500',
                'stock': '30',
                'description': '更新された説明',
                'is_active': 'on'
            }
        )

        self.assertEqual(response.status_code, 302)

        # 商品が更新されたか確認
        self.product.refresh_from_db(using='team_tansaibou')
        self.assertEqual(self.product.name, '更新商品')
        self.assertEqual(self.product.current_price, Decimal('1500'))
        self.assertEqual(self.product.stock, 30)

    def test_product_restock(self):
        """在庫補充テスト"""
        initial_stock = self.product.stock

        response = self.client.post(
            reverse('team_tansaibou:product_restock', args=[self.product.id]),
            {'add_quantity': '50'}
        )

        self.assertEqual(response.status_code, 302)

        # 在庫が増えたか確認
        self.product.refresh_from_db(using='team_tansaibou')
        self.assertEqual(self.product.stock, initial_stock + 50)


class ProductSetCRUDViewTest(TestCase):
    """セット商品CRUD操作のテスト"""

    databases = ['team_tansaibou']

    def setUp(self):
        """テストデータの準備"""
        self.client = Client()

        self.product1 = Product.objects.using('team_tansaibou').create(
            name='構成商品A',
            current_price=Decimal('200'),
            stock=100,
            is_active=True
        )

        self.product2 = Product.objects.using('team_tansaibou').create(
            name='構成商品B',
            current_price=Decimal('300'),
            stock=80,
            is_active=True
        )

    def test_productset_list(self):
        """セット商品一覧表示テスト"""
        product_set = ProductSet.objects.using('team_tansaibou').create(
            name='テストセット',
            price=Decimal('400')
        )

        response = self.client.get(reverse('team_tansaibou:productset_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'テストセット')

    def test_productset_add(self):
        """セット商品追加テスト"""
        response = self.client.post(reverse('team_tansaibou:productset_add'), {
            'name': '新セット',
            'price': '450',
            'description': 'お得なセット',
            'is_active': 'on',
            'product_id[]': [self.product1.id, self.product2.id],
            'quantity[]': ['2', '1']
        })

        self.assertEqual(response.status_code, 302)

        # セット商品が作成されたか確認
        new_set = ProductSet.objects.using('team_tansaibou').filter(name='新セット').first()
        self.assertIsNotNone(new_set)
        self.assertEqual(new_set.price, Decimal('450'))
        self.assertEqual(new_set.items.count(), 2)

    def test_productset_edit(self):
        """セット商品編集テスト"""
        product_set = ProductSet.objects.using('team_tansaibou').create(
            name='既存セット',
            price=Decimal('500')
        )

        ProductSetItem.objects.using('team_tansaibou').create(
            product_set=product_set,
            product=self.product1,
            quantity=1
        )

        response = self.client.post(
            reverse('team_tansaibou:productset_edit', args=[product_set.id]),
            {
                'name': '更新セット',
                'price': '600',
                'description': '更新された説明',
                'is_active': 'on',
                'product_id[]': [self.product1.id, self.product2.id],
                'quantity[]': ['3', '2']
            }
        )

        self.assertEqual(response.status_code, 302)

        # セット商品が更新されたか確認
        product_set.refresh_from_db(using='team_tansaibou')
        self.assertEqual(product_set.name, '更新セット')
        self.assertEqual(product_set.price, Decimal('600'))
        self.assertEqual(product_set.items.count(), 2)


class IntegrationTest(TestCase):
    """統合テスト（販売フロー全体）"""

    databases = ['team_tansaibou']

    def setUp(self):
        """テストデータの準備"""
        self.client = Client()

        self.member = Member.objects.using('team_tansaibou').create(
            name='鈴木 次郎'
        )

        # 個別商品
        self.product = Product.objects.using('team_tansaibou').create(
            name='単品商品',
            current_price=Decimal('800'),
            stock=20,
            is_active=True
        )

        # セット商品用の構成商品
        self.component1 = Product.objects.using('team_tansaibou').create(
            name='構成品1',
            current_price=Decimal('400'),
            stock=30,
            is_active=True
        )

        self.component2 = Product.objects.using('team_tansaibou').create(
            name='構成品2',
            current_price=Decimal('600'),
            stock=25,
            is_active=True
        )

        # セット商品
        self.product_set = ProductSet.objects.using('team_tansaibou').create(
            name='お得セット',
            price=Decimal('900')
        )

        ProductSetItem.objects.using('team_tansaibou').create(
            product_set=self.product_set,
            product=self.component1,
            quantity=1
        )
        ProductSetItem.objects.using('team_tansaibou').create(
            product_set=self.product_set,
            product=self.component2,
            quantity=1
        )

    def test_complete_sale_flow_with_mixed_items(self):
        """個別商品とセット商品を含む完全な販売フローテスト"""
        cart_data = [
            {'type': 'product', 'id': self.product.id, 'name': '単品商品', 'price': 800, 'quantity': 2},
            {'type': 'product_set', 'id': self.product_set.id, 'name': 'お得セット', 'price': 900, 'quantity': 3}
        ]

        response = self.client.post(reverse('team_tansaibou:index'), {
            'transaction_date': timezone.now().isoformat(),
            'payment_method': 'electronic',
            'recorded_by': self.member.id,
            'cart_items': json.dumps(cart_data),
            'notes': '統合テスト'
        })

        # 販売登録成功を確認
        self.assertEqual(response.status_code, 302)

        # トランザクション確認
        transaction = Transaction.objects.using('team_tansaibou').first()
        # 800×2 + 900×3 = 4300
        self.assertEqual(transaction.total_amount, Decimal('4300'))
        self.assertEqual(transaction.payment_method, 'electronic')
        self.assertEqual(transaction.items.count(), 2)

        # 在庫確認
        self.product.refresh_from_db(using='team_tansaibou')
        self.component1.refresh_from_db(using='team_tansaibou')
        self.component2.refresh_from_db(using='team_tansaibou')

        # 単品: 20 - 2 = 18
        self.assertEqual(self.product.stock, 18)
        # 構成品1: 30 - 3 = 27
        self.assertEqual(self.component1.stock, 27)
        # 構成品2: 25 - 3 = 22
        self.assertEqual(self.component2.stock, 22)

    def test_productset_stock_status_calculation(self):
        """セット商品の在庫状況計算の統合テスト"""
        # 構成品1: 30個、構成品2: 25個
        # セット在庫: min(30/1, 25/1) = 25セット
        self.assertEqual(self.product_set.get_stock_status(), 25)

        # 構成品1の在庫を減らす
        self.component1.stock = 10
        self.component1.save(using='team_tansaibou')

        # セット在庫: min(10/1, 25/1) = 10セット
        self.assertEqual(self.product_set.get_stock_status(), 10)
