# Notion2Note Diary AutoDrafter

Notionに書き溜めた雑多なメモを、OpenAI APIで整形し、note.comへ下書き保存する自動化システム。

## セットアップ

### 1. Notion データベース準備

以下のプロパティを持つデータベースを作成してください：

| プロパティ名 | 型 | 説明 |
|-------------|------|------|
| ID | タイトル | 記事の識別用 |
| Date | 日付 | 記事の対象日（例: 2025年1月17日） |
| Diary | テキスト | 日中のメモ・日記を書き込む |
| Status | ステータス | `Ready`, `Done` |

### 2. Notion インテグレーション作成

1. [Notion Developers](https://developers.notion.com/) でインテグレーションを作成
2. データベースにインテグレーションを接続
3. トークンを取得

### 3. note.com セッション状態の準備（初回のみ）

1. Node.js がインストールされていることを確認
2. 以下を実行して note.com にログイン：
```bash
node login-note.js
```
3. ブラウザが起動し、手動でログインしてください
4. ログイン完了後、`note-state.json` が生成されます

### 4. GitHub Secrets 設定

リポジトリの Settings > Secrets and variables > Actions で以下を設定：

**必須：**
- `OPENAI_API_KEY`: OpenAI APIキー
- `NOTION_TOKEN`: Notionインテグレーショントークン
- `NOTION_DATABASE_ID`: NotionデータベースID
- `NOTE_STATE_FILE`: `note-state.json` ファイルの内容（Base64エンコード）

**オプション：**
- `OPENAI_MODEL`: 使用するOpenAIモデル（デフォルト: `gpt-4o-mini`）
  - `gpt-4o-mini`: コスパ最強、日記整形には十分（推奨）
  - `gpt-4o`: より高品質だが高コスト
  - `gpt-3.5-turbo`: 最安だが品質は劣る

#### NOTE_STATE_FILE の設定方法

```bash
# note-state.json をBase64エンコード
cat note-state.json | base64 -w 0 | pbcopy
# または Linux の場合
cat note-state.json | base64 -w 0

# GitHub Secrets にコピーペースト
```

## 実行方法

### 自動実行
- 毎日23:00 JST (14:00 UTC) に自動実行されます

### 手動実行
1. GitHub Actions タブを開く
2. "Note Auto-Drafter" ワークフローを選択
3. "Run workflow" をクリック

## ローカル開発

### セットアップ手順

#### 1. リポジトリをクローン
```bash
git clone <repository-url>
cd notion2note_diary
```

#### 2. Python 仮想環境を作成・有効化
```bash
# 仮想環境の作成
python3 -m venv venv

# 仮想環境の有効化（macOS/Linux）
source venv/bin/activate

# 仮想環境の有効化（Windows）
# venv\Scripts\activate
```

#### 3. Node.js 依存関係をインストール
```bash
npm install  # または yarn install
```

#### 4. Python 依存関係をインストール
```bash
pip install -r requirements.txt
playwright install chromium
playwright install-deps chromium
```

#### 5. 見出し画像とフォントを配置

**見出し画像（header_background.png）：**

アイキャッチ画像として使用される背景画像を準備してください：

```bash
# 推奨サイズ: 1280 x 670 px
# 対応形式: PNG, JPG, JPEG

# assets/ フォルダに配置
cp /path/to/your/header_background.png assets/header_background.png
```

- ファイル名は `header_background.png` (`.jpg`, `.jpeg` も可)
- サイズ: **1280 x 670 px** （note.com推奨）
- note.comへ投稿時、この背景画像に日付テキストを重ねたものが見出し画像として設定されます
- **.gitignoreで除外** されるため、各環境で独立して管理されます

**フォント（Pacifico-Regular.ttf）：**

見出し画像の日付テキスト用フォントです。初回セットアップで自動配置されます：

```bash
# すでに assets/Pacifico-Regular.ttf が配置されているか確認
ls assets/Pacifico-Regular.ttf
```

フォントが見つからない場合、以下で手動ダウンロード：

```bash
cd assets
curl -L https://fonts.gstatic.com/s/pacifico/v24/FwZY7-Qmy14u1-wWIQkA0jVVEsA.ttf -o Pacifico-Regular.ttf
```

**GitHub Actions での動作：**
- `header_background.png` と `Pacifico-Regular.ttf` は `.gitignore` で除外
- ローカル開発では必須（上記の配置が必要）
- GitHub Actions では環境変数/Secretsで自動供給される予定
- リポジトリには **保存されず**、各環境のみで利用

#### 6. 環境変数を設定
```bash
# .env.example をコピー
cp .env.example .env

# .env を編集してAPIキーを設定
# 必須項目：
# - OPENAI_API_KEY
# - NOTION_TOKEN
# - NOTION_DATABASE_ID
```

#### 7. note.com セッション状態を生成（初回のみ）
```bash
# ログインスクリプトを実行
node login-note.js

# ブラウザが起動したら手動でログイン
# ログイン完了後、note-state.json が自動生成されます
```

### ローカル実行

#### 方法1: run.sh を使用（推奨）
```bash
./run.sh
```

#### 方法2: venv/bin/python を直接指定
```bash
./venv/bin/python src/main.py
```

#### 方法3: 仮想環境をアクティベート
```bash
# zsh で仮想環境をアクティベート
. venv/bin/activate

# 確認（venv内のpythonが使われているか）
which python3
# 出力が ./venv/bin/python3 ならOK

# 実行
python3 src/main.py
```

### 見出し画像について

毎回の投稿時に自動的にアイキャッチ画像が生成され、note.comへアップロードされます：

- **背景**: `assets/header_background.png` で指定した画像
- **テキスト**: 記事の日付（YYYY.MM.DD形式）
- **フォント**: Pacifico（カジュアルで読みやすいスタイル）
- **テキスト配置**: 中央、白色、影なし

生成された画像は一時ディレクトリに保存され、note.comへアップロード後は自動削除されます

### トラブルシューティング

**`python: command not found` または `ModuleNotFoundError` の場合：**
```bash
# venv/bin/python を直接使用
./venv/bin/python src/main.py

# または run.sh を使用
./run.sh
```

**Playwright がインストールされていない場合：**
```bash
./venv/bin/python -m playwright install chromium
./venv/bin/python -m playwright install-deps chromium
```

**note.com のセッションが切れた場合：**

GitHub Actions で以下のエラーが出た場合、セッションの再生成が必要です：
- `Session expired or invalid. Redirected to login page.`
- `RuntimeError: Session expired`

**対処方法：**

1. ローカルでログインスクリプトを再実行：
```bash
node login-note.js
```

2. ブラウザで note.com にログイン

3. `note-state.json` が再生成される

4. GitHub Secrets の `NOTE_STATE_FILE` を更新：
```bash
# macOS
cat note-state.json | base64 | pbcopy

# Linux
cat note-state.json | base64 -w 0

# 出力をコピーして GitHub Secrets に貼り付け
```

5. GitHub リポジトリの Settings > Secrets and variables > Actions で `NOTE_STATE_FILE` を更新

**セッションの有効期限について：**
- note.com のセッションは一定期間で期限切れになります
- 定期的（1〜2週間に1回程度）にセッションを再生成することを推奨します
- GitHub Actions が失敗した場合は、まずセッション切れを疑ってください

## 記事フォーマット

生成される記事は以下の形式になります（note.com対応マークダウン形式）：

```markdown
【Log】YYYY.MM.DD

## 📝 今日のハイライト

- **重要なポイント1** - 説明
- **重要なポイント2** - 説明

## 💻 Technical & Work

### プロジェクト名

- 進捗内容

## ✍️ Study & Skills

- 学習内容

## 🧠 Career & Mindset

- キャリアに関する考え

## 🏥 Life & Health

- 健康・生活に関する内容

## 🚀 Next Action

- タスク1
- タスク2

---

### あとがき

本日の感想や一言
```

**note.comのマークダウン対応について：**
- `## ` （大見出し）と `### ` （小見出し）のみ対応
- `##` の後に半角スペースが必須
- `#`（h1）や `####`（h4以上）は非対応
