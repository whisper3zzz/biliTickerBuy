"""
Command-line ticket information query module for biliTickerBuy.
Allows users to query ticket information via terminal.
"""
import json
from argparse import Namespace
from datetime import datetime
from typing import Optional
from urllib.parse import urlparse, parse_qs

from loguru import logger

from util import main_request

# 销售状态映射
SALES_FLAG_MAP = {
    1: "不可售",
    2: "预售",
    3: "停售",
    4: "售罄",
    5: "不可用",
    6: "库存紧张",
    8: "暂时售罄",
    9: "不在白名单",
    101: "未开始",
    102: "已结束",
    103: "未完成",
    105: "下架",
    106: "已取消",
}


def extract_id_from_url(url: str) -> Optional[str]:
    """从URL中提取票务ID"""
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    return query_params.get("id", [None])[0]


def format_timestamp(ts: int) -> str:
    """格式化时间戳"""
    try:
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return "未知"


def info_cmd(args: Namespace):
    """查询票务信息命令"""
    url = args.url
    
    print("\n" + "="*70)
    print("  🎫 B站会员购票务信息查询")
    print("="*70)
    
    # 提取ID
    if "http" in url:
        ticket_id = extract_id_from_url(url)
        if not ticket_id:
            print("❌ 无法从URL中提取票务ID")
            return
    else:
        ticket_id = url

    print(f"\n⏳ 正在查询票务ID: {ticket_id}")
    
    try:
        res = main_request.get(
            url=f"https://show.bilibili.com/api/ticket/project/getV2?version=134&id={ticket_id}&project_id={ticket_id}"
        )
        ret = res.json()

        if ret.get("errno", ret.get("code")) == 100001:
            print("❌ 输入无效，请输入一个有效的票务ID或网址")
            return
        elif ret.get("errno", ret.get("code")) != 0:
            print(f"❌ {ret.get('msg', ret.get('message', '未知错误'))}")
            return

        data = ret["data"]
        
        # 基本信息
        print("\n" + "-"*70)
        print("  📌 基本信息")
        print("-"*70)
        print(f"  项目名称: {data['name']}")
        print(f"  项目ID:   {data['id']}")
        print(f"  热门项目: {'是 🔥' if data.get('hotProject') else '否'}")
        
        # 时间信息
        start_time = format_timestamp(data.get("start_time", 0))
        end_time = format_timestamp(data.get("end_time", 0))
        print(f"  开始时间: {start_time}")
        print(f"  结束时间: {end_time}")
        
        # 场馆信息
        venue_info = data.get("venue_info", {})
        if venue_info:
            print(f"\n  📍 场馆: {venue_info.get('name', '未知')}")
            print(f"     地址: {venue_info.get('address_detail', '未知')}")

        # 票种信息
        print("\n" + "-"*70)
        print("  🎟️  票种列表")
        print("-"*70)
        
        ticket_count = 0
        for screen in data.get("screen_list", []):
            if "name" not in screen:
                continue
            screen_name = screen["name"]
            
            print(f"\n  【{screen_name}】")
            
            express_fee = 0
            if data.get("has_eticket"):
                express_fee = 0
            else:
                if screen.get("express_fee", 0) >= 0:
                    express_fee = screen.get("express_fee", 0)

            for ticket in screen.get("ticket_list", []):
                ticket_count += 1
                ticket_desc = ticket.get("desc", "未知")
                ticket_price = (ticket.get("price", 0) + express_fee) / 100
                sale_start = ticket.get("sale_start", "未知")
                sale_status = SALES_FLAG_MAP.get(ticket.get("sale_flag_number", 0), "未知")
                clickable = "✅ 可购买" if ticket.get("clickable") else "❌ 不可购买"
                
                print(f"    ├─ {ticket_desc}")
                print(f"    │  价格: ¥{ticket_price:.2f}  状态: {sale_status}  {clickable}")
                print(f"    │  起售时间: {sale_start}")

        if ticket_count == 0:
            print("  (暂无票种信息)")
        
        # 可选日期
        sales_dates = data.get("sales_dates", [])
        if sales_dates:
            print("\n" + "-"*70)
            print("  📅 可选日期")
            print("-"*70)
            dates = [t.get("date", "未知") for t in sales_dates]
            print(f"  {', '.join(dates[:10])}")
            if len(dates) > 10:
                print(f"  ... 共 {len(dates)} 个日期")

        print("\n" + "="*70)
        print(f"  ✅ 共找到 {ticket_count} 个票种")
        print("="*70)
        
        # 提示下一步操作
        print("\n💡 下一步操作:")
        print("   1. 运行 'btb login' 登录账号")
        print("   2. 运行 'btb config' 生成抢票配置")
        print("   3. 运行 'btb buy <配置文件>' 开始抢票")

    except Exception as e:
        logger.exception(e)
        print(f"\n❌ 查询失败: {e}")
