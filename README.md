# Notion2Note Diary AutoDrafter

Notionに書き溜めた雑多なメモを、OpenAI APIで整形し、note.comへ下書き保存する自動化システム。

## セットアップ

### 1. Notion データベース準備

以下のプロパティを持つデータベースを作成してください：

| プロパティ名 | 型 | 説明 |
|-------------|------|------|
| タイトル | タイトル | 記事の識別用 |
| メモ内容 | テキスト | 日中のメモを書き込む |
| Status | セレクト | `Ready`, `Done` |
| 日付 | 日付 | 記事の対象日（空なら実行日） |

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

- `OPENAI_API_KEY`: OpenAI APIキー
- `NOTION_TOKEN`: Notionインテグレーショントークン
- `NOTION_DATABASE_ID`: NotionデータベースID
- `NOTE_STATE_FILE`: `note-state.json` ファイルの内容（Base64エンコード）

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

#### 5. 環境変数を設定
```bash
# .env.example をコピー
cp .env.example .env

# .env を編集してAPIキーを設定
# 必須項目：
# - OPENAI_API_KEY
# - NOTION_TOKEN
# - NOTION_DATABASE_ID
```

#### 6. note.com セッション状態を生成（初回のみ）
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

生成される記事は以下の形式になります（note.com用のプレーンテキスト形式）：

```
【Log】YYYY.MM.DD

📝 今日のハイライト
• 重要なポイント1
• 重要なポイント2

💻 Technical & Work
【プロジェクト名】
• 進捗内容

✍️ Study & Skills
• 学習内容

🧠 Career & Mindset
• キャリアに関する考え

🏥 Life & Health
• 健康・生活に関する内容

🚀 Next Action
• タスク1
• タスク2

───

あとがき
本日の感想や一言
```
