# 《数据采集》教材配套代码

《数据采集》教材第 5.1 节、第 5.2 节和第 6.1 节配套代码与教学材料。

本仓库根据书稿中的完整案例整理而成。

## 章节对应关系

| 教材章节 | GitHub目录 | 主要内容 |
| --- | --- | --- |
| 5.1 框架网页数据采集 | `chapter05/5.1-framework-web` | Playwright、Requests、Vue 状态识别和电商案例 |
| 5.2 操作系统数据采集 | `chapter05/5.2-operating-system` | psutil、os、subprocess 和指标上报 |
| 6.1 科研数据采集 | `chapter06/6.1-research-data` | CNKI、Web of Science 和 Scopus 导出说明与模板 |

## 目录结构

```text
data-collection-book-code/
├── README.md
├── CODE_CHECK_REPORT.md
├── CHANGELOG.md
├── requirements.txt
├── .gitignore
├── chapter05/
│   ├── 5.1-framework-web/
│   │   ├── README.md
│   │   ├── quotes_playwright.py
│   │   ├── quotes_api_requests.py
│   │   ├── vue_grid_playwright.py
│   │   ├── ecommerce_playwright.py
│   │   ├── compare_static_playwright.py
│   │   └── outputs/
│   └── 5.2-operating-system/
│       ├── README.md
│       ├── system_metrics.py
│       ├── os_demo.py
│       ├── subprocess_demo.py
│       ├── metrics_exporter_demo.py
│       ├── server_resource_monitor.py
│       └── outputs/
└── chapter06/
    └── 6.1-research-data/
        ├── README.md
        └── templates/
            ├── research_export_template.csv
            └── collection_record_template.csv
```

## 运行环境

- Python 3.10 或以上版本
- Windows 10/11 或常见 Linux 发行版
- 运行 5.1 网络案例时需要能够访问对应教学网站
- `subprocess_demo.py` 中的 `vmstat` 案例主要适用于 Linux

建议在项目根目录创建虚拟环境并安装依赖：

```bash
python -m venv .venv
```

Windows PowerShell：

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Linux：

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
```

安装 Playwright 后还必须安装 Chromium 浏览器组件：

```bash
playwright install chromium
```

## 运行入口

在项目根目录执行以下命令。

5.1 框架网页数据采集：

```bash
python chapter05/5.1-framework-web/quotes_playwright.py
python chapter05/5.1-framework-web/quotes_api_requests.py
python chapter05/5.1-framework-web/vue_grid_playwright.py
python chapter05/5.1-framework-web/ecommerce_playwright.py
python chapter05/5.1-framework-web/compare_static_playwright.py
```

5.2 操作系统数据采集：

```bash
python chapter05/5.2-operating-system/system_metrics.py
python chapter05/5.2-operating-system/os_demo.py
python chapter05/5.2-operating-system/subprocess_demo.py
python chapter05/5.2-operating-system/metrics_exporter_demo.py
python chapter05/5.2-operating-system/server_resource_monitor.py
```

各程序的目标、参数和输出字段见相应章节的 README。

## 输出文件

程序运行结果统一写入脚本所在章节的 `outputs` 目录：

- `chapter05/5.1-framework-web/outputs`
- `chapter05/5.2-operating-system/outputs`

运行结果已在 `.gitignore` 中排除，仅保留空目录占位文件 `.gitkeep`。第 6.1 节的两个 CSV 文件是教材模板，会正常纳入版本管理。

## Windows 与 Linux 兼容性

`psutil` 案例会自动选择系统盘路径：Windows 使用当前用户主目录所在盘的根路径，Linux 使用 `/`。`os_demo.py`、`system_metrics.py`、`metrics_exporter_demo.py` 和 `server_resource_monitor.py` 均可在两类系统运行。

`subprocess_demo.py` 调用 `vmstat 1 3`，主要用于 Linux 教学环境。Windows 未安装 `vmstat` 时，程序会生成说明文件并安全退出，不会使用 `shell=True`。

## 合规与授权

5.1 的程序仅用于公开教学站点的小规模学习实验。运行前应确认目标网站的服务条款、robots 规则、访问频率要求和数据使用范围，不得绕过登录、验证码、访问控制或技术保护措施，不得采集个人敏感信息。

6.1 不包含 API 调用、自动化抓取、模拟登录或数据库实际批量数据。使用 CNKI、Web of Science、Scopus 等科研数据库时，应通过学校、科研机构或数据库官方网站提供的正规入口，在机构授权、平台导出限制和数据版权许可范围内操作。

## 常见错误

- `ModuleNotFoundError`：确认已激活虚拟环境，并重新执行 `python -m pip install -r requirements.txt`。
- 找不到 Chromium：执行 `playwright install chromium`，并确认该命令与运行脚本使用同一个 Python 环境。
- 页面等待超时：确认网络能够访问目标站点；网站结构更新后，需用开发者工具重新核对选择器。
- 在 Spyder 或 Jupyter 中出现同步 API/事件循环错误：把脚本保存后从终端运行，或将案例改写为 Playwright 异步 API。
- Windows 找不到 `vmstat`：这是预期的系统差异；在 Linux 环境运行该案例。
- 8000 端口被占用：先停止占用端口的程序，或修改 `metrics_exporter_demo.py` 中的 `PORT` 常量。
- CSV 在 Excel 中显示异常：程序输出使用 `utf-8-sig`；若被其他软件转换编码，请重新以 UTF-8 打开。

