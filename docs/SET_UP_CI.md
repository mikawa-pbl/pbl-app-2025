# CIのセットアップ手順

## CI(Continuous Integration)とは?

CIとは、本番環境に移す前に、コードの品質を保証するための自動化されたテストプロセスです。
CIを使用することによって2つのメリットがあります。
1つは、開発環境では問題がなかったのに本番環境にデプロイする際に問題が生じることをなくすことができることです。もう一つは、プロダクト全体の品質を保証することができることです。



## CIの設定手順


### 1. yamlファイルの作成

`.github/workflows/<チーム名>.yaml`を作成し、以下の内容を記述してください。

```yaml
name: Test <チーム名>

on:
  pull_request:
    branches:
      - main
    paths:
      - "<チームのディレクトリ名>/**"

jobs:
  call-workflow:
    uses: ./.github/workflows/reusable_team_ci.yaml
    with:
      target_app: "<チーム名>"
```

### 2. `pbl_project/settings.py`の設定（重要）

テスト実行時のデータベース依存関係エラー（Circular dependency）を防ぐため、pbl_projects/settings.pyの`DATABASES`に以下を追記してください。

```python
    '<チーム名>': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / '<チーム名>' / 'db.sqlite3',
        # ▼ここから追加
        'TEST': {
            'DEPENDENCIES': [],  # 依存関係を空に設定
        },
        # ▲ここまで追加
    },
```



### 3. テストファイルの作成(任意)

CIでは、`<チーム名>/tests.py` に記述されたテストが自動的に実行されます。
新しい機能を実装した際は、その機能が正しく動作することを保証するためにテストを作成することを推奨します。

**`tests.py` の記述例:**

```python
from django.test import TestCase
from .models import MyModel  # 自チームのモデルをインポート

class MyTeamTests(TestCase):
    # 【重要】自チームのデータベースエイリアスを指定
    # これを指定しないと、デフォルトのデータベースが使用され、エラーになる可能性があります
    databases = {'<チーム名>'}

    def setUp(self):
        # テストデータの作成（テスト実行のたびにリセットされます）
        MyModel.objects.create(name="test data")

    def test_example(self):
        # テストの実行
        count = MyModel.objects.count()
        self.assertEqual(count, 1)
```


---

## CIの実行の流れとチェック内容

このCIは、mainブランチへのプルリクエスト時に、`<チームのディレクトリ名>`以下のファイルに変更があった場合のみ実行されます。
CIは以下の順序で実行され、問題があればその時点で失敗（Fail）します。

### 1. makemigrationsの実行チェック
- **内容**: `models.py` の変更に対するマイグレーションファイルが作成されているか、整合性が取れているかを確認します（`--check` オプションを使用）。
- **落ちる例**:
  - `models.py` にフィールドを追加したが、`makemigrations` を実行してファイルをコミットし忘れた場合。
  - **エラー**: `SystemCheckError: System check identified some issues...`

### 2. database migrationの実行
- **内容**: 実際にデータベースへのマイグレーションを適用し、SQLエラーが発生しないかを確認します。
- **落ちる例**:
  - マイグレーションファイルの依存関係がおかしい場合。
  - 定義されていないテーブルを参照している場合（例：`OperationalError: no such table: ...`）。

### 3. サーバー起動チェック
- **内容**: 開発サーバー（`runserver`）をバックグラウンドで起動し、HTTPリクエストに応答するかを確認します。
- **落ちる例**:
  - `views.py` や `urls.py` に `ImportError` や `SyntaxError` があり、Djangoが起動しない場合。
  - **エラー**: `Server process died.` / `Server failed to respond.`

### 4. テストの実行
- **内容**: `tests.py` に記述されたユニットテストを実行します。
- **落ちる例**:
  - 実装したロジックがテストの期待値と異なる場合。
  - **エラー**: `AssertionError`

