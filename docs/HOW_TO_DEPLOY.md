# デプロイ手順書（開発環境）

このドキュメントでは、大学で提供されているVM（Ubuntu）にDjangoアプリケーションを開発環境へデプロイする手順を説明します。

## 前提条件

- 各チームの作業用ブランチが作成済み
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

### 3. 初回セットアップ（最初の1回・1人のみ実行）

**注意**: この手順は、VMに初めてアプリケーションをセットアップする際に、チーム内の1人だけが1回実行してください。2回目以降のデプロイでは、この手順はスキップして手順4に進んでください。

#### 3-1. GitHubからソースコードをクローン

```bash
cd ~
git clone https://github.com/mikawa-pbl/pbl-app-2025.git
cd pbl-app-2025
```

#### 3-2. 各チームの作業用ブランチに切り替え

```bash
git checkout <チームのブランチ名>
```

例: `git checkout team_terrace`

#### 3-3. 依存ライブラリのインストール

```bash
uv sync
```

#### 3-4. データベースマイグレーションの実行

```bash
uv run python manage.py migrate --database=<チーム名>
```

例: `uv run python manage.py migrate --database=team_terrace`

**注意**: マイグレーションを実行することで、データベースのテーブル作成と初期データの投入が自動的に行われます。詳細は[データの追加をmigration管理する手順書](HOW_TO_DATA_INSERT_BY_MIGRATION.md)を参照してください。

初回セットアップが完了したら、手順7のアプリケーション起動に進んでください（初回は停止不要）。

---

### 4. GitHubから最新のブランチを取得（2回目以降）

```bash
cd ~/pbl-app-2025
git checkout <チームのブランチ名>
git pull origin <チームのブランチ名>
```

例: `git checkout team_terrace` → `git pull origin team_terrace`

### 5. 依存ライブラリの同期（ライブラリを追加した場合）

ライブラリを追加した場合は、以下のコマンドを実行して依存関係を同期してください。

```bash
uv sync
```

### 6. データベースマイグレーションの実行（必要な場合）

モデル（models.py）に変更を加えた場合など、データベースの構造に変更がある場合は、以下のコマンドを実行してください。

```bash
uv run python manage.py migrate --database=<チーム名>
```

例: `uv run python manage.py migrate --database=team_terrace`

**注意**: マイグレーションを実行することで、データベースの構造変更と初期データの投入が自動的に行われます。データの追加方法については[データの追加をmigration管理する手順書](HOW_TO_DATA_INSERT_BY_MIGRATION.md)を参照してください。

### 7. アプリケーションの再起動

コードの変更を反映させるため、アプリケーションを再起動します。

**注意**: 初回セットアップ時は、アプリケーションがまだ起動していないため、停止コマンドは不要です。起動コマンドのみを実行してください。

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
