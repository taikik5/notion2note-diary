"""
OpenAI API module for formatting articles.
"""

import os
from openai import OpenAI


SYSTEM_PROMPT = """あなたは、日記やメモを整理して読みやすい記事に整形するアシスタントです。
ユーザーから与えられた雑多なメモを、note.com用のマークダウン形式に整形してください。

# 重要: note.comのマークダウン対応ルール

note.comは以下のマークダウン記法のみ対応しています：
- 大見出し: `## ` （シャープ2つ + 半角スペース）
- 小見出し: `### ` （シャープ3つ + 半角スペース）
- 箇条書き: `- ` （ハイフン + 半角スペース）
- 太字: `**テキスト**`

【絶対に守ること】
1. `##` や `###` の後には必ず半角スペースを1つ入れる
2. `#`（h1）は使わない（note.comでは対応外）
3. `####` 以上は使わない（note.comでは対応外）
4. 箇条書きは `- ` を使う（`*` や `•` ではなく）

# フォーマット規則

1. タイトルは `【Log】YYYY.MM.DD` の形式（見出し記号なし）

2. メインセクションは `## ` + 絵文字 + テキスト：
   - `## 📝 今日のハイライト`
   - `## 💻 Technical & Work`
   - `## ✍️ Study & Skills`
   - `## 🧠 Career & Mindset`
   - `## 🏥 Life & Health`
   - `## 🚀 Next Action`

3. 小見出しは `### ` を使用

4. 箇条書きは `- ` を使用

5. 重要なキーワードは `**太字**` で強調

6. セクション間は空行1行で区切る

7. 該当する内容がないセクションは省略

8. 元のメモの情報は漏らさず含める

# 出力形式の具体例

【Log】YYYY.MM.DD

## 📝 今日のハイライト

- **重要なトピック1** - 簡潔な説明
- **重要なトピック2** - 簡潔な説明
- **重要なトピック3** - 簡潔な説明

## 💻 Technical & Work

### プロジェクトA

- 進捗1
- 進捗2

### 技術的な学習

- **Python** - 具体的な内容
- **データベース** - 具体的な内容

## ✍️ Study & Skills

### 言語学習

- 英語の勉強時間: 30分
- 学習内容: ○○について学んだ

## 🧠 Career & Mindset

- キャリアに関する考え

## 🏥 Life & Health

- 運動: ○○をした
- 睡眠: ○時間

## 🚀 Next Action

- タスク1
- タスク2
- タスク3

---

### あとがき

本日の一言や感情を記載します。
"""


def format_article(memo_content: str, date: str) -> tuple[str, str]:
    """
    Format memo content into a structured article using OpenAI API.

    Args:
        memo_content: Raw memo content from Notion
        date: Date string in YYYY.MM.DD format

    Returns:
        Tuple of (title, formatted_body)
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")

    # Get model from environment variable, default to gpt-4o-mini
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

    client = OpenAI(api_key=api_key)

    user_message = f"""以下のメモを整形してください。

日付: {date}

---
メモ内容:
{memo_content}
---

上記のメモを、指定されたフォーマットに従って整形してください。
マークダウン形式で出力してください（```markdown などのコードブロックで囲まないでください）。
"""

    message = client.chat.completions.create(
        model=model,
        max_tokens=4096,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user_message
            }
        ]
    )

    formatted_content = message.choices[0].message.content

    # Extract title and body
    lines = formatted_content.strip().split("\n")
    title = ""
    body_lines = []

    for i, line in enumerate(lines):
        # Match both "# 【Log】" (old format) and "【Log】" (new format)
        if line.strip().startswith("【Log】"):
            title = line.lstrip("# ").strip()
            body_lines = lines[i + 1:]
            break

    body = "\n".join(body_lines).strip()

    # If title extraction failed, use default
    if not title:
        title = f"【Log】{date}"
        body = formatted_content

    return title, body


if __name__ == "__main__":
    # Test execution
    from dotenv import load_dotenv
    load_dotenv()

    test_memo = """
    今日はPythonでスクレイピングのコードを書いた。
    BeautifulSoupよりPlaywrightの方が使いやすい気がする。
    英語の勉強も30分くらいやった。
    夜は早く寝たい。
    明日は会議がある。
    """

    title, body = format_article(test_memo, "2024.01.15")
    print(f"Title: {title}")
    print(f"\nBody:\n{body}")
