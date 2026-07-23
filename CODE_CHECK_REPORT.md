# 代码检查报告

检查日期：2026-07-23

作者测试说明：作者已确认本仓库中的代码均已实际测试。下文“实际运行结果”记录的是本次仓库整理过程中的独立复核结果，用于说明整理环境和可重复检查范围，不替代作者原有的测试结论。

## 1. 检查范围

本次仅整理和检查书稿中的以下内容：

- 5.1 框架网页数据采集：5 个 Python 程序
- 5.2 操作系统数据采集：5 个 Python 程序
- 6.1 科研数据采集：说明文档与 2 个虚构 CSV 模板

未整理第 5.3 节、第 5.4 节及其他章节。

5.1 和 5.2 程序的案例目标、主要流程和字段来自书稿。整理时只修复排版、语法、路径、跨平台和必要异常处理问题；6.1 按书稿中的官方检索、筛选和导出流程建立模板，不包含 API 或爬虫。

## 2. 语法与静态检查

执行：

```bash
python -m compileall .
```

结果：10 个 Python 文件全部编译通过，无语法或缩进错误。

AST 和文本扫描结果：

| 检查项 | 结果 |
| --- | --- |
| Python 文件数 | 10 |
| 每个文件的 `if __name__ == "__main__"` 数量 | 均为 1 |
| 固定个人路径 `C:\Users\Administrator\...` | 未发现 |
| `Path.home() / "Desktop"` 输出路径 | 未发现 |
| `shell=True` | 未发现 |
| Python 代码中的中文弯引号/中文单引号 | 未发现 |
| 输出目录创建 | 10 个程序均使用脚本目录下的 `outputs` |
| CSV 程序输出编码 | 均为 `utf-8-sig` |
| 网络请求超时 | Requests 与 Playwright 网络案例均已设置 |
| 浏览器关闭 | 使用 `try/finally`，每个浏览器仅关闭一次 |
| `subprocess` 参数 | 使用列表参数，检查命令、返回码、stdout 和 stderr |

两个 6.1 CSV 模板均通过 `csv.DictReader` 读取检查：

- `research_export_template.csv`：11 个规定字段，2 行虚构数据
- `collection_record_template.csv`：10 个规定字段，1 行虚构记录

## 3. 实际运行结果

主要测试环境：

- Windows 10
- Python 3.10.19
- psutil 7.2.2
- Chromium（Playwright）
- 测试日期：2026-07-23

| 程序 | 实际测试结果 | 状态 |
| --- | --- | --- |
| `quotes_playwright.py` | 实际访问教学页面，采集 5 页，每页 10 条，共 50 条；CSV 字段和页码检查通过 | 通过 |
| `quotes_api_requests.py` | 实际请求接口，采集 5 页，每页 10 条，共 50 条；`page/text/author/tags` 检查通过 | 通过 |
| `vue_grid_playwright.py` | 作者已实际测试；本次独立复核中，Vue 页面和 iframe 结构已确认，但当前网络访问其 jsDelivr 编译依赖时发生 TLS/`ERR_CONNECTION_CLOSED`，两次端到端运行均在等待表格渲染时超时 | 作者已测试；本机环境限制 |
| `ecommerce_playwright.py` | 实际完成 3 页 AJAX 分页，每页 6 条，共 18 条；6 个输出字段检查通过 | 通过 |
| `compare_static_playwright.py` | 同一 URL、同一首批范围：Requests + BeautifulSoup 得到 0 条、Playwright 得到 6 条；一次完整运行时间分别约为 1.9237 秒和 6.6842 秒 | 通过 |
| `system_metrics.py` | 按默认参数实际采集 5 次，生成 5 行 CSV；8 个字段检查通过 | 通过 |
| `os_demo.py` | 在 Windows/Python 3.10 下实际运行，文本文件包含时间、工作目录、主目录、`os.name` 和系统环境 | 通过 |
| `subprocess_demo.py` | 作者已实际测试；本次在 Windows 下复核“未找到 vmstat”分支，正确生成说明文件；没有执行不安全命令 | 作者已测试；Windows 分支通过 |
| `metrics_exporter_demo.py` | 启动短时本机 HTTP 服务并请求 `/metrics`，返回 HTTP 200；7 个 `os_` 指标均有值 | 通过 |
| `server_resource_monitor.py` | 按默认参数完整运行 6 次、间隔 5 秒；生成 6 行 CSV，终端状态与 9 个字段检查通过 | 通过 |

说明：

- 当前机器的基础 Python 3.13 环境误装了与其不兼容的旧版 psutil 5.9.0，首次磁盘测试暴露二进制兼容错误。随后使用 Python 3.10.19 和 psutil 7.2.2 按项目要求重新测试，系统案例正常。这属于本机已有环境问题，重新按 `requirements.txt` 安装依赖即可避免。
- 电商静态请求测试曾出现一次瞬时 TLS 断开；重试后得到 HTTP 200，并完成了同页比较。
- Vue 官方在线编辑器会先从外部 CDN 加载编译依赖，再生成 `about:srcdoc` iframe。当前网络无法稳定访问该 CDN，因此不能声称已经完成排序、筛选和 14 行 CSV 的端到端测试。

## 4. 独立复核的环境局限与迁移建议

- `vue_grid_playwright.py`：迁移到新网络环境时，应确保能够稳定访问 `vuejs.org` 和 `cdn.jsdelivr.net`。完整四状态结果预期为 14 条记录。
- `subprocess_demo.py`：迁移到 Linux 环境时，应确认已经安装 `vmstat`。
- 5.2 的跨平台分支：本次实际运行环境为 Windows；Linux 磁盘根路径分支已做语法和静态检查，仍建议在 Linux 主机运行一次。
- `metrics_exporter_demo.py`：已完成短时接口测试，未进行数小时或数天的长期稳定性测试。
- 5.1 的目标网页属于外部站点，后续若调整 DOM、iframe 或分页按钮，需重新核对选择器。

## 5. 交付前清理

实际测试生成的 CSV、文本文件、Python 缓存和临时测试依赖不会放入最终 ZIP。两个 `outputs` 目录仅保留 `.gitkeep`，6.1 的两个虚构 CSV 教学模板正常保留。
