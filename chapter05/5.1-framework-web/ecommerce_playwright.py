"""使用 Playwright 采集 Web Scraper 电商 AJAX 分页示例。"""

import csv
from pathlib import Path
from urllib.parse import urljoin

from playwright.sync_api import (
    Error as PlaywrightError,
    TimeoutError as PlaywrightTimeoutError,
    sync_playwright,
)


START_URL = (
    "https://webscraper.io/test-sites/e-commerce/ajax/computers/laptops"
)
BASE_URL = "https://webscraper.io"
MAX_PAGES = 3
PAGE_TIMEOUT_MS = 20_000

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = OUTPUT_DIR / "ecommerce_playwright.csv"


def get_product_cards(page):
    """返回当前页面的商品卡片，兼容训练站点的新旧容器类名。"""
    thumbnail_cards = page.locator(".thumbnail")
    if thumbnail_cards.count() > 0:
        return thumbnail_cards
    return page.locator(".product-wrapper")


def safe_inner_text(locator):
    """当节点存在时提取文字，否则返回空字符串。"""
    if locator.count() == 0:
        return ""
    return locator.first.inner_text().strip()


def extract_current_page(page, page_number):
    """提取当前页面中已经显示的商品数据。"""
    page.locator(".thumbnail, .product-wrapper").first.wait_for(
        state="visible",
        timeout=PAGE_TIMEOUT_MS,
    )

    records = []
    cards = get_product_cards(page)

    for index in range(cards.count()):
        card = cards.nth(index)
        title_node = card.locator("a.title").first
        title = (
            title_node.get_attribute("title")
            or safe_inner_text(title_node)
        )
        href = title_node.get_attribute("href") or ""

        records.append(
            {
                "page": page_number,
                "title": title,
                "price": safe_inner_text(card.locator("h4.price")),
                "description": safe_inner_text(
                    card.locator("p.description")
                ),
                "reviews": safe_inner_text(
                    card.locator(".ratings p.pull-right")
                ),
                "product_url": urljoin(BASE_URL, href) if href else "",
            }
        )

    return records


def find_next_button(page, next_page_number):
    """优先按页码定位 AJAX 分页按钮，并兼容旧版下一页按钮。"""
    numbered_button = page.get_by_role(
        "button",
        name=str(next_page_number),
        exact=True,
    )
    if numbered_button.count() > 0:
        return numbered_button.first
    return page.locator("button.next").first


def collect_products(max_pages=MAX_PAGES):
    """自动完成动态分页并采集商品记录。"""
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
                    f"共获取 {len(current_records)} 条商品记录。"
                )

                if page_number == max_pages:
                    break

                next_button = find_next_button(page, page_number + 1)
                if next_button.count() == 0 or not next_button.is_enabled():
                    print("页面中不存在可用的下一页按钮，采集结束。")
                    break

                first_title_before_click = (
                    page.locator("a.title").first.inner_text().strip()
                )
                next_button.click()

                try:
                    page.wait_for_function(
                        """
                        oldTitle => {
                            const firstTitle = document.querySelector("a.title");
                            return firstTitle
                                && firstTitle.textContent.trim() !== oldTitle;
                        }
                        """,
                        arg=first_title_before_click,
                        timeout=PAGE_TIMEOUT_MS,
                    )
                except PlaywrightTimeoutError:
                    print("下一页商品数据更新等待超时，程序停止运行。")
                    break
        finally:
            browser.close()

    return all_records


def save_to_csv(records, output_file=OUTPUT_FILE):
    """将商品采集结果保存为 CSV 文件。"""
    with output_file.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "page",
                "title",
                "price",
                "description",
                "reviews",
                "product_url",
            ],
        )
        writer.writeheader()
        writer.writerows(records)


def main():
    try:
        records = collect_products()
    except (PlaywrightError, PlaywrightTimeoutError) as error:
        print(f"电商页面采集失败，请检查网络连接或页面结构：{error}")
        return

    save_to_csv(records)
    print(f"采集结束，共获取 {len(records)} 条商品记录。")
    print(f"结果文件保存至：{OUTPUT_FILE.resolve()}")


if __name__ == "__main__":
    main()
