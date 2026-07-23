"""使用 Requests 重放接口请求，采集 Quotes to Scrape 名言数据。"""

import csv
from pathlib import Path

import requests


API_URL = "https://quotes.toscrape.com/api/quotes"
MAX_PAGES = 5
REQUEST_TIMEOUT = 15

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = OUTPUT_DIR / "quotes_api_requests.csv"


def collect_quotes(max_pages=MAX_PAGES):
    """通过接口请求采集指定页数的名言数据。"""
    all_records = []

    with requests.Session() as session:
        session.headers.update(
            {"User-Agent": "data-collection-book-code/1.0 (teaching example)"}
        )

        for requested_page in range(1, max_pages + 1):
            try:
                response = session.get(
                    API_URL,
                    params={"page": requested_page},
                    timeout=REQUEST_TIMEOUT,
                )
                response.raise_for_status()
                data = response.json()
            except (requests.RequestException, ValueError) as error:
                print(f"第 {requested_page} 页接口请求失败：{error}")
                break

            response_page = data.get("page", requested_page)
            quotes = data.get("quotes", [])

            for item in quotes:
                author = item.get("author") or {}
                all_records.append(
                    {
                        "page": response_page,
                        "text": item.get("text", "").strip(),
                        "author": author.get("name", "").strip(),
                        "tags": ",".join(item.get("tags") or []),
                    }
                )

            print(
                f"第 {response_page} 页接口采集完成，"
                f"共获取 {len(quotes)} 条记录。"
            )

            if not data.get("has_next", False):
                break

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
    records = collect_quotes()
    save_to_csv(records)
    print(f"采集结束，共获取 {len(records)} 条记录。")
    print(f"结果文件保存至：{OUTPUT_FILE.resolve()}")


if __name__ == "__main__":
    main()
