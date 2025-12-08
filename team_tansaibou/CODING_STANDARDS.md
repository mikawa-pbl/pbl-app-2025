# Team Tansaibou - コーディング規約

## 📋 目的

このドキュメントは、Team TansaibouのPOSシステム開発における統一されたコーディング規約を定めます。

### 規約を設ける理由

1. **可読性向上**: 誰が書いたコードでも読みやすく理解しやすい
2. **保守性向上**: 将来の変更や修正が容易になる
3. **バグ削減**: 一貫したパターンによりバグを防止
4. **チーム効率化**: レビューやペアプログラミングがスムーズに

## 🎯 評価基準との対応

この規約は以下の評価基準達成を目指します：

- **Lv3 (貢献)**: コードの重複削減、責任分離、設計判断の明確化
- **Lv4 (促進)**: チーム標準の確立、コードレビュー文化、継続的改善

## 1️⃣ Python コーディング規約

### 1.1 基本方針

- **PEP 8準拠**: Pythonの標準スタイルガイドに従う
- **日本語コメント可**: ビジネスロジックは日本語で説明してOK
- **英語命名推奨**: 変数名・関数名は英語を推奨（日本語も許容）

### 1.2 インデント

```python
# ✅ 良い例: 4スペースインデント
def calculate_total(items):
    total = 0
    for item in items:
        total += item.price * item.quantity
    return total

# ❌ 悪い例: タブやスペース混在
def calculate_total(items):
	total = 0  # タブ
    for item in items:  # スペース
        total += item.price
```

**ルール**: インデントは4スペース、タブは使用しない

### 1.3 命名規則

| 対象 | 規則 | 例 |
|------|------|-----|
| モジュール・パッケージ | 小文字、アンダースコア区切り | `team_tansaibou`, `models.py` |
| クラス | パスカルケース | `Product`, `TransactionItem` |
| 関数・メソッド | スネークケース | `register_sale()`, `get_stock_status()` |
| 変数 | スネークケース | `total_amount`, `product_id` |
| 定数 | 大文字アンダースコア区切り | `DB_NAME`, `MAX_QUANTITY` |
| プライベート変数 | アンダースコア始まり | `_internal_cache` |

```python
# ✅ 良い例
class ProductSet:
    def get_stock_status(self):
        min_stock = self._calculate_min_stock()
        return min_stock

# ❌ 悪い例
class productSet:  # クラス名がスネークケース
    def GetStockStatus(self):  # メソッド名がパスカルケース
        MinStock = self._CalculateMinStock()  # 変数名がパスカルケース
```

### 1.4 docstring（ドキュメント文字列）

**必須レベル**:
- ✅ モジュール: 必須
- ✅ クラス: 必須
- ✅ パブリック関数/メソッド: 必須
- ⚠️ プライベート関数/メソッド: 推奨

**フォーマット**:

```python
def register_sale(request):
    """
    販売登録画面（POSレジ）

    機能:
    - GET: POS画面を表示（商品ボタン、カート、会計フォーム）
    - POST: 複数商品の一括販売登録と在庫減算

    設計方針:
    - オフライン対応: JavaScriptでカート管理し、会計時のみサーバー通信
    - トランザクション保証: atomic()で在庫減算の一貫性を確保

    Args:
        request: HTTPリクエストオブジェクト
            POST時の必須パラメータ:
                - transaction_date: 取引日時（ISO形式）
                - payment_method: 支払方法
                - recorded_by: 担当者ID
                - cart_items: カート内商品のJSON配列

    Returns:
        HttpResponse: POS画面（GET時）または販売履歴へリダイレクト（POST成功時）

    Raises:
        ValueError: カート空、必須項目不足
        json.JSONDecodeError: カートデータ形式不正
    """
    # 実装...
```

**ポイント**:
- **機能**: 何をするか
- **設計方針**: なぜそのように実装したか
- **Args**: 引数の説明
- **Returns**: 戻り値の説明
- **Raises**: 発生する可能性のある例外

## 2️⃣ Django 固有の規約

### 2.1 データベースアクセス

**マルチデータベース対応**:

```python
# ✅ 良い例: DB_NAME定数を使用
DB_NAME = 'team_tansaibou'

def product_list(request):
    products = Product.objects.using(DB_NAME).all()

# ❌ 悪い例: ハードコード
def product_list(request):
    products = Product.objects.using('team_tansaibou').all()
```

**ルール**: データベース名は定数`DB_NAME`を使用

### 2.2 クエリ最適化

**N+1問題対策**:

```python
# ✅ 良い例: select_related/prefetch_relatedを使用
transactions = Transaction.objects.using(DB_NAME).select_related(
    'recorded_by'
).prefetch_related(
    'items__product',
    'items__product_set'
)

# ❌ 悪い例: 関連データを都度取得（N+1問題）
transactions = Transaction.objects.using(DB_NAME).all()
for trans in transactions:
    print(trans.recorded_by.name)  # 毎回クエリ発行
    for item in trans.items.all():  # 毎回クエリ発行
        print(item.product.name)
```

**ルール**:
- 1対1、多対1: `select_related()`
- 1対多、多対多: `prefetch_related()`

### 2.3 トランザクション管理

```python
# ✅ 良い例: atomic()でデータ整合性を保証
from django.db import transaction as db_transaction

with db_transaction.atomic(using=DB_NAME):
    trans = Transaction.objects.using(DB_NAME).create(...)
    for item in cart_data:
        TransactionItem.objects.using(DB_NAME).create(...)

# ❌ 悪い例: トランザクション未使用（途中でエラーになると不整合）
trans = Transaction.objects.using(DB_NAME).create(...)
for item in cart_data:
    TransactionItem.objects.using(DB_NAME).create(...)  # エラー発生時、transだけ残る
```

**ルール**: 複数の関連データを作成・更新する場合は必ず`atomic()`を使用

### 2.4 モデル設計

**ビジネスロジックはモデルに**:

```python
# ✅ 良い例: ビジネスロジックをモデルメソッドに
class ProductSet(models.Model):
    def get_stock_status(self):
        """在庫状況を取得（最も少ない構成商品から計算）"""
        if not self.items.exists():
            return 0
        return min(
            item.product.stock // item.quantity
            for item in self.items.all()
        )

# ビュー
stock = product_set.get_stock_status()

# ❌ 悪い例: ビューにビジネスロジックを記述
def productset_list(request):
    product_sets = ProductSet.objects.using(DB_NAME).all()
    for ps in product_sets:
        # ビューで在庫計算（再利用性が低い）
        min_stock = min(item.product.stock // item.quantity for item in ps.items.all())
```

**ルール**: 再利用可能なビジネスロジックはモデルメソッドに実装

## 3️⃣ エラーハンドリング

### 3.1 例外処理

```python
# ✅ 良い例: 具体的な例外をキャッチ
try:
    product = Product.objects.using(DB_NAME).get(id=product_id)
except Product.DoesNotExist:
    messages.error(request, '商品が見つかりません')
    return redirect('team_tansaibou:product_list')

# ❌ 悪い例: 広範囲の例外をキャッチ
try:
    product = Product.objects.using(DB_NAME).get(id=product_id)
except Exception:  # 何のエラーか不明
    messages.error(request, 'エラーが発生しました')
```

**ルール**: 具体的な例外をキャッチし、適切に処理

### 3.2 ユーザーフィードリーなメッセージ

```python
# ✅ 良い例: ユーザーが理解できるメッセージ
messages.error(request, '商品「りんご」の在庫が不足しています（必要: 5個、在庫: 2個）')

# ❌ 悪い例: 技術的すぎるメッセージ
messages.error(request, 'ValidationError: Stock insufficient')
```

## 4️⃣ テスト規約

### 4.1 テストファイル

- **ファイル名**: `tests.py` または `tests/` ディレクトリ
- **テストクラス名**: `<対象>Test` （例: `ProductModelTest`）
- **テストメソッド名**: `test_<テスト内容>`（例: `test_check_stock_sufficient`）

### 4.2 テストの独立性

```python
# ✅ 良い例: setUpでテストデータ準備
class ProductModelTest(TestCase):
    databases = ['team_tansaibou']

    def setUp(self):
        """各テストメソッド実行前に呼ばれる"""
        self.product = Product.objects.using('team_tansaibou').create(...)

    def test_check_stock_sufficient(self):
        self.assertTrue(self.product.check_stock(5))

    def test_check_stock_insufficient(self):
        self.assertFalse(self.product.check_stock(100))

# ❌ 悪い例: テスト間で状態共有（前のテストに依存）
class ProductModelTest(TestCase):
    def test_create_product(self):
        self.product = Product.objects.create(...)  # クラス変数に保存

    def test_check_stock(self):
        # test_create_productの実行に依存
        self.assertTrue(self.product.check_stock(5))
```

**ルール**: 各テストは独立して実行可能であること

## 5️⃣ Git コミット規約

### 5.1 コミットメッセージ

**フォーマット**:

```
<type>: <subject>

<body>

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**type の種類**:
- `feat`: 新機能追加
- `fix`: バグ修正
- `refactor`: リファクタリング（機能変更なし）
- `test`: テスト追加・修正
- `docs`: ドキュメント変更
- `style`: コードスタイル修正（空白、フォーマット等）

**例**:

```
feat: セット商品の在庫状況表示機能を追加

- ProductSet.get_stock_status()で構成商品の最小在庫を計算
- セット商品一覧画面に在庫バッジを追加（緑/黄/赤）
- 各構成商品の在庫数も表示

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

### 5.2 コミット単位

- **1機能 = 1コミット**: 関連する変更をまとめる
- **小さなコミット**: レビューしやすいサイズに分割
- **動作するコード**: 各コミット時点でテストが通ること

## 6️⃣ コードレビューガイドライン

### 6.1 レビュー観点

チェックポイント:

- [ ] **機能性**: 要件を満たしているか
- [ ] **コーディング規約**: この規約に準拠しているか
- [ ] **テスト**: 適切なテストケースがあるか
- [ ] **パフォーマンス**: N+1問題などがないか
- [ ] **セキュリティ**: SQL インジェクション、XSS等の脆弱性がないか
- [ ] **ドキュメント**: docstringが適切か

### 6.2 レビューコメント例

```markdown
# ✅ 建設的なコメント
「`select_related()`を使うとN+1問題を防げます。以下のように修正してはどうでしょうか？」

# ❌ 否定的なコメント
「これはダメです。」
```

**ルール**: 改善案を具体的に提案する

## 7️⃣ セキュリティ規約

### 7.1 SQL インジェクション対策

```python
# ✅ 良い例: ORM使用（自動エスケープ）
Product.objects.filter(name=user_input)

# ❌ 悪い例: 生SQL（エスケープなし）
cursor.execute(f"SELECT * FROM product WHERE name = '{user_input}'")
```

### 7.2 XSS対策

Djangoテンプレートは自動でHTMLエスケープするため、基本的に安全。

```html
<!-- ✅ 自動エスケープされる -->
<p>{{ product.name }}</p>

<!-- ⚠️ エスケープ無効化（注意して使用） -->
<p>{{ product.description|safe }}</p>
```

**ルール**: `|safe`フィルタは信頼できるデータのみに使用

### 7.3 CSRF対策

```html
<!-- ✅ CSRFトークン必須 -->
<form method="post">
    {% csrf_token %}
    ...
</form>
```

**ルール**: POSTフォームには必ず`{% csrf_token %}`を含める

## 8️⃣ パフォーマンス規約

### 8.1 データベースクエリ

- **件数制限**: 大量データは`[:100]`などで制限
- **インデックス**: 頻繁に検索するフィールドにindexを追加
- **集計はDB側で**: `aggregate()`, `annotate()`を活用

### 8.2 キャッシング

将来的な改善案として、頻繁にアクセスされるデータはキャッシュを検討。

## 9️⃣ 継続的改善

### 9.1 定期レビュー

- **頻度**: 月1回、この規約を見直し
- **更新**: チームで議論して規約を改善

### 9.2 学習リソース

- [PEP 8 -- Style Guide for Python Code](https://pep8.org/)
- [Django Coding Style](https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/coding-style/)
- [Django Best Practices](https://django-best-practices.readthedocs.io/)

## ✅ チェックリスト

コミット前の確認項目:

- [ ] PEP 8に準拠しているか（`flake8`でチェック可能）
- [ ] docstringを追加したか
- [ ] テストケースを追加したか
- [ ] テストが全て通るか
- [ ] マイグレーションファイルを作成したか（モデル変更時）
- [ ] セキュリティ上の問題がないか

---

**策定日**: 2025-11-17
**担当**: Team Tansaibou
**バージョン**: 1.0
**次回レビュー予定**: 2025-12-17
