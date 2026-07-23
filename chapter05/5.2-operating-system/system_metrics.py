"""使用 psutil 连续采集基础系统指标并保存为 CSV。"""

import csv
import platform
import time
from datetime import datetime
from pathlib import Path

import psutil


INTERVAL = 2
COUNT = 5

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = OUTPUT_DIR / "system_metrics.csv"

if platform.system() == "Windows":
    DISK_PATH = Path.home().anchor
else:
    DISK_PATH = "/"


def collect_once():
    """采集一次 CPU、内存、磁盘和网络状态。"""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage(DISK_PATH)
    network = psutil.net_io_counters()

    return {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cpu_percent": round(cpu_percent, 2),
        "memory_percent": round(memory.percent, 2),
        "memory_available_mb": round(memory.available / 1024**2, 2),
        "disk_percent": round(disk.percent, 2),
        "disk_free_gb": round(disk.free / 1024**3, 2),
        "bytes_sent": network.bytes_sent,
        "bytes_recv": network.bytes_recv,
    }


def save_records(records, output_file=OUTPUT_FILE):
    """将采集结果保存为 CSV 文件。"""
    with output_file.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "time",
                "cpu_percent",
                "memory_percent",
                "memory_available_mb",
                "disk_percent",
                "disk_free_gb",
                "bytes_sent",
                "bytes_recv",
            ],
        )
        writer.writeheader()
        writer.writerows(records)


def main():
    records = []

    for index in range(COUNT):
        record = collect_once()
        records.append(record)
        print(
            f"[{record['time']}] "
            f"CPU: {record['cpu_percent']}% | "
            f"内存: {record['memory_percent']}% "
            f"(可用 {record['memory_available_mb']} MB) | "
            f"磁盘: {record['disk_percent']}% "
            f"(剩余 {record['disk_free_gb']} GB)"
        )

        if index < COUNT - 1:
            time.sleep(INTERVAL)

    save_records(records)
    print(f"采集完成，结果文件保存至：{OUTPUT_FILE.resolve()}")


if __name__ == "__main__":
    main()
