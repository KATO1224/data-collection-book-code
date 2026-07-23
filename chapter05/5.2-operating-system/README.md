# 5.2 操作系统数据采集

本目录对应教材第 5.2 节，包含 `psutil` 基础采集、`os` 环境信息、`subprocess` 命令调用、Prometheus 指标暴露和服务器资源监控五个案例。

## 环境与适用范围

安装第三方依赖：

```bash
python -m pip install psutil prometheus-client
```

也可以在项目根目录一次安装全部依赖：

```bash
python -m pip install -r requirements.txt
```

| 程序 | Windows | Linux | 输出 |
| --- | --- | --- | --- |
| `system_metrics.py` | 支持 | 支持 | CSV |
| `os_demo.py` | 支持 | 支持 | 文本 |
| `subprocess_demo.py` | 通常无 `vmstat` | 主要适用 | 文本 |
| `metrics_exporter_demo.py` | 支持 | 支持 | `/metrics` HTTP 接口 |
| `server_resource_monitor.py` | 支持 | 支持 | CSV |

程序结果统一写入本目录下的 `outputs`。Windows 自动采集当前用户主目录所在系统盘，Linux 采集根文件系统 `/`。

## `system_metrics.py`

对应教材中的 `psutil` 基础采集案例。程序默认采集 5 次，CPU 采样窗口为 1 秒，两次记录之间等待 2 秒。

```bash
python chapter05/5.2-operating-system/system_metrics.py
```

输出文件为 `outputs/system_metrics.csv`，包含：

```text
time,cpu_percent,memory_percent,memory_available_mb,disk_percent,disk_free_gb,bytes_sent,bytes_recv
```

如需调整采集行为，可修改文件顶部的 `COUNT` 和 `INTERVAL` 常量。

## `os_demo.py`

对应教材中的 `os` 模块案例。程序获取当前工作目录、用户主目录、`os.name`、系统名称、系统版本和 Python 版本，并记录采集时间。

```bash
python chapter05/5.2-operating-system/os_demo.py
```

输出文件为 `outputs/os_info.txt`。

## `subprocess_demo.py`

对应教材中的 `subprocess` 模块案例，主要适用于安装了 `vmstat` 的 Linux 系统。程序先使用 `shutil.which()` 判断命令是否存在，再以参数列表形式执行：

```text
vmstat 1 3
```

```bash
python chapter05/5.2-operating-system/subprocess_demo.py
```

输出文件为 `outputs/vmstat_result.txt`，包含返回码、标准输出和标准错误。程序没有使用 `shell=True`，也没有把外部输入拼接为系统命令。Windows 未找到 `vmstat` 时会写入说明后正常退出。

## `metrics_exporter_demo.py`

对应教材 5.2.3.3“可视化与上报方案”。程序使用 `psutil` 更新 CPU、内存、磁盘和网络 Gauge 指标，在本机 8000 端口启动 HTTP 服务，默认每 5 秒更新一次。

启动服务：

```bash
python chapter05/5.2-operating-system/metrics_exporter_demo.py
```

Linux/macOS 或带有 `grep` 的终端可使用：

```bash
curl -s http://127.0.0.1:8000/metrics | grep os_
```

Windows PowerShell 可使用：

```powershell
(Invoke-WebRequest http://127.0.0.1:8000/metrics).Content |
    Select-String "os_"
```

浏览器也可以直接访问 `http://127.0.0.1:8000/metrics`。这是长期运行服务，使用 `Ctrl+C` 停止。如 8000 端口被占用，可修改程序顶部的 `PORT` 常量。

## `server_resource_monitor.py`

对应教材 5.2.5“实例：服务器资源使用监控脚本”。默认参数如下：

| 参数 | 默认值 | 含义 |
| --- | ---: | --- |
| `INTERVAL` | 5 | 两次记录之间的等待秒数 |
| `COUNT` | 6 | 采集次数 |
| `CPU_WARNING` | 80 | CPU 使用率预警阈值（%） |
| `MEMORY_WARNING` | 80 | 内存使用率预警阈值（%） |
| `DISK_WARNING` | 85 | 磁盘使用率预警阈值（%） |

运行：

```bash
python chapter05/5.2-operating-system/server_resource_monitor.py
```

程序每次都会在终端显示 CPU、内存、磁盘、网络累计发送/接收量与预警状态。输出文件为 `outputs/server_resource_monitor.csv`。修改顶部常量即可完成教材中的采集间隔、次数和阈值实验。

## 常见问题

- `ModuleNotFoundError: psutil`：执行 `python -m pip install psutil`。
- `vmstat` 不存在：该案例主要用于 Linux；Debian/Ubuntu 通常由 `procps` 软件包提供。
- `Permission denied`：只采集当前用户有权读取的系统状态，不要为了普通指标采集随意使用管理员权限。
- 8000 端口被占用：停止已有服务或修改 `PORT`。
- CSV 无数据：确认程序已正常完成全部采集；运行中强制关闭不会写出最终 CSV。
