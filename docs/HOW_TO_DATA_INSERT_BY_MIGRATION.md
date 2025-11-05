# SQLite（例: `team_terrace`）で データの追加をmigration管理する
この手順書では、team_terraceを例にして、djangoのmigration機能を使ったシードデータを投入するための手順書を記載しています。
データの投入をmigration管理するメリットとしては、以下のものが挙げられます。
- コマンドを実行するだけで同じ初期データを確実に作成でき、手動でSQLを実行する手間・ミスがなくなる
- データの変更履歴をコード上で管理できる

---
## 0. 自分のチームのapp名を確認する

マイグレーションを作成する前に、**対象のアプリ名（app名）** を確認しておきましょう。
プロジェクトの `settings.py` を開き、`INSTALLED_APPS` のリストを探します。

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'team_terrace',  # ← これがアプリ名
    'another_app',
]
```

## 1. 空のマイグレーションファイルを作成する

```bash
uv run python manage.py makemigrations --empty team_terrace -n seed_members_sql
```
| オプション                      | 意味                           | 補足                                             |
|----------------------------|------------------------------|------------------------------------------------|
| `--empty`                  | **空のマイグレーションファイル**を作成します。    | モデル変更がない場合でも、任意の SQL や Python 処理を手書きできます。      |
| `team_terrace`             | 対象の Django アプリ名です。           | `team_terrace/migrations/` 内にファイルが生成されます。      |
| `-n seed_members_sql`      | ファイル名に追加される説明ラベルです。          | 実際のファイル名は `0002_seed_members_sql.py` のようになります。 |

## 2. マイグレーションファイルを編集する
作成された`<app名>/migrations/<生成されたファイル名>` (例：`team_terrace/migrations/0002_seed_members_sql.py`)を開いて、以下の内容を貼り付けます。

```python
from django.db import migrations

SQL_SEED = """
INSERT INTO team_terrace_member -- TODO: app名_memberに変更
(first_name, last_name)
VALUES
  ('Taro', 'Yamada'),
  ('Hanako', 'Sato');
"""

SQL_ROLLBACK = """
DELETE FROM team_terrace_member -- TODO: app名_memberに変更
WHERE (first_name='Taro' AND last_name='Yamada')
   OR (first_name='Hanako' AND last_name='Sato');
"""

class Migration(migrations.Migration):
    dependencies = [
        ('team_terrace', '0001_initial'),  # TODO: app名に変更
    ]
    operations = [
        migrations.RunSQL(
            sql=SQL_SEED,
            reverse_sql=SQL_ROLLBACK,
        ),
    ]
```

## 3. マイグレーションを実行
```bash
# TODO: team_terraceを任意のapp名に変更
uv run python manage.py migrate team_terrace --database=team_terrace
```

## 4. データを確認する
4-1 or 4-2のどちらかの方法でデータが追加されたことを確認してください
### 4-1 shell内で確認する
ターミナルで以下を実行します
```bash
# TODO: team_terraceを任意のapp名に変更
uv run python manage.py dbshell --database=team_terrace
```
シェル内で以下を実行します：
```sql
SELECT * FROM team_terrace_member; -- TODO: app名_memberに変更する
```
以下のような結果が出ればOK
| id | first_name | last_name |
| -- | ---------- | --------- |
| 1  | Taro       | Yamada    |
| 2  | Hanako     | Sato      |


### 4-2 WEBアプリ上で確認する
以下のコマンドでアプリを立ち上げます。
```shell
uv run python manage.py runserver
```
チームの該当ページに行き、以下のような画面を表示されて入ればOK
![メンバー画面の表示結果](../images/migration-result-check.png)

## 5. (任意)データを削除したい場合
```bash
# TODO: team_terraceを任意のapp名に変更
uv run python manage.py migrate team_terrace 0001 --database=team_terrace
```
