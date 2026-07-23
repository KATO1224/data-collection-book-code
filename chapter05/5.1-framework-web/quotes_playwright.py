"""使用 Playwright 采集 Quotes to Scrape JavaScript 页面。"""

import csv
from pathlib import Path

from playwright.sync_api import (
    Error as PlaywrightError,
    TimeoutError as PlaywrightTimeoutError,
    sync_playwright,
)


START_URL = "https://quotes.toscrape.com/js/"
MAX_PAGES = 5
PAGE_TIMEOUT_MS = 15_000

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = OUTPUT_DIR / "quotes_playwright.csv"


def extract_current_page(page, page_number):
    """提取当前页面中已经由 JavaScript 渲染完成的名言数据。"""
    page.locator(".quote").first.wait_for(
        state="visible",
        timeout=PAGE_TIMEOUT_MS,
    )

    records = []
    quote_cards = page.locator(".quote")

    for index in range(quote_cards.count()):
        card = quote_cards.nth(index)
        tags = card.locator(".tags .tag").all_inner_texts()
        records.append(
            {
                "page": page_number,
                "text": card.locator(".text").inner_text().strip(),
                "author": card.locator(".author").inner_text().strip(),
                "tags": ",".join(tag.strip() for tag in tags),
            }
        )

    return records


def collect_quotes(max_pages=MAX_PAGES):
    """打开浏览器并按页采集名言。"""
    all_records = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.goto(
                START_URL,
                wait_until="domcontentloaded",
                timeout=PAGE_TIMEOUT_MS,
            )

            for page_number in range(1, max_pages + 1):
                current_records = extract_current_page(page, page_number)
                all_records.extend(current_records)
                print(
                    f"第 {page_number} 页采集完成，"
                    f"共获取 {len(current_records)} 条记录。"
                )

                next_button = page.locator("li.next > a")
                if page_number == max_pages or next_button.count() == 0:
                    break

                first_text_before_click = (
                    page.locator(".quote .text").first.inner_text().strip()
                )
                next_button.click()

                try:
                    page.wait_for_function(
                        """
                        oldText => {
                            const element = document.querySelector(".quote .text");
                            return element
                                && element.textContent.trim() !== oldText;
                        }
                        """,
                        arg=first_text_before_click,
                        timeout=PAGE_TIMEOUT_MS,
                    )
                except PlaywrightTimeoutError:
                    print("页面内容更新等待超时，程序停止继续翻页。")
                    break
        finally:
            browser.close()

    return all_records


def save_to_csv(records, output_file=OUTPUT_FILE):
    """将采集结果保存为 CSV 文件。"""
    with output_file.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["page", "text", "author", "tags"],
        )
        writer.writeheader()
        writer.writerows(records)


def main():
    try:
        records = collect_quotes()
    except (PlaywrightError, PlaywrightTimeoutError) as error:
        print(f"网页采集失败，请检查网络连接和浏览器组件：{error}")
        return

    save_to_csv(records)
    print(f"采集结束，共获取 {len(records)} 条记录。")
    print(f"结果文件保存至：{OUTPUT_FILE.resolve()}")


if __name__ == "__main__":
    main()
