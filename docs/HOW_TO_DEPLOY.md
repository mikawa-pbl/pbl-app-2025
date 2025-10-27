# デプロイ手順書（本番環境）

このドキュメントでは、大学で提供されているVM（Ubuntu）にDjangoアプリケーションを本番環境へデプロイする手順を説明します。

## 前提条件

- アプリケーションのソースコードはすでにVMにクローン済み
- 初期段階のアプリケーションが実行されている状態（mainブランチ）
- サーバーへのアクセス情報（IPアドレス、ユーザー名、パスワード）は[Google Classroomのスプレッドシート](https://classroom.google.com/c/ODA1ODY3MTM5MjUz/m/ODIwMDc1ODQ2ODA0/details)を参照してください

## デプロイ手順

### 1. ネットワーク接続

学内Wi-FiまたはVPNに接続してください。

### 2. SSHでサーバーへアクセス

以下のアプリケーションを使用してSSH接続を行います。

- **Windows**: PowerShellまたはコマンドプロンプト（Windows 10/11に標準搭載）
- **Mac**: ターミナル（標準搭載）
- **Linux**: ターミナル（標準搭載）

ターミナルまたはコマンドプロンプトを開き、以下のコマンドを実行してください。

```bash
ssh <ユーザー名>@<IPアドレス>
```

パスワードの入力を求められるので、[Google Classroomのスプレッドシート](https://classroom.google.com/c/ODA1ODY3MTM5MjUz/m/ODIwMDc1ODQ2ODA0/details)に記載されているパスワードを入力してください。

**注意**: パスワードを入力しても画面には何も表示されませんが、入力は受け付けられています。入力後、Enterキーを押してください。

### 3. GitHubから最新のmainブランチを取得

```bash
cd ~/pbl-app-2025
git checkout main
git pull origin main
```

### 4. 依存ライブラリの同期（ライブラリを追加した場合）

ライブラリを追加した場合は、以下のコマンドを実行して依存関係を同期してください。

```bash
uv sync
```

### 5. データベースマイグレーションの実行（必要な場合）

モデル（models.py）に変更を加えた場合など、データベースの構造に変更がある場合は、以下のコマンドを実行してください。

```bash
uv run python manage.py migrate --database=チーム名 (例：--database=team_terrace)
```

### 6. データ投入（必要な場合）

データの投入が必要な場合は、dbshellに入ってデータを投入してください。

```bash
uv run python manage.py dbshell --database=チーム名 (例：--database=team_terrace)
```
dbshell内でSQLコマンドを実行してデータを投入します。
```sql
# これは例です。実際のデータ投入内容に応じて変更してください。
INSERT INTO team_terrace_member (first_name, last_name) VALUES ('太郎', '山田');
INSERT INTO team_terrace_member (first_name, last_name) VALUES ('花子', '佐藤');
SELECT * FROM team_terrace_member;
```

### 7. アプリケーションの再起動

コードの変更を反映させるため、アプリケーションを再起動します。

#### アプリケーションの停止

```bash
sudo start-stop-daemon --stop --pidfile /run/django-dev.pid --retry=TERM/5/KILL/2
```

#### アプリケーションの起動

```bash
sudo bash -lc 'U=$(logname); start-stop-daemon --start --quiet --background --make-pidfile --pidfile /run/django-dev.pid --chdir /home/$U/pbl-app-2025 --exec /home/$U/pbl-app-2025/.venv/bin/python -- manage.py runserver 0.0.0.0:80 --noreload'
```

### 8. ブラウザからアクセスして確認

ブラウザでアプリケーションにアクセスし、更新が反映されているか確認してください。

アクセスURL: `http://<IPアドレス>`
