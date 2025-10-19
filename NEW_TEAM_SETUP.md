
# 新チーム立ち上げ手順書（アプリ初期セットアップ）

この文書は、**新しいチームが立ち上がったとき**に、既存のマルチチーム Django プロジェクトへ **新チーム用アプリを追加して動かす**までの初期セットアップ手順をまとめたものです。
前提：テンプレートはプロジェクト直下 `templates/` のみ参照（`APP_DIRS=False`）、チームごとに **独立した SQLite** を使用、依存関係は `uv` で管理する運用です。

---

## 0. 前提 / 必要なツール

- Python 3.11+
- uv（依存解決・仮想環境管理）
  - macOS / Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
  - Windows (PowerShell): `irm https://astral.sh/uv/install.ps1 | iex`
- SQLite3（Windows で `dbshell` を使う場合は `sqlite3.exe` を PATH に通すと便利）

※ 既にプロジェクトの仮想環境と依存が入っていれば、この章はスキップ可。

---

## 1. ブランチを切る

```bash
git switch -c setup/team_terrace-bootstrap
```

---

## 2. アプリを作成（チーム用アプリ）

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

## 3. SQLite ファイルを配置（SKIP可能）

**ファイルがなくてもOK**（マイグレーション時に作成されます）。

```text
team_terrace/db.sqlite3  （ファイルが無くても可）
```

---

## 4. `settings.py` にアプリとDBを追加

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

## 5. DBルーターにチームを追加

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

## 6. URL を親ルータに追加

`pbl_project/urls.py`：

```python
from django.urls import path, include

urlpatterns = [
    # ... 既存
    path('team_terrace/', include('team_terrace.urls')),  # ← 追加
]
```

---

## 7. チーム用 URLs / Views / Models を雛形化

### `team_terrace/urls.py`（新規ファイルを作成してください）

```python
from django.urls import path
from . import views

app_name = "team_terrace"
urlpatterns = [
    path('', views.index, name='index'),
    path('items/', views.items, name='items'),
]
```

### `team_terrace/views.py`

```python
from django.shortcuts import render
from .models import Item

def index(request):
    return render(request, 'teams/team_terrace/index.html')

def items(request):
    qs = Item.objects.using('team_terrace').all()  # ← team_terrace DBを明示
    return render(request, 'teams/team_terrace/items.html', {'items': qs})
```

### `team_terrace/models.py`（例）

```python
from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=100)
    memo = models.TextField(blank=True, default='')

    def __str__(self):
        return self.name
```

---

## 8. プロジェクト直下テンプレートを用意（**APP_DIRS=False 運用**）

```text
templates/
└── teams/
    └── team_terrace/
        ├── index.html
        └── items.html
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
<p><a href="/team-terrace/items/">items 一覧</a></p>
</body>
</html>
```

**`templates/teams/team_terrace/items.html`（例）**

```html
<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8"><title>Team C Items</title></head>
<body>
  <h1>Team Terrace Items</h1>
  <ul>
    {% for it in items %}
      <li>{{ it.name }} - {{ it.memo }}</li>
    {% empty %}
      <li>データがありません</li>
    {% endfor %}
  </ul>
  <p><a href="/team_terrace/">Team Terrace トップへ</a></p>
</body></html>
```

> 既存のトップ（`templates/index.html`）にも Team Terrace へのリンクを追記推奨。

---

## 9 プロジェクトポータルページ（index）にチームリンクを追加

新チーム用のページができたら、**プロジェクト全体のトップページ (`pbl_project/views.py` の `index`) に新チームをコンテキストとして追加**してください。これにより、全体トップからチームページへ遷移できるようになります。

### `pbl_project/views.py`

```python
from django.shortcuts import render

def index(request):
    teams = [
        # データサンプル
        # {"name": "Team A", "url": "/team_a/"},
        {"name": "Team Terrace", "url": "/team-terrace/"},  # ← 新チームを追加
    ]
    return render(request, "top.html", {"teams": teams})

---

## 10. マイグレーション

マイグレーションファイル作成：

```bash
uv run python manage.py makemigrations
```

反映（team_terrace DB に対して）：

```bash
uv run python manage.py migrate --database=team_terrace
```

---

## 11. 動作確認

### 11.1 サーバ起動

```bash
uv run python manage.py runserver
```

- `/team_terrace/` にアクセスして Team Terrace の index が表示されること
- `/team_terrace/items/` が空一覧で表示されること

### 11.2 データ投入

**dbshell で直接 INSERT**

```bash
uv run python manage.py dbshell --database=team_terrace
```

```sql
INSERT INTO team_terrace_item (name, memo) VALUES ('Sample', 'first row');
SELECT * FROM team_terrace_item;
```

リロードして `/team_terrace/items/` にデータが出ればOK。

---

## 12. コミット & プッシュ

```bash
git add .
git commit -m "Team Terraceのsetupが完了"
git push origin setup/team_terrace-bootstrap
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

## 付録：OS別の補足

### uv のインストール

- macOS / Linux:

  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

- Windows (PowerShell):

  ```powershell
  irm https://astral.sh/uv/install.ps1 | iex
  ```

### dbshell（SQLite CLI がない場合）

- Windows で `dbshell` が動かない場合は、Django シェルで代替：

  ```bash
  python manage.py shell
  ```

  ```python
  from team_terrace.models import Item
  list(Item.objects.using('team_terrace').all())
  ```

---

## 完了！

ここまでで、新チーム（例：team_terrace）のアプリ追加〜DB作成〜URL配線〜テンプレート連携までが完了します。
同様の手順で、他の新チームも追加可能です。