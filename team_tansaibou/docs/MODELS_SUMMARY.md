# models.py サマリー

## モデル一覧

### 1. Member（メンバー）
**行数:** 7-12

```python
class Member(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
```

**用途:** チームメンバー情報
**リレーション:** PriceHistory, Transaction から参照

---

### 2. Product（個別商品）
**行数:** 15-53

```python
class Product(models.Model):
    name = models.CharField(max_length=100)           # 商品名
    current_price = models.DecimalField(...)          # 価格
    stock = models.IntegerField(default=0)            # 在庫数
    description = models.TextField(blank=True)        # 説明
    is_active = models.BooleanField(default=True)     # 販売中
    created_at, updated_at                            # タイムスタンプ
```

**メソッド:**
- `check_stock(quantity)` → bool: 在庫チェック

**用途:** 個別商品の管理
**特徴:** シンプルな構造、在庫管理機能付き

---

### 3. ProductSet（セット商品）
**行数:** 56-112

```python
class ProductSet(models.Model):
    name = models.CharField(max_length=100)           # セット名
    price = models.DecimalField(...)                  # セット価格
    description = models.TextField(blank=True)        # 説明
    is_active = models.BooleanField(default=True)     # 販売中
    created_at, updated_at                            # タイムスタンプ
```

**メソッド:**
- `get_total_component_price()` → Decimal: 構成商品の合計価格
- `get_discount_amount()` → Decimal: 割引額
- `check_stock(quantity)` → bool: 全構成商品の在庫チェック
- `get_stock_status()` → int: 販売可能数

**用途:** セット商品の管理
**特徴:** 構成商品から自動的に在庫数・割引額を計算

---

### 4. ProductSetItem（セット構成商品）
**行数:** 115-139

```python
class ProductSetItem(models.Model):
    product_set = models.ForeignKey(ProductSet, ...)  # セット商品
    product = models.ForeignKey(Product, ...)         # 商品
    quantity = models.IntegerField(...)               # 数量
```

**制約:**
- unique_together: ['product_set', 'product']

**用途:** セット商品の構成管理
**例:** セットA = ジュース2本 + お菓子1個

---

### 5. PriceHistory（価格変更履歴）
**行数:** 142-193

```python
class PriceHistory(models.Model):
    product = models.ForeignKey(Product, null=True, ...)        # 商品
    product_set = models.ForeignKey(ProductSet, null=True, ...) # セット商品
    old_price = models.DecimalField(...)                        # 変更前価格
    new_price = models.DecimalField(...)                        # 変更後価格
    changed_at = models.DateTimeField(auto_now_add=True)        # 変更日時
    changed_by = models.ForeignKey(Member, ...)                 # 変更者
    reason = models.TextField(blank=True)                       # 変更理由
```

**制約:**
- product と product_set のどちらか一方のみ（XOR）

**メソッド:**
- `clean()`: バリデーション

**用途:** 価格変更の追跡
**特徴:** 個別商品とセット商品の両方に対応

---

### 6. Transaction（販売取引）
**行数:** 196-242

```python
class Transaction(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', '現金'),
        ('card', 'カード'),
        ('electronic', '電子マネー'),
        ('other', 'その他'),
    ]

    transaction_date = models.DateTimeField(...)              # 販売日時
    total_amount = models.DecimalField(...)                   # 合計金額
    recorded_by = models.ForeignKey(Member, ...)              # 担当者
    payment_method = models.CharField(choices=...)            # 支払方法
    notes = models.TextField(blank=True)                      # メモ
    created_at, updated_at                                    # タイムスタンプ
```

**インデックス:**
- transaction_date (降順)
- recorded_by

**用途:** 販売の基本情報
**特徴:** 支払方法の選択、担当者の記録

---

### 7. TransactionItem（取引明細）
**行数:** 245-346

```python
class TransactionItem(models.Model):
    transaction = models.ForeignKey(Transaction, ...)           # 取引
    product = models.ForeignKey(Product, null=True, ...)        # 商品
    product_set = models.ForeignKey(ProductSet, null=True, ...) # セット商品
    quantity = models.IntegerField(...)                         # 数量
    price_at_sale = models.DecimalField(...)                    # 販売時価格
    subtotal = models.DecimalField(...)                         # 小計
```

**制約:**
- product と product_set のどちらか一方のみ（XOR）

**メソッド:**
- `clean()`: バリデーション
- `get_item_name()` → str: 商品名を取得
- `check_and_reduce_stock()`: 在庫チェックと減算（エラー時は詳細メッセージ）
- `save()`: 小計自動計算、新規作成時に在庫を自動減算

**用途:** 取引の商品明細
**特徴:** 保存時に自動的に在庫を減算する

---

## 在庫管理の仕組み

### 個別商品販売
```
TransactionItem.save()
  → check_and_reduce_stock()
    → Product.stock -= quantity
```

### セット商品販売
```
TransactionItem.save()
  → check_and_reduce_stock()
    → for each ProductSetItem:
        Product.stock -= (item.quantity × quantity)
```

### 在庫不足時
- ValidationErrorを発生
- 詳細なエラーメッセージ（どの商品が何個不足しているか）

---

## リレーション図

```
Member
  ├→ PriceHistory.changed_by
  └→ Transaction.recorded_by

Product
  ├→ ProductSetItem.product
  ├→ PriceHistory.product
  └→ TransactionItem.product

ProductSet
  ├→ ProductSetItem.product_set (1:N)
  ├→ PriceHistory.product_set
  └→ TransactionItem.product_set

Transaction
  └→ TransactionItem.transaction (1:N)
```

---

## バリデーション

### MinValueValidator
- Product.current_price ≥ 0
- Product.stock ≥ 0
- Transaction.total_amount ≥ 0
- TransactionItem.quantity ≥ 1
- TransactionItem.price_at_sale ≥ 0

### XOR制約
- PriceHistory: product または product_set のどちらか一方のみ
- TransactionItem: product または product_set のどちらか一方のみ

### unique_together
- ProductSetItem: ['product_set', 'product']

---

## インポート

```python
from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal
```

---

## コード統計

| 項目 | 値 |
|------|-----|
| 総行数 | 347行 |
| モデル数 | 7 |
| メソッド数 | 9 |
| ForeignKey数 | 10 |
| インデックス数 | 2 |
| unique_together | 1 |

---

## 主な特徴

1. **シンプル:** 7モデルで完結、理解しやすい構造
2. **自動化:** 在庫減算、小計計算を自動実行
3. **柔軟性:** 個別商品とセット商品の両方に対応
4. **追跡可能:** 価格変更履歴、担当者記録
5. **堅牢性:** バリデーション、制約で整合性を保証

---

## 使用例

### 個別商品の登録
```python
product = Product.objects.using('team_tansaibou').create(
    name='ジュース',
    current_price=100,
    stock=50
)
```

### セット商品の作成
```python
# セット本体
product_set = ProductSet.objects.using('team_tansaibou').create(
    name='ドリンクセット',
    price=250
)

# 構成商品の追加
ProductSetItem.objects.using('team_tansaibou').create(
    product_set=product_set,
    product=juice,      # ジュース
    quantity=2
)
ProductSetItem.objects.using('team_tansaibou').create(
    product_set=product_set,
    product=snack,      # お菓子
    quantity=1
)
```

### 販売記録
```python
# 取引作成
transaction = Transaction.objects.using('team_tansaibou').create(
    transaction_date=timezone.now(),
    total_amount=250,
    recorded_by=member,
    payment_method='cash'
)

# 明細作成（在庫は自動減算される）
TransactionItem.objects.using('team_tansaibou').create(
    transaction=transaction,
    product_set=product_set,
    quantity=1,
    price_at_sale=250
)
# → ジュースの在庫 -2、お菓子の在庫 -1
```

### 販売可能数の確認
```python
# セットの販売可能数を取得
available = product_set.get_stock_status()
# → 最も少ない構成商品から計算
#    例: ジュース在庫50、お菓子在庫20の場合
#    → min(50//2, 20//1) = min(25, 20) = 20セット
```

---

## 注意事項

### TransactionItemの更新
- `save()`で在庫減算は**新規作成時のみ**実行
- 既存レコードの編集では在庫は変更されない
- 取引の修正が必要な場合は、明細を削除→再作成するか、手動で在庫を調整

### データベースルーティング
- 必ず `using('team_tansaibou')` を指定
- 例: `Product.objects.using('team_tansaibou').all()`

### 在庫不足エラー
- 販売時に在庫が不足すると ValidationError が発生
- トランザクション全体がロールバックされる
- 管理画面では自動的にエラーメッセージが表示される
