"""比较静态请求与 Playwright 渲染采集同一批商品的结果。"""

import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import (
    Error as PlaywrightError,
    TimeoutError as PlaywrightTimeoutError,
    sync_playwright,
)


START_URL = (
    "https://webscraper.io/test-sites/e-commerce/ajax/computers/laptops"
)
REQUEST_TIMEOUT = 15
PAGE_TIMEOUT_MS = 20_000

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def select_static_cards(soup):
    """兼容训练站点的新旧商品卡片类名。"""
    cards = soup.select(".thumbnail")
    return cards if cards else soup.select(".product-wrapper")


def collect_by_requests():
    """使用 Requests 获取初始 HTML 并尝试提取可见商品。"""
    start_time = time.perf_counter()
    response = requests.get(
        START_URL,
        headers={
            "User-Agent": "data-collection-book-code/1.0 (teaching example)"
        },
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    records = []

    for card in select_static_cards(soup):
        title_node = card.select_one("a.title")
        price_node = card.select_one("h4.price")
        description_node = card.select_one("p.description")
        records.append(
            {
                "title": (
                    title_node.get("title")
                    or title_node.get_text(strip=True)
                    if title_node
                    else ""
                ),
                "price": (
                    price_node.get_text(strip=True)
                    if price_node
                    else ""
                ),
                "description": (
                    description_node.get_text(strip=True)
                    if description_node
                    else ""
                ),
            }
        )

    elapsed_time = time.perf_counter() - start_time
    return records, elapsed_time


def get_rendered_cards(page):
    """兼容训练站点的新旧商品卡片类名。"""
    thumbnail_cards = page.locator(".thumbnail")
    if thumbnail_cards.count() > 0:
        return thumbnail_cards
    return page.locator(".product-wrapper")


def collect_by_playwright():
    """使用 Playwright 等待页面渲染后提取同一批可见商品。"""
    start_time = time.perf_counter()
    records = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.goto(
                START_URL,
                wait_until="domcontentloaded",
                timeout=PAGE_TIMEOUT_MS,
            )
            page.locator(".thumbnail, .product-wrapper").first.wait_for(
                state="visible",
                timeout=PAGE_TIMEOUT_MS,
            )

            cards = get_rendered_cards(page)
            for index in range(cards.count()):
                card = cards.nth(index)
                title_node = card.locator("a.title").first
                records.append(
                    {
                        "title": (
                            title_node.get_attribute("title")
                            or title_node.inner_text().strip()
                        ),
                        "price": (
                            card.locator("h4.price")
                            .first.inner_text()
                            .strip()
                        ),
                        "description": (
                            card.locator("p.description")
                            .first.inner_text()
                            .strip()
                        ),
                    }
                )
        finally:
            browser.close()

    elapsed_time = time.perf_counter() - start_time
    return records, elapsed_time


def print_result(method_name, records, elapsed_time, error=None):
    """输出一种采集方式的实验结果。"""
    print(f"\n{method_name}")
    if error is not None:
        print(f"执行失败：{error}")
        return

    print(f"采集记录数：{len(records)}")
    print(f"运行时间：{elapsed_time:.4f} 秒")
    if records:
        print(f"首条商品数据：{records[0]}")
    else:
        print("未提取到商品记录。")


def main():
    static_records = []
    static_time = 0.0
    static_error = None
    try:
        static_records, static_time = collect_by_requests()
    except requests.RequestException as error:
        static_error = error

    rendered_records = []
    rendered_time = 0.0
    rendered_error = None
    try:
        rendered_records, rendered_time = collect_by_playwright()
    except (PlaywrightError, PlaywrightTimeoutError) as error:
        rendered_error = error

    print_result(
        "方法一：Requests + BeautifulSoup 静态解析",
        static_records,
        static_time,
        static_error,
    )
    print_result(
        "方法二：Playwright 浏览器渲染采集",
        rendered_records,
        rendered_time,
        rendered_error,
    )

    print("\n比较范围：同一 URL 首次打开后显示的首批商品。")
    if static_error is None and rendered_error is None:
        difference = len(rendered_records) - len(static_records)
        print(f"渲染方式比静态方式多提取 {difference} 条记录。")
    print("实验比较完成。")


if __name__ == "__main__":
    main()
