# PBL App in 2025

このプロジェクトは、**複数チーム（team_a, team_b,
...）ごとに独立したアプリケーション・DB(SQLite)を運用**しつつ、テンプレートはプロジェクト直下で一元管理する構成です。

------------------------------------------------------------------------

## 📦 必要な環境

- Python 3.9+ 推奨
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

------------------------------------------------------------------------

## 🔐 認証/認可（お試し）

本プロジェクトでは Django 標準認証（`django.contrib.auth`）を使い、ユーザー/セッションは `default` DB で一元管理しつつ、
各チームアプリ配下（例: `/team_USL/`）へのアクセス可否を **Group（グループ）** で分ける構成を試せます。

トップページ（`/`）右上にもログイン/ログアウト導線があります。

### 1) ログインURL

- ログイン: `/accounts/login/`
- ログアウト: `/accounts/logout/`

### 2) チーム用グループの作成

チームアプリと同名の Group（例: `team_USL`）を作成し、ユーザーを所属させます。

一括作成（推奨）:
```bash
python manage.py sync_team_groups
```

### 3) admin でユーザーをグループに所属させる

1. `python manage.py createsuperuser` で管理ユーザー作成
2. `/admin/` にログイン
3. Users から対象ユーザーを開き、Groups にチーム名（例: `team_USL`）を追加

### 4) アクセス制御の仕様（ミドルウェア）

- `/admin/` と `/accounts/` と `/` は除外
- それ以外で、URLの先頭セグメントが「保護対象アプリ名」に一致する場合:
  - 未ログイン → ログイン画面へリダイレクト
  - ログイン済みでも、同名Group所属（またはsuperuser）でない → 403

保護対象アプリ名は `pbl_project/settings.py` の `TEAM_AUTHZ_PROTECTED_APP_LABELS` で指定できます。
`None` の場合は、`routers.py` に登録されている全チームアプリが対象になります。

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
├── .gitignore               # Git除外ファイル設定
├── .python-version          # 使用するPythonバージョン(pyenv)
├── README.md
├── .github/
│   └── workflows/
│       └── deploy.yaml      # self-hosted runner 用デプロイワークフロー
├── manage.py
├── main.py
├── db.sqlite3               # default DB
├── .venv/                   # 仮想環境(必要に応じて)
├── pbl_project/             # プロジェクト設定モジュール
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py          # 複数DB / テンプレート設定
│   ├── urls.py              # 全体URLルーティング
│   └── wsgi.py
├── routers.py               # DBルーター（app→DB割当）
├── authz/                   # 認可補助（Group一括作成コマンドなど）
├── templates/               # ★テンプレートはここに集約
│   ├── top.html             # 全体トップページ
│   ├── registration/
│   │   └── login.html        # ログイン画面（/accounts/login/）
│   └── team_a/
│       └── members.html
├── docs/                    # ドキュメント類
│   ├── HOW_TO_DATA_INSERT_BY_MIGRATION.md
│   ├── HOW_TO_DEPLOY.md
│   ├── HOW_TO_RESOLVE_CONFLICTS.md
│   ├── NEW_TEAM_SETUP.md
│   ├── SQLITE3_INSTALLATION.md
│   └── UV_INSTALLATION.md
├── images/                  # 画像リソース
├── team_a/                  # 各チーム用アプリ（team_a / team_b ...）
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── db.sqlite3
│   ├── migrations/
│   │   ├── __init__.py
│   │   └── 0001_initial.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── team_b/
│   └── ...                  # 他チームも同様の構成
├── pyproject.toml           # パッケージ管理(uv)
├── uv.lock                  # ロックファイル
└── work/                    # 補助スクリプト等
```

------------------------------------------------------------------------

## ⚠️ 運用上の注意点

- **原則としてテンプレートは `templates/` 配下に配置**してください。
    本プロジェクトはテンプレートをプロジェクト直下で集約する方針です。
    なお、Django標準の admin/auth などが持つ組み込みテンプレートは読み込めるように設定されています。

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
