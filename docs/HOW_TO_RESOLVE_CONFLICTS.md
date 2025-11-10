# コンフリクト解消手順書

## 背景：なぜコンフリクトが発生するのか

[NEW_TEAM_SETUP.md](NEW_TEAM_SETUP.md) の手順に従って各チームがセットアップ作業を進めると、以下の **4つのファイル** を編集することになります：

1. `pbl_project/settings.py` - `INSTALLED_APPS` と `DATABASES` にチームを追加
2. `pbl_project/urls.py` - チームのURLパターンを追加
3. `pbl_project/views.py` - プロジェクトトップページにチームリンクを追加
4. `routers.py` - DBルーターにチームを追加

複数チームが同じファイルの同じ箇所を編集するため、**最初のチームがマージされた後、後続のチームは必ずコンフリクトが発生します。**

このドキュメントでは、コンフリクトを解消する **2つの方法** を説明します：

- **方法1：GitHub Web UI で解消する方法（簡単・推奨）**
- **方法2：ローカルで解消する方法（詳細な制御が可能）**

---

## 前提条件

- main ブランチには **ブランチ保護** がかかっており、直接プッシュできません
- コンフリクトは Pull Request (PR) を作成した後に発生します
- 必ず PR の画面でコンフリクトの有無を確認してください
- この手順書では、あなたのチーム名を `team_fuga`、他チームの例として `team_hoge` を使用しています。適宜読み替えてください。

---

### PR を確認

GitHub の PR ページを開くと、コンフリクトがある場合は以下のような表示が出ます：

```text
This branch has conflicts that must be resolved
```

[![Image from Gyazo](https://i.gyazo.com/83f503b73282a6651c9fcf56ad1bcad3.png)](https://gyazo.com/83f503b73282a6651c9fcf56ad1bcad3)

コンフリクトしている場合は以下のどちらかの方法でコンフリクトを解消してください。

## 方法1：GitHub Web UI でコンフリクトを解消する（推奨）

この方法は、GitHub の画面上でコンフリクトを解消できる**最も簡単な方法**です。軽微なコンフリクトであれば、この方法で十分です。

### 手順
#### 1. 「Resolve conflicts」ボタンをクリック

PR ページの下部にある **「Resolve conflicts」** ボタンをクリックします。

#### 2. Web エディタでコンフリクトを解消

GitHub の Web エディタが開き、コンフリクトが発生しているファイルが表示されます。

コンフリクト箇所は以下のような形式で表示されます：

```python
    'team_a',
<<<<<<< <あなたのブランチ名>
    'team_fuga'
=======
    'team_hoge'
>>>>>>> main
```
[![Image from Gyazo](https://i.gyazo.com/a064c9048674932c44aa01ce6ca03d62.png)](https://gyazo.com/a064c9048674932c44aa01ce6ca03d62)

**解消方法：両方の変更を残す**

ほとんどの場合、**両方のチームの変更を残す**必要があります。以下のように編集してください：

**編集前（コンフリクト状態）：**

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'team_a',
<<<<<<< team_fuga/setup (Current Change)
    'team_fuga'
=======
    'team_hoge'
>>>>>>> main (Incoming change)
]
```

**編集後（両方のチームを残す）：**

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'team_a',
    'team_fuga',
    'team_hoge'
]
```

**重要：**
- `Accept both changes`をクリックしても、手動で編集しても構いません
- 手動で編集する場合は、`<<<<<<<`、`=======`、`>>>>>>>` の行は **すべて削除** してください
- Python の文法エラーがないか確認してください（カンマ、インデントなど）
  - 特に配列や辞書を編集した場合、各要素の間にカンマが必要なことに注意してください
- 他チームの変更を削除しないように注意してください

#### 3. すべてのコンフリクトファイルを解消

通常、以下の4ファイルでコンフリクトが発生します。それぞれ同様の手順で解消してください：

##### `pbl_project/settings.py`

**INSTALLED_APPS セクション：**

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    # ... 既存アプリ ...
    'team_hoge',      # ← main にマージ済み
    'team_fuga',    # ← あなたのチーム
]
```

[![Image from Gyazo](https://i.gyazo.com/b6ed8533b6830326aae21a3717bff77e.png)](https://gyazo.com/b6ed8533b6830326aae21a3717bff77e)

**DATABASES セクション：**

```python
DATABASES = {
    'default': { ... },
    'team_a': { ... },
    'team_b': { ... },
    'team_hoge': {    # ← main にマージ済み
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'team_hoge' / 'db.sqlite3',
    },
    'team_fuga': {  # ← あなたのチーム
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'team_fuga' / 'db.sqlite3',
    },
}
```

[![Image from Gyazo](https://i.gyazo.com/519758151b10265bf1df48ff927bbb74.png)](https://gyazo.com/519758151b10265bf1df48ff927bbb74)

##### `pbl_project/urls.py`

```python
urlpatterns = [
    path('admin/', admin.site.urls),
    # ... 既存パス ...
    path('team_hoge/', include('team_hoge.urls')),      # ← main にマージ済み
    path('team_fuga/', include('team_fuga.urls')),  # ← あなたのチーム
]
```

[![Image from Gyazo](https://i.gyazo.com/6f3779364d22468c14cd39d15bedb414.png)](https://gyazo.com/6f3779364d22468c14cd39d15bedb414)

##### `pbl_project/views.py`

```python
def index(request):
    teams = [
        {"name": "Team hoge", "url": "/team_hoge/"},      # ← main にマージ済み
        {"name": "Team fuga", "url": "/team_fuga/"},  # ← あなたのチーム
    ]
    return render(request, "top.html", {"teams": teams})
```

[![Image from Gyazo](https://i.gyazo.com/7c9a753decd597032996bcf03e3d325b.png)](https://gyazo.com/7c9a753decd597032996bcf03e3d325b)

##### `routers.py`

```python
class TeamPerAppRouter:
    app_to_db = {
        'team_a': 'team_a',
        'team_b': 'team_b',
        'team_hoge': 'team_hoge',      # ← main にマージ済み
        'team_fuga': 'team_fuga',  # ← あなたのチーム
    }
```

[![Image from Gyazo](https://i.gyazo.com/d01775323aff6c6a2cae84da0cd86833.png)](https://gyazo.com/d01775323aff6c6a2cae84da0cd86833)

#### 4. 「Mark as resolved」をクリック

各ファイルの編集が終わったら、ファイルごとに **「Mark as resolved」** ボタンをクリックします。

#### 5. 「Commit merge」をクリック

すべてのファイルが解消されたら、**「Commit merge」** ボタンをクリックしてコンフリクト解消をコミットします。

コミットメッセージは自動生成されたものをそのまま使用して構いません（例：`Merge branch 'main' into team_fuga/setup`）。

#### 6. PR をマージ

コンフリクトが解消されると、PR ページに **「Merge pull request」** ボタンが表示されます。

レビュー承認後、マージを実行してください。

---

## 方法2：ローカルでコンフリクトを解消する

この方法は、**より複雑なコンフリクトや、複数ファイルの変更を詳細に確認したい場合**に適しています。

### 手順

#### 1. 最新の main ブランチを取得

まず、リモートの最新状態を取得します：

```bash
git fetch origin
```

#### 2. main ブランチの変更を自分のブランチにマージ

現在の作業ブランチ（例：`team_fuga/setup`）に、main の変更を取り込みます：

```bash
git checkout team_fuga/setup
git merge origin/main
```

コンフリクトが発生すると、以下のようなメッセージが表示されます：

```text
Auto-merging pbl_project/settings.py
CONFLICT (content): Merge conflict in pbl_project/settings.py
Auto-merging pbl_project/urls.py
CONFLICT (content): Merge conflict in pbl_project/urls.py
Auto-merging pbl_project/views.py
CONFLICT (content): Merge conflict in pbl_project/views.py
Auto-merging routers.py
CONFLICT (content): Merge conflict in routers.py
Automatic merge failed; fix conflicts and then commit the result.
```

#### 3. コンフリクトが発生したファイルを確認

コンフリクトが発生しているファイルの一覧を確認します：

```bash
git status
```

以下のような表示が出ます：

```text
Unmerged paths:
  (use "git add <file>..." to mark resolution)
        both modified:   pbl_project/settings.py
        both modified:   pbl_project/urls.py
        both modified:   pbl_project/views.py
        both modified:   routers.py
```

#### 4. エディタでコンフリクトを解消

VS Code や任意のエディタでファイルを開きます。

**VS Code の場合、コンフリクト箇所には便利なボタンが表示されます：**

- `現在の変更を取り込む`（自分の変更を採用）
- `入力側の変更を取り込む`（main の変更を採用）
- `両方の変更を取り込む`（両方を採用）← **多くの場合これを使用**
- `変更の比較`（変更を比較）

**コンフリクト箇所の例（`routers.py`）：**

```python
app_to_db = {
    'team_a': 'team_a',
    'team_b': 'team_b',
<<<<<<< HEAD
    'team_fuga': 'team_fuga',
=======
    'team_hoge': 'team_hoge',
>>>>>>> origin/main
}
```

**解消後：**

```python
app_to_db = {
    'team_a': 'team_a',
    'team_b': 'team_b',
    'team_hoge': 'team_hoge',
    'team_fuga': 'team_fuga',
}
```

**重要なポイント：**
- `Accept both changes`をクリックしても、手動で編集しても構いません
- 手動で編集する場合は、`<<<<<<<`、`=======`、`>>>>>>>` の行は **すべて削除** してください
- Python の文法エラーがないか確認してください（カンマ、インデントなど）
  - 特に配列や辞書を編集した場合、各要素の間にカンマが必要なことに注意してください
- 他チームの変更を削除しないように注意してください

#### 5. すべてのコンフリクトファイルを解消

`pbl_project/settings.py`、`pbl_project/urls.py`、`pbl_project/views.py`、`routers.py` の4ファイルすべてで、同様に両方の変更を残すように解消してください。

#### 6. 解消したファイルをステージング

コンフリクトを解消したら、ファイルをステージングエリアに追加します：

```bash
git add pbl_project/settings.py
git add pbl_project/urls.py
git add pbl_project/views.py
git add routers.py
```

または一括で追加：

```bash
git add .
```

#### 7. マージコミットを作成

コンフリクト解消のコミットを作成します：

```bash
git commit -m "Merge main into team_fuga/setup and resolve conflicts"
```

または、`git commit` だけを実行すると、自動生成されたマージコミットメッセージが表示されます（そのまま保存して OK）。

#### 8. リモートにプッシュ

解消した変更をリモートブランチにプッシュします：

```bash
git push origin team_fuga/setup
```

#### 9. PR を確認してマージ

GitHub の PR ページを確認すると、コンフリクトが解消されていることが確認できます。

レビュー承認後、**「Merge pull request」** をクリックしてマージしてください。

---

## コンフリクト解消のベストプラクティス

### ✅ DO（推奨）

- **両方の変更を残す**：他チームの変更を削除しないように注意
- **アルファベット順や追加順に整理**：可読性を高める
- **コンフリクト解消後に動作確認**：ローカルでサーバーを起動して問題がないか確認

  ```bash
  uv run python manage.py runserver
  ```

- **PR にコメントを追加**：「main の変更を取り込み、コンフリクトを解消しました」など

### ❌ DON'T（避けるべき）

- **他チームの変更を削除しない**：必ず両方の変更を残してください
- **コンフリクトマーカーを残さない**：`<<<<<<<`、`=======`、`>>>>>>>` は必ず削除
- **main に直接プッシュしない**：ブランチ保護により拒否されます
- **コンフリクト解消後のテストを怠らない**：必ず動作確認を行う

---

## トラブルシューティング

### Q1. コンフリクト解消後もエラーが出る

**原因：** Python の文法エラー（カンマ忘れ、インデント間違いなど）が残っている可能性があります。

**解決策：**

```bash
# 文法チェック
uv run python manage.py check

# サーバー起動で確認
uv run python manage.py runserver
```

エラーメッセージを確認して、該当箇所を修正してください。

### Q2. 「Resolve conflicts」ボタンが表示されない

**原因：** コンフリクトが複雑すぎて、GitHub の Web エディタでは解消できない場合があります。

**解決策：** 方法2（ローカルでの解消）を使用してください。

### Q3. `git merge` でコンフリクトが発生しなかった

**原因：** すでに最新の main を取り込んでいるか、変更が競合していない可能性があります。

**解決策：** `git status` で状態を確認し、必要に応じてそのままプッシュしてください。

## まとめ

22チームが同時にセットアップを進める場合、コンフリクトは**避けられません**が、正しく解消すれば問題ありません。

- **簡単な場合**：GitHub Web UI で解消（方法1）
- **複雑な場合**：ローカルで解消（方法2）

**重要：必ず両方のチームの変更を残してください。**

不明点があれば、チームメンバーやコーチに相談してください。
