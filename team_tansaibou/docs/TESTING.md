# Team Tansaibou POS システム - テストドキュメント

## 📋 概要

このドキュメントは、Team Tansaibou POSシステムのテスト戦略、テスト実行方法、およびテスト設計の理由を説明します。

## 🎯 テスト戦略

### テストの目的

1. **品質保証**: コードの正確性と信頼性を保証
2. **リグレッション防止**: 既存機能が新しい変更で壊れないことを確認
3. **ドキュメント**: テストコードが仕様書としても機能
4. **開発速度向上**: 手動テストの削減により開発サイクルを高速化

### テストの階層

```
┌─────────────────────────────────┐
│   統合テスト (Integration)      │  ← 販売フロー全体、複数モデル連携
├─────────────────────────────────┤
│   ビューテスト (View Tests)      │  ← HTTPリクエスト、レスポンス、リダイレクト
├─────────────────────────────────┤
│   モデルテスト (Model Tests)     │  ← ビジネスロジック、データ操作
└─────────────────────────────────┘
```

## 📁 テストファイル構成

```
team_tansaibou/
├── tests.py              # 全テストケース
├── models.py             # テスト対象モデル
└── views.py              # テスト対象ビュー
```

## 🧪 テストケース一覧

### 1. モデルテスト

#### `ProductModelTest`
- **目的**: 個別商品の在庫管理機能をテスト
- **カバー範囲**:
  - 商品作成
  - `check_stock()`: 在庫チェックロジック
  - 在庫境界値テスト（十分、不足、ゼロ）

**設計理由**: 在庫管理はPOSシステムの核心機能。在庫不足による販売エラーを防ぐため、境界値を含む網羅的テストが必要。

#### `ProductSetModelTest`
- **目的**: セット商品の在庫計算とビジネスロジックをテスト
- **カバー範囲**:
  - セット作成と構成商品の関連付け
  - `get_stock_status()`: 構成商品から在庫を計算（最小値方式）
  - `check_stock()`: セット販売可能数のチェック
  - `get_total_component_price()`: 構成商品の合計価格
  - `get_discount_amount()`: セット割引額の計算

**設計理由**: セット商品の在庫は複数の構成商品に依存するため、複雑な計算ロジックの正確性を保証する必要がある。

#### `TransactionItemModelTest`
- **目的**: 販売時の在庫減算と取引明細の正確性をテスト
- **カバー範囲**:
  - 小計の自動計算（`price_at_sale × quantity`）
  - `check_and_reduce_stock()`: 在庫減算処理
  - 在庫不足時のエラーハンドリング
  - XOR制約（productまたはproduct_setのどちらか一方のみ）
  - セット商品販売時の構成商品在庫減算

**設計理由**: 在庫減算はトランザクションの中核。誤った減算は在庫不整合を引き起こすため、エラーケースを含む徹底的なテストが必要。

### 2. ビューテスト

#### `RegisterSaleViewTest`
- **目的**: POS販売登録機能の完全性をテスト
- **カバー範囲**:
  - GET: フォーム表示（商品リスト、メンバーリスト）
  - POST: 単一商品の販売登録
  - POST: 複数商品の一括販売登録
  - エラーケース: 空カート、必須項目不足

**設計理由**: POSシステムのメイン機能。ユーザー入力のバリデーション、カートデータのパース、トランザクション作成が正しく動作することを保証。

#### `ProductCRUDViewTest`
- **目的**: 商品管理機能の完全性をテスト
- **カバー範囲**:
  - 商品一覧表示
  - 商品追加
  - 商品編集
  - 在庫補充

**設計理由**: 基本的なCRUD操作の正確性を保証。特に在庫補充は加算方式のため、正しい計算を確認。

#### `ProductSetCRUDViewTest`
- **目的**: セット商品管理機能の完全性をテスト
- **カバー範囲**:
  - セット一覧表示
  - セット追加（構成商品との同時作成）
  - セット編集（構成商品の差し替え）

**設計理由**: セット商品は構成商品との関連を持つため、関連データの整合性を保証する必要がある。

### 3. 統合テスト

#### `IntegrationTest`
- **目的**: システム全体の動作を確認
- **カバー範囲**:
  - 個別商品とセット商品を含む完全な販売フロー
  - 在庫減算の正確性（個別商品、セット構成商品）
  - セット在庫状況の動的計算

**設計理由**: 単体テストでは検出できない、複数コンポーネント間の連携問題を検出。実際の使用シナリオに近い形でテスト。

## 🚀 テスト実行方法

### 全テスト実行

```bash
# プロジェクトルートディレクトリで実行
python manage.py test team_tansaibou
```

### 特定のテストクラスのみ実行

```bash
# モデルテストのみ
python manage.py test team_tansaibou.tests.ProductModelTest

# ビューテストのみ
python manage.py test team_tansaibou.tests.RegisterSaleViewTest

# 統合テストのみ
python manage.py test team_tansaibou.tests.IntegrationTest
```

### 詳細な出力（verboseモード）

```bash
python manage.py test team_tansaibou --verbosity=2
```

### テストカバレッジ測定（オプション）

```bash
# coverageパッケージをインストール
pip install coverage

# カバレッジ測定付きでテスト実行
coverage run --source='team_tansaibou' manage.py test team_tansaibou

# レポート表示
coverage report

# HTMLレポート生成
coverage html
# htmlcov/index.html をブラウザで開く
```

## 📊 テストカバレッジ目標

| カテゴリ | 目標カバレッジ | 現状 |
|---------|--------------|------|
| モデル | 90%以上 | ✅ 達成 |
| ビュー | 80%以上 | ✅ 達成 |
| 全体 | 85%以上 | ✅ 達成 |

## 🔍 テスト設計のポイント

### 1. データベース分離

```python
class ProductModelTest(TestCase):
    databases = ['team_tansaibou']  # 専用DBを指定
```

**理由**: マルチデータベース構成のため、テスト実行時に正しいDBを使用する必要がある。

### 2. setUp メソッドの活用

```python
def setUp(self):
    """各テストメソッド実行前に呼ばれる"""
    self.product = Product.objects.using('team_tansaibou').create(...)
```

**理由**: テストデータの準備を共通化し、各テストの独立性を保つ。

### 3. トランザクション自動ロールバック

Djangoの`TestCase`は各テストメソッド実行後に自動的にデータベースをロールバックする。

**理由**: テスト間でデータが残らないため、テストの独立性が保証される。

### 4. エッジケースのテスト

```python
def test_check_stock_zero(self):
    """在庫ゼロの場合のcheck_stockテスト"""
    self.product.stock = 0
    self.assertFalse(self.product.check_stock(1))
    self.assertTrue(self.product.check_stock(0))
```

**理由**: 境界値（0, 1, 最大値）でのバグを早期発見。

## 🐛 よくある問題とトラブルシューティング

### 問題1: `no such table` エラー

```
django.db.utils.OperationalError: no such table: team_tansaibou_product
```

**解決策**: テストデータベースにマイグレーションを適用

```bash
python manage.py migrate --database=team_tansaibou
```

### 問題2: テスト失敗時のデバッグ

```python
# テスト内でprintデバッグ
def test_something(self):
    print(f"Product stock: {self.product.stock}")
    self.assertEqual(self.product.stock, 10)
```

**ヒント**: `--verbosity=2` で実行すると print 出力が表示される。

### 問題3: トランザクションテストの注意点

`atomic()` を使用するコードをテストする場合、テストメソッド内でも `atomic()` の動作を考慮する。

## 📝 テスト追加ガイドライン

新しい機能を追加する際は、以下の手順でテストを追加してください：

1. **モデルにビジネスロジックを追加した場合**:
   - `tests.py` に対応するモデルテストクラスを作成
   - メソッドごとに正常系・異常系のテストケースを追加

2. **ビューを追加した場合**:
   - GET/POSTリクエストのテストを追加
   - 成功時のリダイレクト先を確認
   - エラーケースのテストを追加

3. **新しい機能フローを追加した場合**:
   - 統合テストを追加して、エンドツーエンドの動作を確認

## 🎓 学習リソース

- [Django Testing Documentation](https://docs.djangoproject.com/en/4.2/topics/testing/)
- [Python unittest Documentation](https://docs.python.org/3/library/unittest.html)
- [Test-Driven Development (TDD)](https://en.wikipedia.org/wiki/Test-driven_development)

## ✅ チェックリスト

新しいコードをコミットする前に確認：

- [ ] 追加した機能に対応するテストケースを作成した
- [ ] 全テストが成功することを確認した (`python manage.py test team_tansaibou`)
- [ ] テストカバレッジが目標値を満たしている
- [ ] エッジケース（境界値、エラー条件）をテストした
- [ ] テストコードにコメントを追加し、何をテストしているか明確にした

---

**最終更新日**: 2025-11-17
**担当者**: Team Tansaibou
**バージョン**: 1.0
