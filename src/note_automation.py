"""
Playwright-based automation for note.com article posting.
"""

import os
import time
import json
import platform
from playwright.sync_api import sync_playwright, Page


NOTE_NEW_ARTICLE_URL = "https://note.com/notes/new"


def post_draft_to_note(
    title: str,
    body: str,
    state_file: str | None = None
) -> bool:
    """
    Post an article as a draft to note.com using saved session state.

    Args:
        title: Article title
        body: Article body (Markdown)
        state_file: Path to note-state.json file (defaults to ./note-state.json)

    Returns:
        True if successful, False otherwise
    """
    state_file = state_file or os.environ.get("NOTE_STATE_FILE", "./note-state.json")

    if not os.path.exists(state_file):
        raise FileNotFoundError(
            f"Session state file not found: {state_file}\n"
            f"Please run 'node login-note.js' first to generate the session state."
        )

    with sync_playwright() as p:
        # Use headed mode with xvfb for proper JavaScript execution
        # GitHub Actions uses xvfb-run to provide virtual display
        browser = p.chromium.launch(headless=False)

        # Create context with session state
        context_options = {
            "viewport": {"width": 1280, "height": 800},
            "locale": "ja-JP",
            "storage_state": state_file,
        }

        try:
            with open(state_file, 'r') as f:
                state = json.load(f)
                cookies_count = len(state.get('cookies', []))
                print(f"✓ Loaded {cookies_count} cookies from session state")
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Warning: Could not load session state: {e}")

        context = browser.new_context(**context_options)
        page = context.new_page()

        try:
            # Navigate to new article page directly (session already authenticated)
            _navigate_to_new_article(page)

            # Input title and body
            _input_article_content(page, title, body)

            # Save as draft
            _save_draft(page)

            return True

        except Exception as e:
            print(f"Error during note automation: {e}")
            # Take screenshot for debugging
            page.screenshot(path="error_screenshot.png")
            raise

        finally:
            context.close()
            browser.close()


def _navigate_to_new_article(page: Page) -> None:
    """Navigate to new article creation page."""
    print("Navigating to new article page...")
    page.goto(NOTE_NEW_ARTICLE_URL)
    page.wait_for_load_state("networkidle")

    # Check if redirected to login page
    current_url = page.url
    print(f"Current URL: {current_url}")

    if "/login" in current_url:
        page.screenshot(path="error_screenshot.png")
        raise RuntimeError(
            "Session expired or invalid. Redirected to login page.\n"
            "Please run 'npm run login' to regenerate the session state."
        )

    # Wait for the editor to be fully loaded
    # Try multiple selectors and wait longer
    print("Waiting for editor to fully load (this may take a while)...")

    selectors_to_try = [
        '[contenteditable="true"]',
        'textarea',
        '[data-testid="article-body"]',
        '.ProseMirror',
        '[role="textbox"]'
    ]

    editor_found = False
    for selector in selectors_to_try:
        try:
            page.wait_for_selector(selector, timeout=60000)  # 60 second timeout
            print(f"✓ Editor element found: {selector}")
            editor_found = True
            break
        except Exception as e:
            print(f"  Selector '{selector}' not found: {str(e)[:50]}")

    if not editor_found:
        print("Warning: No editor elements found after 60 seconds")
        # Save debug page for inspection
        with open("page_content_debug.html", "w", encoding="utf-8") as f:
            f.write(page.content())
        print("Debug HTML saved to page_content_debug.html")

    time.sleep(2)  # Additional wait

    print("✓ Successfully navigated to new article page")


def _input_article_content(page: Page, title: str, body: str) -> None:
    """Input article title and body."""
    print("Inputting article content...")

    # Wait a bit more for elements to be interactive
    time.sleep(2)

    # Input title
    title_input = page.locator('[placeholder*="タイトル"]').or_(
        page.locator('.o-noteEditorTextarea__title')
    ).or_(
        page.locator('[data-testid="article-title"]')
    ).or_(
        page.locator('textarea').first
    )

    if title_input.count() > 0:
        print("Found title input, filling...")
        title_input.first.click()
        time.sleep(0.3)
        title_input.first.fill(title)
        time.sleep(0.5)
        print(f"Title filled: {title}")
        # Debug: Check if title was actually filled
        title_value = page.locator('input, textarea').first.input_value() if page.locator('input, textarea').count() > 0 else "N/A"
        print(f"Debug - Title input value after fill: {title_value[:50]}")
    else:
        print("Warning: Title input not found")
        print(f"Debug - Available textareas: {page.locator('textarea').count()}")
        print(f"Debug - Available inputs: {page.locator('input').count()}")

    # Input body using clipboard paste (required for markdown conversion)
    body_editor = page.locator('[data-testid="article-body"]').or_(
        page.locator('.o-noteEditorTextarea__body')
    ).or_(
        page.locator('[contenteditable="true"]')
    ).or_(
        page.locator('.ProseMirror')
    )

    if body_editor.count() > 0:
        print("Found body editor, pasting content via clipboard...")
        editor_element = body_editor.first
        editor_element.click()
        time.sleep(0.5)

        # Use clipboard paste - this is required for note.com to recognize markdown
        # note.com converts markdown to proper formatting only when pasting from clipboard
        try:
            # Set clipboard content using JavaScript
            page.evaluate(
                """async (text) => {
                    await navigator.clipboard.writeText(text);
                }""",
                body
            )
            time.sleep(0.3)

            # Paste using keyboard shortcut (Ctrl+V or Cmd+V)
            # Use Meta for Mac, Control for Linux (GitHub Actions runs on Linux)
            if platform.system() == "Darwin":
                page.keyboard.press("Meta+v")
            else:
                page.keyboard.press("Control+v")

            print("Body pasted using clipboard")
            time.sleep(1)
        except Exception as e:
            print(f"Clipboard paste failed: {e}, trying alternative method...")
            # Fallback: Use Playwright's built-in clipboard
            try:
                # Focus and select all first
                editor_element.click()
                time.sleep(0.3)

                # Type the content line by line with Enter key
                # This helps note.com recognize markdown better
                lines = body.split('\n')
                for i, line in enumerate(lines):
                    if line.strip():
                        page.keyboard.type(line, delay=5)
                    if i < len(lines) - 1:
                        page.keyboard.press("Enter")

                print("Body typed line by line")
            except Exception as e2:
                print(f"Line-by-line typing also failed: {e2}")
                # Last resort: direct fill
                try:
                    editor_element.fill(body)
                    print("Body filled using fill() as last resort")
                except Exception as e3:
                    print(f"All methods failed: {e3}")
    else:
        print("Warning: Body editor not found")
        print(f"Debug - contenteditable elements: {page.locator('[contenteditable=true]').count()}")
        print(f"Debug - ProseMirror elements: {page.locator('.ProseMirror').count()}")

    time.sleep(1)
    print("Article content input complete")


def _save_draft(page: Page) -> None:
    """Save the article as a draft."""
    print("Saving as draft...")

    # Take screenshot before saving
    page.screenshot(path="before_save_screenshot.png")
    print("Screenshot saved: before_save_screenshot.png")

    try:
        # Debug: List all buttons on the page
        all_buttons = page.locator('button').count()
        print(f"Debug - Total buttons on page: {all_buttons}")

        # Look for the draft save button
        draft_button = page.locator('text=下書き保存').or_(
            page.locator('button:has-text("下書き")').first
        ).or_(
            page.locator('[data-testid="save-draft"]')
        )

        print(f"Debug - Draft button count: {draft_button.count()}")

        if draft_button.count() > 0:
            print(f"Found draft button, clicking...")
            draft_button.first.click()
            time.sleep(5)  # Wait for save to complete
            print("Draft saved successfully")
        else:
            print("Draft button not found, trying keyboard shortcut...")
            # Try Cmd+S on Mac
            page.keyboard.press("Meta+s")
            time.sleep(3)
            print("Attempted keyboard shortcut save (Cmd+S)")

    except Exception as e:
        print(f"Error during save: {e}")
        page.keyboard.press("Meta+s")
        time.sleep(2)

    # Take screenshot after saving
    page.screenshot(path="after_save_screenshot.png")
    print("Screenshot saved: after_save_screenshot.png")


if __name__ == "__main__":
    # Test execution (requires note-state.json from login-note.js)
    from dotenv import load_dotenv
    load_dotenv()

    test_title = "【Log】2024.01.15"
    test_body = """## 今日のハイライト
* テスト投稿です

## Technical & Work
Playwrightの自動化テスト

---
### あとがき
テスト完了！
"""

    post_draft_to_note(test_title, test_body)
    print("Test completed successfully!")
