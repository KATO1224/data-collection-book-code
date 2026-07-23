"""演示使用 os 模块采集路径和基础系统环境信息。"""

import os
import platform
from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = OUTPUT_DIR / "os_info.txt"


def collect_environment_info():
    """获取当前工作目录、用户主目录和操作系统环境信息。"""
    return {
        "采集时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "当前工作目录": os.getcwd(),
        "用户主目录": str(Path.home()),
        "os.name": os.name,
        "系统名称": platform.system(),
        "系统版本": platform.release(),
        "Python版本": platform.python_version(),
    }


def save_info(info, output_file=OUTPUT_FILE):
    """将系统环境信息保存为 UTF-8 文本文件。"""
    with output_file.open("w", encoding="utf-8") as file:
        for field, value in info.items():
            file.write(f"{field}：{value}\n")


def main():
    info = collect_environment_info()
    save_info(info)

    print("os 模块示例运行完成。")
    for field, value in info.items():
        print(f"{field}：{value}")
    print(f"结果文件保存至：{OUTPUT_FILE.resolve()}")


if __name__ == "__main__":
    main()
