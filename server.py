"""CSQAQ（CS:GO 饰品行情）MCP Server

提供 CS:GO 饰品实时行情查询能力（BUFF / 悠悠有品 / Steam / C5 / IGXE / ECO 多平台）：
- search_items:   按关键词搜索饰品（中英文均可）
- get_good:       查询饰品多平台价格 / 在售 / 涨跌 / 存世量详情
- get_chart:      查询价格 / 成交量图表数据
- get_hot_series: 热门饰品系列列表
"""

import os
import threading
import time
from pathlib import Path
from typing import Any, Dict, List

import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("CSQAQ MCP Server")

BASE_URL = "https://api.csqaq.com/api/v1"
RATE_LIMIT_MS = 1000  # CSQAQ 限频：单 IP 1 次/秒


# ---------------- 配置读取 ----------------

def _load_env_file(path: Path) -> Dict[str, str]:
    """极简 .env 解析（只读 KEY=VALUE，忽略注释 / 空行）。"""
    result: Dict[str, str] = {}
    if not path.exists():
        return result
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        result[key.strip()] = value.strip().strip('"').strip("'")
    return result


def _get_api_token() -> str:
    token = os.environ.get("CSQAQ_API_TOKEN", "")
    if token:
        return token
    # 回退：读取本目录 .env，或 cs-price-predictor 项目的 .env
    candidates = [
        Path(__file__).resolve().parent / ".env",
        Path(__file__).resolve().parent.parent / "cs-price-predictor-main" / ".env",
    ]
    for path in candidates:
        env = _load_env_file(path)
        if env.get("CSQAQ_API_TOKEN"):
            return env["CSQAQ_API_TOKEN"]
    return ""


API_TOKEN = _get_api_token()
if not API_TOKEN:
    raise RuntimeError(
        "缺少 CSQAQ_API_TOKEN：请设置环境变量 CSQAQ_API_TOKEN，"
        "或确保 cs-price-predictor-main/.env 中有 CSQAQ_API_TOKEN=..."
    )


# ---------------- CSQAQ 客户端（限频 + 锁） ----------------

_lock = threading.Lock()
_last_call_ts = 0.0


def _rate_limit() -> None:
    global _last_call_ts
    with _lock:
        now = time.time() * 1000
        wait_ms = RATE_LIMIT_MS - (now - _last_call_ts)
        if wait_ms > 0:
            time.sleep(wait_ms / 1000)
        _last_call_ts = time.time() * 1000


def _request(method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
    _rate_limit()
    resp = requests.request(
        method,
        f"{BASE_URL}{endpoint}",
        headers={"ApiToken": API_TOKEN, "Content-Type": "application/json"},
        timeout=15,
        **kwargs,
    )
    resp.raise_for_status()
    payload = resp.json()
    if payload.get("code") != 200:
        raise RuntimeError(f"CSQAQ 返回错误: {payload.get('msg', payload)}")
    return payload


# ---------------- MCP Tools ----------------

@mcp.tool()
def search_items(query: str) -> List[Dict[str, Any]]:
    """
    按关键词搜索 CS:GO 饰品（支持中英文，如 "AK" / "红线" / "沙鹰"）。

    Args:
        query: 搜索关键词

    Returns:
        饰品候选列表 [{id, name}]，把 id 传给 get_good 查询详情
    """
    payload = _request("get", "/search/suggest", params={"text": query})
    return [
        {"id": item.get("id"), "name": item.get("value")}
        for item in (payload.get("data") or [])
    ]


@mcp.tool()
def get_good(item_id: int) -> Dict[str, Any]:
    """
    查询单个饰品的多平台行情快照（BUFF / 悠悠 / Steam / C5 / IGXE / ECO）。

    Args:
        item_id: 饰品 ID（来自 search_items）

    Returns:
        完整行情数据：7 平台价格、在售数、1/7/30/180 日涨跌、存世量、手续费估算等
    """
    payload = _request("get", "/info/good", params={"id": int(item_id)})
    return payload.get("data") or {}


@mcp.tool()
def get_chart(item_id: int, key: str, platform: int = 1, period: int = 30) -> Dict[str, Any]:
    """
    查询饰品价格 / 成交量图表数据。

    Args:
        item_id: 饰品 ID
        key: 图表键（如 price / sell_num 等，见 get_good 返回结构）
        platform: 平台，1=BUFF 2=悠悠 3=Steam，默认 1
        period: 周期天数，默认 30

    Returns:
        图表序列数据
    """
    payload = _request(
        "post",
        "/info/chart",
        json={
            "good_id": int(item_id),
            "key": key,
            "platform": platform,
            "period": period,
            "style": "all_style",
        },
    )
    return payload.get("data") or {}


@mcp.tool()
def get_hot_series(page: int = 1, page_size: int = 10) -> List[Dict[str, Any]]:
    """
    获取 CS:GO 热门饰品系列列表。

    Args:
        page: 页码，默认 1
        page_size: 每页数量，默认 10

    Returns:
        热门系列列表
    """
    payload = _request(
        "post", "/info/get_series_list", json={"page": page, "page_size": page_size}
    )
    return payload.get("data") or []


if __name__ == "__main__":
    mcp.run(transport="stdio")
