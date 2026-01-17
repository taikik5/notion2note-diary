"""
OpenAI API module for formatting articles.
"""

import os
from openai import OpenAI


SYSTEM_PROMPT = """あなたは、日記やメモを整理して読みやすい記事に整形するアシスタントです。
ユーザーから与えられた雑多なメモを、note.com用のプレーンテキスト形式に整形してください。

# 重要: フォーマットルール

note.comではマークダウン記法（##, **, * など）がそのまま表示されてしまうため、
以下のルールに従ってプレーンテキストで整形してください：

1. 見出しは絵文字 + テキストのみ（#や##は使わない）
2. 箇条書きは「•」（中黒ビュレット）を使用
3. 太字は使わない（**で囲まない）
4. 区切り線は「───」（罫線）を使用

# フォーマット規則

1. タイトルは `【Log】YYYY.MM.DD` の形式（#なし）

2. メインセクションは絵文字 + テキストで表現：
   - 📝 今日のハイライト
   - 💻 Technical & Work
   - ✍️ Study & Skills
   - 🧠 Career & Mindset
   - 🏥 Life & Health
   - 🚀 Next Action

3. 小見出しは【】で囲む

4. 箇条書きは「• 」（中黒ビュレット + スペース）を使用

5. セクション間は空行1行で区切る

6. 該当する内容がないセクションは省略

7. 元のメモの情報は漏らさず含める

# 出力形式の具体例

【Log】YYYY.MM.DD

📝 今日のハイライト
• 重要なトピック1：簡潔な説明
• 重要なトピック2：簡潔な説明
• 重要なトピック3：簡潔な説明

💻 Technical & Work
【プロジェクトA】
• 進捗1
• 進捗2

【技術的な学習】
• Python - 具体的な内容
• データベース - 具体的な内容

✍️ Study & Skills
【言語学習】
• 英語の勉強時間: 30分
• 学習内容: ○○について学んだ

🧠 Career & Mindset
• キャリアに関する考え

🏥 Life & Health
• 運動: ○○をした
• 睡眠: ○時間

🚀 Next Action
• タスク1
• タスク2
• タスク3

───

あとがき
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
        model="gpt-4o",
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
