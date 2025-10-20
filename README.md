# PBL App in 2025

このプロジェクトは、**複数チーム（team_a, team_b,
...）ごとに独立したアプリケーション・DB(SQLite)を運用**しつつ、テンプレートはプロジェクト直下で一元管理する構成です。

------------------------------------------------------------------------

## 📦 必要な環境

- Python 3.11+ 推奨
- [uv](https://github.com/astral-sh/uv)（依存解決・仮想環境管理に使用）

```bash
#### 各環境毎のインストール方法 ####
# On macOS and Linux.
curl -LsSf https://astral.sh/uv/install.sh | sh
# On Windows.
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

- SQLite3 (インストールは不要です)
- Git

------------------------------------------------------------------------

## 🚀 インストールとセットアップ

1. 仮想環境を作成

``` bash
uv venv
```

1. 依存関係をインストール

``` bash
uv sync
```

1. DBマイグレーション

``` bash
# 1. 各チーム共通で行ってください
python manage.py makemigrations
# 2. team_aは以下のコマンドを実行してください
python manage.py migrate --database=team_a
# 2. team_bは以下のコマンドを実行してください
python manage.py migrate --database=team_b
```

------------------------------------------------------------------------

## ▶️ 起動方法

### アプリ

``` bash
uv run python manage.py runserver
```

ブラウザで <http://127.0.0.1:8000/> にアクセス。

- `/` → 全体のIndex（各チームページへのリンク
- `/team-a/` → Team A Index
- `/team-b/` → Team B Index

### DB

```bash
# team_aの場合
python manage.py dbshell --database=team_a
# team_bの場合
python manage.py dbshell --database=team_b
```

------------------------------------------------------------------------

## 📂 ディレクトリ構造

```text
    .
    ├── .gitignore            # Git除外ファイル設定
    ├── .python-version       # pyenv用Pythonバージョン指定
    ├── manage.py
    ├── myproject/
    │   ├── __init__.py
    │   ├── asgi.py           # ASGI設定（非同期対応）
    │   ├── settings.py       # 複数DB/テンプレート設定
    │   ├── urls.py           # プロジェクト全体URLルーティング
    │   ├── views.py          # 全体Indexなど
    │   └── wsgi.py           # WSGI設定（本番デプロイ用）
    ├── routers.py            # DBルーター（app→DB割当）
    ├── templates/            # ★テンプレートはここに集約
    │   ├── team_a/
    │   │   └── members.html
    │   └── top.html          # 全体トップページ
    ├── team_a/               # Team A専用アプリ
    │   ├── __init__.py
    │   ├── admin.py          # Django管理画面設定
    │   ├── apps.py           # アプリケーション設定
    │   ├── db.sqlite3        # Team A専用DB
    │   ├── migrations/       # DBマイグレーションファイル
    │   │   ├── __init__.py
    │   │   └── 0001_initial.py
    │   ├── models.py
    │   ├── tests.py          # テストコード
    │   ├── urls.py
    │   └── views.py
    ├── docs/
    │   ├── NEW_TEAM_SETUP.md # 新チーム立ち上げ手順書
    │   └── UV_INSTALLATION.md # uvインストール手順書
    ├── pyproject.toml        # パッケージ管理（uv）
    └── uv.lock               # ロックファイル
```

------------------------------------------------------------------------

## ⚠️ 運用上の注意点

- **テンプレートは必ず `templates/` 配下に配置**してください。
    各アプリ配下の `templates/` は参照されません (`APP_DIRS=False`)。

- **チームごとにSQLiteを分離**しています。

  - `team_a` のモデルは `team_a/db.sqlite3` に保存
  - `team_b` のモデルは `team_b/db.sqlite3` に保存
  - `views.py` 内で `.using("team_a")` / `.using("team_b")`
        を明示してアクセスします。

- **異なるDB間のリレーションは不可**です（Djangoの複数DB制約）。
    チーム間でデータを共有する必要がある場合は、共通の `default` DB
    を利用するか、API経由で連携してください。

- **依存関係はuvで管理**します。

  - パッケージ定義: `pyproject.toml`
  - ロックファイル: `uv.lock`
  - チーム固有の依存が必要な場合は`pyproject.toml`のoptional-dependenciesを活用

- **マイグレーションはチームごとに実行**してください。

    ``` bash
    python manage.py migrate --database=team_a
    python manage.py migrate --database=team_b
    ```
