"""通过 Prometheus /metrics 接口暴露操作系统指标。"""

import platform
import time
from pathlib import Path

import psutil
from prometheus_client import Gauge, start_http_server


PORT = 8000
UPDATE_INTERVAL = 5

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

if platform.system() == "Windows":
    DISK_PATH = Path.home().anchor
else:
    DISK_PATH = "/"

CPU_PERCENT = Gauge("os_cpu_percent", "CPU usage percent")
MEMORY_PERCENT = Gauge("os_memory_percent", "Memory usage percent")
DISK_PERCENT = Gauge("os_disk_percent", "Disk usage percent")
MEMORY_AVAILABLE_MB = Gauge(
    "os_memory_available_mb",
    "Available memory in MB",
)
DISK_FREE_GB = Gauge("os_disk_free_gb", "Free disk space in GB")
NETWORK_BYTES_SENT = Gauge(
    "os_network_bytes_sent",
    "Total bytes sent",
)
NETWORK_BYTES_RECV = Gauge(
    "os_network_bytes_recv",
    "Total bytes received",
)


def update_metrics():
    """采集一次系统状态并更新 Prometheus 指标值。"""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage(DISK_PATH)
    network = psutil.net_io_counters()

    CPU_PERCENT.set(cpu_percent)
    MEMORY_PERCENT.set(memory.percent)
    DISK_PERCENT.set(disk.percent)
    MEMORY_AVAILABLE_MB.set(round(memory.available / 1024**2, 2))
    DISK_FREE_GB.set(round(disk.free / 1024**3, 2))
    NETWORK_BYTES_SENT.set(network.bytes_sent)
    NETWORK_BYTES_RECV.set(network.bytes_recv)


def main():
    start_http_server(PORT, addr="127.0.0.1")
    print(f"指标服务已启动：http://127.0.0.1:{PORT}/metrics")
    print("按 Ctrl+C 停止服务。")

    try:
        while True:
            update_metrics()
            time.sleep(UPDATE_INTERVAL)
    except KeyboardInterrupt:
        print("\n指标服务已停止。")


if __name__ == "__main__":
    main()
