import os
import time
from datetime import datetime
from playwright.async_api import async_playwright
from app.core.config import settings


class QAWebMonitor:
    @staticmethod
    async def run_check(url: str, expected_selector: str = None):
        result = {
            "status_code": None,
            "response_time": 0.0,
            "is_up": False,
            "error_message": None,
            "screenshot_path": None,
        }

        start_time = time.time()

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/58.0.3029.110 Safari/537.3"
                )
            )
            page = await context.new_page()

            try:
                response = await page.goto(url, wait_until="domcontentloaded", timeout=10000)

                if response:
                    result["status_code"] = response.status

                if response and response.status >= 400:
                    raise Exception(f"La página devolvió un error: {response.status}")

                if expected_selector:
                    await page.wait_for_selector(expected_selector, timeout=5000)

                result["is_up"] = True

            except Exception as e:
                result["is_up"] = False
                result["error_message"] = str(e)

            finally:
                result["response_time"] = time.time() - start_time

                try:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    clean_url = url.replace("://", "_").replace("/", "_")
                    screenshot_filename = f"{clean_url}_{timestamp}.png"
                    screenshot_path = os.path.join(settings.SCREENSHOT_DIR, screenshot_filename)

                    os.makedirs(settings.SCREENSHOT_DIR, exist_ok=True)
                    await page.screenshot(path=screenshot_path)
                    result["screenshot_path"] = screenshot_path
                except Exception as screenshot_error:
                    result["error_message"] = (
                        result.get("error_message") or ""
                    ) + f" | Screenshot error: {screenshot_error}"

                await browser.close()

        return result