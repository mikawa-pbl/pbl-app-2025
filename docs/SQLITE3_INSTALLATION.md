# SQLite3 インストールガイド

このドキュメントは、Django の `dbshell` コマンドや SQLite データベースを直接操作するために必要な **SQLite3 コマンドラインツール**のインストール方法をまとめたものです。

---

## 目次

1. [OS別の必要性](#os別の必要性)
2. [オプション1: パッケージマネージャーでインストール（推奨）](#オプション1-パッケージマネージャーでインストール推奨)
3. [オプション2: ZIP ファイルからインストール（Windows のみ）](#オプション2-zip-ファイルからインストールwindows-のみ)
4. [オプション3: VS Code 拡張機能を使用（代替手段）](#オプション3-vs-code-拡張機能を使用代替手段)
5. [インストール確認](#インストール確認)

---

## OS別の必要性

### macOS / Linux

**SQLite3 はシステムに標準搭載されています。** インストール作業は不要です。

ターミナルで以下のコマンドを実行して、バージョンが表示されることを確認してください：

```bash
sqlite3 --version
```

### Windows

**Windows には SQLite3 が標準搭載されていません。** Django の `dbshell` コマンドを使用するには、以下のいずれかの方法でインストールする必要があります。

---

## オプション1: パッケージマネージャーでインストール（推奨）

パッケージマネージャーを使用する方法は、最も簡単で確実なインストール方法です。

### Windows の場合

**winget を使用**（Windows 10/11 標準搭載）

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

### macOS の場合

**標準搭載されているため、インストール不要です。**

念のため確認する場合：

```bash
sqlite3 --version
```

もし何らかの理由で再インストールが必要な場合は、Homebrew を使用できます：

```bash
brew install sqlite3
```

### Linux の場合

**標準搭載されているため、通常はインストール不要です。**

念のため確認する場合：

```bash
sqlite3 --version
```

もしインストールが必要な場合は、ディストリビューションのパッケージマネージャーを使用します：

**Ubuntu / Debian の場合：**

```bash
sudo apt update
sudo apt install sqlite3
```

**Fedora / RHEL / CentOS の場合：**

```bash
sudo dnf install sqlite
```

**Arch Linux の場合：**

```bash
sudo pacman -S sqlite
```

---

## オプション2: ZIP ファイルからインストール（Windows のみ）

winget が使用できない、または手動でインストールしたい場合は、この方法を使用できます。

### ステップ 1: ZIP ファイルをダウンロード

1. [SQLite 公式ダウンロードページ](https://www.sqlite.org/download.html) にアクセス

2. **"Precompiled Binaries for Windows"** セクションから以下のファイルをダウンロード：
   - `sqlite-tools-win-x64-XXXXXXX.zip`（数字部分はバージョンによって異なります）
   - 64ビット版Windowsをお使いの場合はこちらを選択してください（ほとんどの現代的なPCは64ビット版です）

### ステップ 2: ファイルを解凍して配置

1. ダウンロードした ZIP ファイルを右クリックして「すべて展開」を選択

2. 任意の場所（デフォルトのダウンロードフォルダでOK）に解凍します
   - 解凍すると `sqlite-tools-win-x64-XXXXXXX` のようなフォルダができます

3. 解凍されたフォルダ全体を `C:\` 直下に移動します
   - エクスプローラーでフォルダをドラッグ＆ドロップするか、切り取り＆貼り付けで移動

4. `C:\` に移動したフォルダの名前を `sqlite` に変更します
   - `C:\sqlite-tools-win-x64-XXXXXXX` → `C:\sqlite`

5. `C:\sqlite` フォルダの中に以下のファイルがあることを確認：
   - `sqlite3.exe`
   - `sqldiff.exe`
   - `sqlite3_analyzer.exe`
   - `sqlite3_rsync.exe`

### ステップ 3: 環境変数 PATH にフォルダを追加

**方法A: PowerShell コマンドで設定（推奨）**

PowerShell を開いて、以下のコマンドを実行します（**管理者権限は不要**です）：

```powershell
setx PATH "$env:PATH;C:\sqlite"
```

実行すると「成功: 指定した値は保存されました。」と表示されます。

**PowerShell や VS Code を再起動**して変更を反映してください。

**注意:** このコマンドは**ユーザー環境変数**に設定します。研究室の共有PCなど、管理者権限がない環境でも安全に使用できます。

**方法B: GUI で設定**

コマンドでの設定が難しい場合は、以下の手順で GUI から設定できます：

1. **Windows キー**を押して「環境変数」と入力し、「環境変数を編集」を選択

2. 「ユーザー環境変数」の中から **Path** を選択して「編集」をクリック

3. 「新規」ボタンをクリックして、以下のパスを追加：
   ```
   C:\sqlite
   ```

4. 「OK」をクリックしてすべてのダイアログを閉じる

5. **PowerShell や VS Code を再起動**して変更を反映

### ステップ 4: インストール確認

```powershell
sqlite3 --version
```

---

## オプション3: VS Code 拡張機能を使用（代替手段）

SQLite3 のコマンドラインツールのインストールが難しい場合、または `dbshell` コマンドを使用しない場合は、VS Code の拡張機能を使用することで GUI から SQLite データベースを操作できます。

### インストール手順

1. VS Code を開く
2. 拡張機能パネルを開く（`Ctrl+Shift+X` または `Cmd+Shift+X`）
3. 検索ボックスに **`SQLite3 Editor`** と入力
   [![Image from Gyazo](https://i.gyazo.com/8c3caeaacf1492b8d9281cdeb3ae997b.png)](https://gyazo.com/8c3caeaacf1492b8d9281cdeb3ae997b)
4. 「SQLite3 Editor」拡張機能をインストール

### 使用方法

1. VS Code のエクスプローラーで `.sqlite3` ファイルをダブルクリック
  [![Image from Gyazo](https://i.gyazo.com/5926ce63dd1d1fe1550c4d69a88cc93e.png)](https://gyazo.com/5926ce63dd1d1fe1550c4d69a88cc93e)
2. GUI でテーブルの閲覧、データの編集、SQL クエリの実行が可能です

### 注意事項

- この方法では Django の `dbshell` コマンドは使用できません
- データベースの操作は VS Code の GUI 経由で行います

---

## インストール確認
いずれの方法でインストールした場合も、以下のコマンドでバージョンが表示されることを確認してください：

### Windows (PowerShell):
```powershell
sqlite3 --version
```

### macOS / Linux:
```bash
sqlite3 --version
```

バージョンが表示されれば（例: `3.42.0`）、インストール成功です。

---

## Django の dbshell コマンドの使用例
インストール後、以下のコマンドで SQLite データベースに接続できます：

```bash
# デフォルトデータベースに接続
uv run python manage.py dbshell

# 特定のデータベースに接続（マルチDB環境の場合）
uv run python manage.py dbshell --database=team_terrace
```

接続後、SQL コマンドを直接実行できます：

```sql
-- テーブル一覧を表示
.tables

-- データを挿入
INSERT INTO team_terrace_member (first_name, last_name) VALUES ('太郎', '山田');

-- データを確認
SELECT * FROM team_terrace_member;

-- 終了
.exit
```

## まとめ

- **macOS / Linux:** 標準搭載、インストール不要
- **Windows（推奨）:** オプション1のwingetを使用
- **Windows（手動）:** オプション2のZIPファイルから手動インストール
- **代替手段:** オプション3のVS Code拡張機能を使用

それでも問題が解決しない場合は、チームメンバーや講師に相談してください。
