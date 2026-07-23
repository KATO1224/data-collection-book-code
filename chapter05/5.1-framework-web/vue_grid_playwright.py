"""采集 Vue 官方 Grid 示例在不同交互状态下显示的数据。"""

import csv
from pathlib import Path

from playwright.sync_api import (
    Error as PlaywrightError,
    TimeoutError as PlaywrightTimeoutError,
    expect,
    sync_playwright,
)


START_URL = "https://vuejs.org/examples/#grid"
# Vue 在线编辑器需要先编译示例，再把结果写入 iframe；慢速网络下
# 该过程可能明显长于普通页面元素加载。
PAGE_TIMEOUT_MS = 45_000

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = OUTPUT_DIR / "vue_grid_state_results.csv"


def extract_table_rows(preview_frame, state_name):
    """提取当前页面状态下表格中显示的数据行。"""
    records = []
    rows = preview_frame.locator("tbody tr")

    for index in range(rows.count()):
        cells = rows.nth(index).locator("td").all_inner_texts()
        if len(cells) >= 2:
            records.append(
                {
                    "state": state_name,
                    "name": cells[0].strip(),
                    "power": cells[1].strip(),
                }
            )

    return records


def print_records(title, records):
    """在终端中输出当前状态下采集到的数据。"""
    print(f"\n{title}")
    for record in records:
        print(f"{record['name']} - {record['power']}")


def collect_state_records():
    """依次执行排序、筛选操作并采集四种页面状态。"""
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

            # Vue 示例的运行结果位于页面中的 iframe 预览区域。
            preview = page.frame_locator("iframe").first
            rows = preview.locator("tbody tr")
            rows.first.wait_for(state="visible", timeout=PAGE_TIMEOUT_MS)

            initial_records = extract_table_rows(preview, "初始状态")
            all_records.extend(initial_records)
            print_records("初始状态数据：", initial_records)

            preview.locator("th").filter(has_text="Name").click()
            first_name = rows.first.locator("td").first
            expect(first_name).to_have_text("Jet Li", timeout=PAGE_TIMEOUT_MS)

            name_sorted_records = extract_table_rows(preview, "按Name排序")
            all_records.extend(name_sorted_records)
            print_records("按Name排序后的数据：", name_sorted_records)

            search_box = preview.locator("input[name='query']")
            search_box.fill("0")
            expect(rows).to_have_count(3, timeout=PAGE_TIMEOUT_MS)

            filtered_records = extract_table_rows(preview, "输入0后筛选")
            all_records.extend(filtered_records)
            print_records("输入0后筛选得到的数据：", filtered_records)

            preview.locator("th").filter(has_text="Power").click()
            expect(first_name).to_have_text("Bruce Lee", timeout=PAGE_TIMEOUT_MS)

            power_sorted_records = extract_table_rows(
                preview,
                "输入0后按Power排序",
            )
            all_records.extend(power_sorted_records)
            print_records(
                "输入0后按Power排序的数据：",
                power_sorted_records,
            )
        finally:
            browser.close()

    return all_records


def save_to_csv(records, output_file=OUTPUT_FILE):
    """将不同页面状态下的数据保存为 CSV 文件。"""
    with output_file.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["state", "name", "power"],
        )
        writer.writeheader()
        writer.writerows(records)


def main():
    try:
        records = collect_state_records()
    except (AssertionError, PlaywrightError, PlaywrightTimeoutError) as error:
        print(f"Vue 示例采集失败，请检查网络连接或页面结构：{error}")
        return

    save_to_csv(records)
    print(f"\n采集结束，共记录 {len(records)} 条状态数据。")
    print(f"结果文件保存至：{OUTPUT_FILE.resolve()}")


if __name__ == "__main__":
    main()
