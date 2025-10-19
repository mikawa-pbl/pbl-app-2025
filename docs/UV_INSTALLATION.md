# uv インストールガイド

このドキュメントでは、Python パッケージマネージャー `uv` のインストール方法を OS 別に説明します。

---

## Windows（PowerShell）

### 1. uv をインストール

PowerShell を開き、以下のコマンドを実行します：

```PowerShell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. パスを通す

上記のインストールコマンドを実行すると、以下のようなメッセージが表示されます：

```txt
To add C:\Users\<ユーザー名>\.local\bin to your PATH, either restart your shell or run:

    $env:Path = "C:\Users\<ユーザー名>\.local\bin;$env:Path"   (powershell)
```

メッセージに従い、**PowerShell を一旦閉じて開き直し**てパスを通します。

### 3. インストール確認（Windows）

以下のコマンドで `uv` が正しくインストールされているか確認します：

```PowerShell
uv --version
```

### 4. （エラーが出た場合のみ）実行ポリシーの変更

上記のコマンドでエラーが出る場合は、PowerShell を**管理者として実行**し、以下のコマンドを実行します：

```PowerShell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
```

実行後、PowerShell を開き直してから、再度 `uv --version` で確認してください。

---

## macOS

### 1. Homebrew で uv をインストール

ターミナルを開き、以下のコマンドを実行します：

```bash
brew install uv
```

### 2. インストール確認（macOS）

以下のコマンドで `uv` が正しくインストールされているか確認します：

```bash
uv --version
```

---

## Linux

### 1. インストールスクリプトを実行

ターミナルを開き、以下のコマンドを実行します：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. シェルを再起動

パスを通すために、**ターミナルを一旦閉じて開き直し**ます。

### 3. インストール確認（Linux）

以下のコマンドで `uv` が正しくインストールされているか確認します：

```bash
uv --version
```

---

## VS Code の設定（全 OS 共通）

### 1. Python 拡張機能をインストール

VS Code の拡張機能から「Python」をインストールします。
[![Image from Gyazo](https://i.gyazo.com/be99bbfeec3e1c0bda697dbea07c9935.png)](https://gyazo.com/be99bbfeec3e1c0bda697dbea07c9935)

### 2. Python 環境の自動有効化設定

VS Code の設定で以下をオンにします：

```txt
Python › Terminal: Activate Env In Current Terminal
```

**設定方法:**

- VS Code 左下の歯車マーク ＞ 設定 をクリック
- 検索バーに「Python Terminal Activate」と入力
- 「Python › Terminal: Activate Env In Current Terminal」にチェックを入れる

### 3. VS Code でターミナルを開き直す

設定を反映させるため、VS Code のターミナルを閉じて開き直します。

---

## 次のステップ

`uv` のインストールと VS Code の設定が完了したら、[NEW_TEAM_SETUP.md](NEW_TEAM_SETUP.md) に従ってプロジェクトのセットアップを進めてください。
