"""E2E test for PPT RAG system via Chainlit UI."""
import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

SCREENSHOT_DIR = "C:/Users/wangl/Hacker/ppt-rag/screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

QUESTIONS = [
    ("FusionDirector的故障诊断准确率是多少？", "q1_fusiondirector"),
    ("FusionXpark GB10支持Wi-Fi 6E无线网络连接", "q2_wifi"),
    (
        "FusionXpark GB10支持哪些存储容量？\nA.512GB\nB.1TB\nC.2TB\nD.4TB\nE.8TB",
        "q3_storage"
    ),
]


async def get_message_count(page):
    """Count all message containers in the chat."""
    return await page.evaluate("""() => {
        // Chainlit wraps messages in containers with 'msg-' or specific structure
        // Try multiple selectors
        const containers = document.querySelectorAll(
            '[class*="message"], [id*="message"], [data-testid*="message"]'
        );
        return containers.length;
    }""")


async def get_all_chat_text(page):
    """Get all visible chat text."""
    return await page.evaluate("""() => {
        const container = document.querySelector(
            '[class*="messages-container"], [class*="chat"], main, #root'
        );
        return container ? container.textContent.slice(0, 3000) : '';
    }""")


async def wait_for_assistant_response(page, prev_msg_count, timeout=90):
    """Wait until a new assistant message appears and loading finishes."""
    start = asyncio.get_event_loop().time()
    stable_count = 0

    while (asyncio.get_event_loop().time() - start) < timeout:
        current_count = await get_message_count(page)

        # Check for active generation indicators
        has_running = await page.evaluate("""() => {
            // Chainlit stores running state on the message container
            const running = document.querySelector('[data-running="true"]');
            const stopped = document.querySelector('[data-status="done"]');
            // Also check for the stop button which appears during generation
            const stopBtn = document.querySelector('button[aria-label="Stop"], button[title="Stop"]');
            // Check for any spinner/loading inside recent messages
            const spinners = document.querySelectorAll('[class*="spin"], [role="progressbar"]');
            return running !== null || (stopBtn !== null && !stopped) || spinners.length > 0;
        }""")

        elapsed = int(asyncio.get_event_loop().time() - start)

        # Messages should have increased by at least 2 (user msg + loading, then assistant)
        if current_count >= prev_msg_count + 1:
            # If no running indicator for 3 consecutive checks, we're done
            if not has_running:
                stable_count += 1
                if stable_count >= 3:
                    print(f"    Response complete after ~{elapsed}s")
                    await page.wait_for_timeout(2000)  # Final render wait
                    return True
            else:
                stable_count = 0
                print(f"    Generating... ({elapsed}s, msgs={current_count})")
        else:
            stable_count = 0
            print(f"    Waiting for response... ({elapsed}s, msgs={current_count}, running={has_running})")

        await page.wait_for_timeout(2000)

    print(f"    WARNING: Timeout after {timeout}s. Taking screenshot anyway.")
    return False


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 900},
            locale="zh-CN",
        )
        page = await context.new_page()

        print("=" * 60)
        print("PPT RAG E2E Test - Chainlit UI")
        print("=" * 60)

        # Step 1: Load the page
        print("\n[Step 1] Loading Chainlit interface...")
        await page.goto("http://localhost:8501", wait_until="networkidle", timeout=30000)
        await page.wait_for_selector("#chat-input", timeout=20000)
        await page.wait_for_timeout(3000)

        # Initial state
        initial_msg_count = await get_message_count(page)
        print(f"    Chat loaded. Initial message count: {initial_msg_count}")

        await page.screenshot(
            path=f"{SCREENSHOT_DIR}/00_initial.png",
            full_page=True
        )
        print("    Screenshot: 00_initial.png")

        # Step 2: Ask questions one by one
        for q_idx, (q_text, label) in enumerate(QUESTIONS):
            print(f"\n{'=' * 60}")
            print(f"[Q{q_idx + 1}] {q_text.split(chr(10))[0]}")
            print(f"{'=' * 60}")

            msg_before = await get_message_count(page)
            print(f"    Messages before: {msg_before}")

            # Find and fill the chat input
            input_div = page.locator("#chat-input")
            await input_div.click()
            await page.wait_for_timeout(300)
            await input_div.fill("")  # clear
            await input_div.click()
            await page.wait_for_timeout(200)

            # Type the question
            await input_div.fill(q_text)
            await page.wait_for_timeout(500)

            print(f"    Sending message...")

            # Send via Enter key
            await input_div.press("Enter")

            # Wait for the response to complete
            success = await wait_for_assistant_response(page, msg_before)

            # Take full-page screenshot after response
            screenshot_path = f"{SCREENSHOT_DIR}/{label}_response.png"
            await page.screenshot(
                path=screenshot_path,
                full_page=True
            )
            print(f"    Screenshot saved: {label}_response.png ({'OK' if success else 'MAY BE INCOMPLETE'})")

            # Log the latest exchange
            chat_text = await get_all_chat_text(page)
            # Find the relevant part (last ~1000 chars)
            print(f"    --- Chat excerpt (last 800 chars) ---")
            print(chat_text[-800:] if len(chat_text) > 800 else chat_text)
            print(f"    --- End excerpt ---")

            await page.wait_for_timeout(2000)

        # Final screenshot
        await page.screenshot(
            path=f"{SCREENSHOT_DIR}/99_final.png",
            full_page=True
        )
        print(f"\n[Final] Screenshot: 99_final.png")

        await browser.close()

        print(f"\n{'=' * 60}")
        print(f"All screenshots saved in: {SCREENSHOT_DIR}")
        files = sorted([f for f in os.listdir(SCREENSHOT_DIR) if f.endswith('.png')])
        for f in files:
            size = os.path.getsize(os.path.join(SCREENSHOT_DIR, f))
            print(f"  {f:40s} {size:>8,d} bytes")
        print(f"{'=' * 60}")


if __name__ == "__main__":
    asyncio.run(main())
