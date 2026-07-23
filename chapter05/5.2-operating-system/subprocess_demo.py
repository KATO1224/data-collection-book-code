"""使用 subprocess 安全调用 Linux vmstat 命令。"""

import shutil
import subprocess
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = OUTPUT_DIR / "vmstat_result.txt"


def run_vmstat():
    """运行 vmstat 1 3，并返回命令结果；不使用 shell。"""
    vmstat_path = shutil.which("vmstat")
    if vmstat_path is None:
        return None

    try:
        return subprocess.run(
            [vmstat_path, "1", "3"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        return error


def save_result(result, output_file=OUTPUT_FILE):
    """保存命令返回码、标准输出和标准错误。"""
    with output_file.open("w", encoding="utf-8") as file:
        if result is None:
            file.write("当前系统未找到 vmstat 命令。\n")
            return

        if isinstance(result, Exception):
            file.write(f"vmstat 命令执行失败：{result}\n")
            return

        file.write(f"返回码：{result.returncode}\n")
        file.write("\n标准输出：\n")
        file.write(result.stdout or "（无）\n")
        file.write("\n标准错误：\n")
        file.write(result.stderr or "（无）\n")


def main():
    result = run_vmstat()
    save_result(result)

    if result is None:
        print("当前系统未找到 vmstat 命令；该案例主要适用于 Linux。")
    elif isinstance(result, Exception):
        print(f"vmstat 命令执行失败：{result}")
    elif result.returncode != 0:
        print(f"vmstat 命令返回非零状态码：{result.returncode}")
    else:
        print("subprocess 模块示例运行完成。")

    print(f"结果文件保存至：{OUTPUT_FILE.resolve()}")


if __name__ == "__main__":
    main()
