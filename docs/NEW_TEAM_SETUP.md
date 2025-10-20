
# 新チーム立ち上げ手順書（アプリ初期セットアップ）

この文書は、**新しいチームが立ち上がったとき**に、既存のマルチチーム Django プロジェクトへ **新チーム用アプリを追加して動かす**までの初期セットアップ手順をまとめたものです。
前提：テンプレートはプロジェクト直下 `templates/` のみ参照（`APP_DIRS=False`）、チームごとに **独立した SQLite** を使用、依存関係は `uv` で管理する運用です。

---

## 0. 前提 / 必要なツール

- Python 3.11+
- uv（依存解決・仮想環境管理）
- SQLite3（Windows で `dbshell` を使う場合は `sqlite3.exe` を PATH に通すと便利）

### uv のインストール確認

まず、uv がインストールされているか確認します：

```bash
uv --version
```

バージョンが表示されれば OK です（例: `uv 0.x.x`）。
コマンドが見つからない場合は、[UV_INSTALLATION.md](UV_INSTALLATION.md) を参照してインストールしてください。

### SQLite3 のインストール（Windows のみ）

**macOS / Linux の場合：** SQLite3 はシステムに標準搭載されているため、この章はスキップしてください。

**Windows の場合：** Django の `dbshell` コマンドを使用するために、SQLite3 のコマンドラインツールをインストールします。

#### インストール手順

1. PowerShell を**管理者として実行**します

2. 以下のコマンドを実行します：

   ```powershell
   winget install --scope machine SQLite.SQLite
   ```

3. インストール完了後、**PowerShell を再起動**します
   - VS Code のターミナルを使用している場合は、**VS Code も再起動**してください

4. インストール確認：

   ```powershell
   sqlite3 --version
   ```

---

## 1. リポジトリのクローン（まだクローンしていない場合）

リポジトリをまだクローンしていない場合は、まずクローンしたいディレクトリに移動します：

```bash
cd ~/Documents  # 例: Documentsフォルダにクローンする場合
```

次に、以下のコマンドを実行してリポジトリをクローンします：

```bash
git clone https://github.com/mikawa-pbl/pbl-app-2025.git
```

クローン後、プロジェクトディレクトリに移動します：

```bash
cd pbl-app-2025
```

※ 既にクローン済みの場合は、この章はスキップしてください。

---

## 2. 仮想環境のセットアップと依存関係のインストール

プロジェクトディレクトリ(`pbl-app-sample`ディレクトリ)で以下のコマンドを実行し、Python 仮想環境を作成して必要なライブラリをインストールします：

```bash
uv sync
```

このコマンドは以下を自動的に行います：

- Python 仮想環境（venv）の作成
- `pyproject.toml` に記載された依存関係のインストール
- 開発に必要なパッケージのセットアップ

### ⚠️ 重要：仮想環境の確認

`uv sync` 実行後、**必ずターミナルの一番左に `(pbl-app-sample)` と表示されていることを確認してください。**

```bash
(pbl-app-sample) ユーザー名@PC名:~/Documents/pbl-app-sample$
```

この表示があれば、仮想環境が有効化されています。**以降のすべてのコマンド（manage.py の実行、マイグレーション、サーバー起動など）は、必ずこの仮想環境内で実行してください。**

#### 仮想環境が自動で有効にならない場合

`(pbl-app-sample)` が表示されない場合は、以下のいずれかの方法で対処してください：

##### 方法1: VS Code の設定を確認

[UV_INSTALLATION.md](UV_INSTALLATION.md) の「VS Code の設定（全 OS 共通）」セクションを参照し、Python 環境の自動有効化設定を行ってください。

##### 方法2: 手動で仮想環境を有効化

以下のコマンドで手動で仮想環境を有効化できます：

- **Windows (PowerShell):**

  ```PowerShell
  .venv\Scripts\Activate.ps1
  ```

- **macOS / Linux:**

  ```bash
  source .venv/bin/activate
  ```

> **📌 今後の開発でも常に確認すること：**
> ターミナルを新しく開くたびに、`(pbl-app-sample)` の表示を確認してください。表示されていない場合は、プロジェクトディレクトリで再度 `uv sync` を実行するか、VS Code で新しいターミナルを開き直してください。

※ 既にプロジェクトの仮想環境と依存が入っている場合は、この章はスキップ可。

---

## 3. ブランチを切る

新しい作業用ブランチを作成します。**ブランチ名は先頭にチーム名で階層を作る**ようにしてください：

```bash
git checkout -b <チーム名>/<作業内容>
```

例：チーム名が `team_terrace` で、初期セットアップを行う場合

```bash
git checkout -b team_terrace/setup
```

---

## 4. アプリを作成（チーム用アプリ）

例では **team_terrace** とします。`team_terrace`を各チーム名に合わせて修正してください

```bash
uv run python manage.py startapp team_terrace
```

作成直後の構成（抜粋）:

```text
team_terrace/
├── __init__.py
├── admin.py
├── apps.py
├── migrations/
│   └── __init__.py
├── models.py      # ← モデル定義
├── tests.py
├── urls.py        # ← ファイルを新規作成（後述）
└── views.py       # ← ビュー実装
```

---

## 5. `settings.py` にアプリとDBを追加

`pbl_project/settings.py`:

```python
INSTALLED_APPS = [
    # ... 既存
    'team_terrace',  # ← 追加
]
```

```python
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

DATABASES = {
    # ... 既存 default, team_a, team_b
    'team_terrace': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'team_terrace' / 'db.sqlite3',
    },
}
```

> ※ テンプレート設定は既に `APP_DIRS=False` & `DIRS=[BASE_DIR / "templates"]` の想定。変更不要。

---

## 6. DBルーターにチームを追加

`routers.py` に `team_terrace` を登録：

```python
class TeamPerAppRouter:
    app_to_db = {
        'team_a': 'team_a',
        'team_b': 'team_b',
        'team_terrace': 'team_terrace',  # ← 追加
    }
    # 以降のメソッドは既存のまま（db_for_read/write, allow_relation, allow_migrate）
```

---

## 7. URL を親ルータに追加

`pbl_project/urls.py`：

```python
from django.urls import path, include

urlpatterns = [
    # ... 既存
    path('team_terrace/', include('team_terrace.urls')),  # ← 追加
]
```

---

## 8. チーム用 URLs / Views / Models を雛形化

### `team_terrace/urls.py`（新規ファイルを作成してください）

```python
from django.urls import path
from . import views

app_name = "team_terrace"
urlpatterns = [
    path('', views.index, name='index'),
    path('members/', views.members, name='members'),
]
```

### `team_terrace/views.py`

```python
from django.shortcuts import render
from .models import Member

def index(request):
    return render(request, 'teams/team_terrace/index.html')

def members(request):
    qs = Member.objects.using('team_terrace').all()  # ← team_terrace DBを明示
    return render(request, 'teams/team_terrace/members.html', {'members': qs})
```

### `team_terrace/models.py`（例）

```python
from django.db import models

class Member(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"
```

---

## 9. プロジェクト直下テンプレートを用意（**APP_DIRS=False 運用**）

```text
templates/
└── teams/
    └── team_terrace/
        ├── index.html
        └── members.html
```

**`templates/teams/team_terrace/index.html`（例）**

```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>Team Terrace</title></head>
<body>
<h1>Team Terrace</h1>
<p><a href="/team_terrace/members/">メンバー一覧</a></p>
</body>
</html>
```

**`templates/teams/team_terrace/members.html`（例）**

```html
<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8"><title>Team Terrace Members</title></head>
<body>
  <h1>Team Terrace Members</h1>
  <ul>
    {% for member in members %}
      <li>{{ member.last_name }} {{ member.first_name }}</li>
    {% empty %}
      <li>データがありません</li>
    {% endfor %}
  </ul>
  <p><a href="/team_terrace/">Team Terrace トップへ</a></p>
</body></html>
```

> 既存のトップ（`templates/index.html`）にも Team Terrace へのリンクを追記推奨。

---

## 10. プロジェクトポータルページ（index）にチームリンクを追加

新チーム用のページができたら、**プロジェクト全体のトップページ (`pbl_project/views.py` の `index`) に新チームをコンテキストとして追加**してください。これにより、全体トップからチームページへ遷移できるようになります。

### `pbl_project/views.py`

```python
from django.shortcuts import render

def index(request):
    teams = [
        # データサンプル
        # {"name": "Team A", "url": "/team_a/"},
        {"name": "Team Terrace", "url": "/team_terrace/"},  # ← 新チームを追加
    ]
    return render(request, "top.html", {"teams": teams})
```

---

## 11. マイグレーション

マイグレーションファイル作成：

```bash
uv run python manage.py makemigrations
```

反映（team_terrace DB に対して）：

```bash
uv run python manage.py migrate --database=team_terrace
```

---

## 12. 動作確認

### 12.1 サーバ起動

```bash
uv run python manage.py runserver
```

- `/team_terrace/` にアクセスして Team Terrace の index が表示されること
- `/team_terrace/members/` が空一覧で表示されること

### 12.2 データ投入

**dbshell で直接 INSERT**

```bash
uv run python manage.py dbshell --database=team_terrace
```

```sql
INSERT INTO team_terrace_member (first_name, last_name) VALUES ('太郎', '山田');
INSERT INTO team_terrace_member (first_name, last_name) VALUES ('花子', '佐藤');
SELECT * FROM team_terrace_member;
```

リロードして `/team_terrace/members/` にデータが出ればOK。

---

## 13. コミット & プッシュ

```bash
git add .
git commit -m "Team Terraceのsetupが完了"
git push origin team_terrace/setup
```

PR を作成し、レビュー依頼。

---

## よくあるエラー / チェックリスト

- [ ] `routers.py` に新チームのエイリアスを追加したか（`app_to_db` に `team_terrace`）
- [ ] `DATABASES['team_terrace']` の `NAME` パスが `BASE_DIR / 'team_terrace' / 'db.sqlite3'` になっているか
- [ ] ビューで `.using('team_terrace')` を付けているか（付け忘れると `default` に書かれる）
- [ ] `APP_DIRS=False` のため、**アプリ配下の `templates/` は参照されない**（必ずプロジェクト直下に配置）
- [ ] 必要に応じて `pyproject.toml` にチーム固有の依存を追加したか
- [ ] マイグレーションを **`--database=team_terrace`** で実行したか

---

## 完了！

ここまでで、新チーム（例：team_terrace）のアプリ追加〜DB作成〜URL配線〜テンプレート連携までが完了します。
同様の手順で、他の新チームも追加可能です。