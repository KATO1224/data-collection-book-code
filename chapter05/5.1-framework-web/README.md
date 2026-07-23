# 5.1 框架网页数据采集

本目录对应教材第 5.1 节，保留书稿中的案例目标与字段，整理了浏览器渲染、接口请求重放、前端状态识别、电商动态分页和静态/动态效率比较五个程序。

## 环境准备

在项目根目录执行：

```bash
python -m pip install -r requirements.txt
playwright install chromium
```

除 `quotes_api_requests.py` 外，其余浏览器案例都需要 Chromium 组件。所有案例都需要外网连接，目标教学站点结构若有更新，CSS 选择器也可能需要相应调整。

## 案例说明

### `quotes_playwright.py`

- 对应小节：5.1.3.1 基于浏览器渲染的采集——以 Playwright 为例
- 目标网页：`https://quotes.toscrape.com/js/`
- 案例目标：等待 JavaScript 渲染名言节点，提取 `page`、`text`、`author`、`tags`，自动点击下一页，默认采集前 5 页
- 运行命令：

```bash
python chapter05/5.1-framework-web/quotes_playwright.py
```

- 输出文件：`outputs/quotes_playwright.csv`

### `quotes_api_requests.py`

- 对应小节：5.1.3.2 基于接口监听与请求重放的采集
- 目标接口：`https://quotes.toscrape.com/api/quotes`
- 案例目标：使用 Requests 按页读取 JSON，保存 `page`、`text`、`author`、`tags`，依据 `has_next` 停止，默认最多 5 页
- 运行命令：

```bash
python chapter05/5.1-framework-web/quotes_api_requests.py
```

- 输出文件：`outputs/quotes_api_requests.csv`

### `vue_grid_playwright.py`

- 对应小节：5.1.3.3 基于前端框架渲染状态的数据识别
- 目标网页：`https://vuejs.org/examples/#grid`
- 案例目标：进入 iframe 预览区域，依次提取初始状态、按 Name 排序、输入 `0` 后筛选、筛选状态下按 Power 排序的结果
- 输出字段：`state`、`name`、`power`
- 运行命令：

```bash
python chapter05/5.1-framework-web/vue_grid_playwright.py
```

- 输出文件：`outputs/vue_grid_state_results.csv`
- 预期记录数：4 + 4 + 3 + 3，共 14 条状态记录

### `ecommerce_playwright.py`

- 对应小节：5.1.5.1 电商动态网页数据采集案例
- 目标网页：`https://webscraper.io/test-sites/e-commerce/ajax/computers/laptops`
- 案例目标：提取商品名称、价格、描述、评价数量和详情链接，自动完成 AJAX 动态分页，默认采集前 3 页
- 输出字段：`page`、`title`、`price`、`description`、`reviews`、`product_url`
- 运行命令：

```bash
python chapter05/5.1-framework-web/ecommerce_playwright.py
```

- 输出文件：`outputs/ecommerce_playwright.csv`

程序点击下一页后会等待首条商品名称发生变化，不使用固定 `time.sleep()` 判断页面是否更新。代码同时兼容训练站点曾使用的 `.thumbnail` 和 `.product-wrapper` 商品容器类名。

### `compare_static_playwright.py`

- 对应小节：5.1.5.2 静态爬取与框架渲染采集的效率比较
- 目标网页：与电商动态分页案例相同
- 案例目标：分别使用 Requests + BeautifulSoup 和 Playwright 读取同一 URL 首次打开后显示的首批商品，比较运行时间与记录数量
- 运行命令：

```bash
python chapter05/5.1-framework-web/compare_static_playwright.py
```

- 输出：仅在终端显示比较结果，不生成数据文件

## 网络连接与错误处理

所有 HTTP 请求均设置了超时。网络断开、TLS 连接失败或网站返回错误状态时，程序会在终端给出提示。Playwright 程序使用明确的元素可见、记录数或内容变化等待条件；若等待超时，应先在浏览器中直接访问目标网址，再用开发者工具核对页面结构。

教学站点可能调整 HTML、按钮角色或 iframe 结构。若页面能够打开但采集结果为空，重点检查 `.quote`、`iframe`、`tbody tr`、`.thumbnail`、`.product-wrapper`、`a.title` 和分页按钮等定位条件。

## Spyder 与 Jupyter 注意事项

这些示例使用 Playwright 同步 API。Spyder、Jupyter Notebook 等交互环境可能已经运行异步事件循环，直接执行同步 API 时可能报错。推荐把程序保存为 `.py` 文件后从系统终端运行。若必须在异步环境执行，应改用 `playwright.async_api`，并使用 `await` 调用相应方法。

## 合规提示

本目录只面向公开教学站点和小规模课堂实验。请遵守目标网站的使用规则与访问频率限制，不要把示例改造成绕过登录、验证码、权限控制或技术保护措施的工具。
