# CSQAQ MCP Server

CS:GO 饰品行情 MCP server——把 [CSQAQ API](https://api.csqaq.com) 封装成 MCP 工具，供 AI 助手直接查询 BUFF / 悠悠有品 / Steam / C5 / IGXE / ECO 七平台实时价格、在售、涨跌、存世量。

> 模板参考：`bilibili-mcp-server`（mimo 智能体 2026-08-02 安装）。2026-08-03 由用户与 QA Agent 一起开发，作为 AI 学习里程碑「自己写第一个 MCP server」。

## 提供的工具

| 工具 | 说明 |
|---|---|
| `search_items(query)` | 按关键词搜索饰品（中英文均可），返回 `[{id, name}]` |
| `get_good(item_id)` | 单个饰品完整行情快照：7 平台价格 / 在售 / 1/7/30/180 日涨跌 / 存世量 / 手续费估算 |
| `get_chart(item_id, key, platform, period)` | 价格 / 成交量图表数据 |
| `get_hot_series(page, page_size)` | 热门饰品系列列表 |

## 配置

CSQAQ API Token（环境变量 `CSQAQ_API_TOKEN`，或本目录/`cs-price-predictor-main/.env` 中的同名配置）。

Token 需与当前网络 IP 绑定（`POST /api/v1/sys/bind_local_ip`），换网络后需重新绑定。

## 运行

```bash
python -m venv .venv
.venv\Scripts\pip install -e .
# 调试（MCP Inspector）
npx @modelcontextprotocol/inspector .venv\Scripts\python.exe server.py
# 或注册进 QwenPaw：stdio 命令 = .venv\Scripts\python.exe server.py，cwd = 本目录
```

限频：CSQAQ 单 IP 1 次/秒，server 内置 1s 限流。
