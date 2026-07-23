"""定时采集服务器资源使用情况，并根据阈值给出预警。"""

import csv
import platform
import time
from datetime import datetime
from pathlib import Path

import psutil


# 采集间隔（秒）与采集次数。
INTERVAL = 5
COUNT = 6

# CPU、内存和磁盘使用率预警阈值（百分比）。
CPU_WARNING = 80
MEMORY_WARNING = 80
DISK_WARNING = 85

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = OUTPUT_DIR / "server_resource_monitor.csv"

# Windows 与 Linux 的磁盘根路径不同，程序根据系统自动选择。
if platform.system() == "Windows":
    DISK_PATH = Path.home().anchor
else:
    DISK_PATH = "/"


def build_warning(cpu_percent, memory_percent, disk_percent):
    """根据预设阈值生成资源预警文字。"""
    warnings = []

    if cpu_percent >= CPU_WARNING:
        warnings.append(f"CPU使用率过高：{cpu_percent}%")
    if memory_percent >= MEMORY_WARNING:
        warnings.append(f"内存使用率过高：{memory_percent}%")
    if disk_percent >= DISK_WARNING:
        warnings.append(f"磁盘使用率过高：{disk_percent}%")

    return "；".join(warnings) if warnings else "正常"


def collect_once():
    """采集一次服务器 CPU、内存、磁盘和网络状态。"""
    # interval=1 表示在 1 秒采样窗口内计算 CPU 使用率。
    cpu_percent = psutil.cpu_percent(interval=1)

    # 采集内存使用率和当前可用内存。
    memory = psutil.virtual_memory()
    memory_percent = memory.percent
    memory_available_mb = memory.available / 1024**2

    # 采集系统盘使用率和剩余空间。
    disk = psutil.disk_usage(DISK_PATH)
    disk_percent = disk.percent
    disk_free_gb = disk.free / 1024**3

    # 网络计数器是系统启动以来的累计发送量和接收量。
    network = psutil.net_io_counters()
    net_sent_mb = network.bytes_sent / 1024**2
    net_recv_mb = network.bytes_recv / 1024**2

    return {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cpu_percent": round(cpu_percent, 2),
        "memory_percent": round(memory_percent, 2),
        "memory_available_mb": round(memory_available_mb, 2),
        "disk_percent": round(disk_percent, 2),
        "disk_free_gb": round(disk_free_gb, 2),
        "net_sent_mb": round(net_sent_mb, 2),
        "net_recv_mb": round(net_recv_mb, 2),
        "warning": build_warning(
            round(cpu_percent, 2),
            round(memory_percent, 2),
            round(disk_percent, 2),
        ),
    }


def save_to_csv(records, output_file=OUTPUT_FILE):
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
                "net_sent_mb",
                "net_recv_mb",
                "warning",
            ],
        )
        writer.writeheader()
        writer.writerows(records)


def print_record(record):
    """在终端输出一次采集结果和预警状态。"""
    print(
        f"[{record['time']}] "
        f"CPU: {record['cpu_percent']}% | "
        f"内存: {record['memory_percent']}% "
        f"(可用 {record['memory_available_mb']} MB) | "
        f"磁盘: {record['disk_percent']}% "
        f"(剩余 {record['disk_free_gb']} GB) | "
        f"网络发送/接收: "
        f"{record['net_sent_mb']}/{record['net_recv_mb']} MB"
    )
    if record["warning"] != "正常":
        print(f"预警：{record['warning']}")
    else:
        print("状态：正常")


def main():
    records = []
    print("服务器资源使用监控开始")
    print(f"采集间隔：{INTERVAL} 秒；采集次数：{COUNT} 次")
    print("-" * 72)

    for index in range(COUNT):
        record = collect_once()
        records.append(record)
        print_record(record)

        if index < COUNT - 1:
            time.sleep(INTERVAL)

    save_to_csv(records)
    print("-" * 72)
    print("服务器资源使用监控结束")
    print(f"采集结果保存至：{OUTPUT_FILE.resolve()}")


if __name__ == "__main__":
    main()
