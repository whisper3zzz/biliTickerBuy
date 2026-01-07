"""
Command-line configuration generator for biliTickerBuy.
Allows users to generate ticket purchase configurations via terminal.
"""
import json
import os
import re
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse, parse_qs

from loguru import logger

from util import TEMP_PATH, GLOBAL_COOKIE_PATH, main_request, set_main_request, ConfigDB
from util.BiliRequest import BiliRequest

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


def filename_filter(filename: str) -> str:
    """过滤文件名中的非法字符"""
    return re.sub('[/:*?"<>|]', "", filename)


def extract_id_from_url(url: str) -> Optional[str]:
    """从URL中提取票务ID"""
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    return query_params.get("id", [None])[0]


def print_menu(title: str, options: List[str], allow_multiple: bool = False) -> None:
    """打印菜单选项"""
    print(f"\n{'='*50}")
    print(f"  {title}")
    print('='*50)
    for i, option in enumerate(options, 1):
        print(f"  [{i}] {option}")
    if allow_multiple:
        print("\n  提示: 可以输入多个数字，用空格或逗号分隔")
    print('='*50)


def get_single_choice(prompt: str, max_val: int) -> int:
    """获取单选输入"""
    while True:
        try:
            choice = input(f"{prompt} (1-{max_val}): ").strip()
            val = int(choice)
            if 1 <= val <= max_val:
                return val - 1  # 返回0-based索引
            print(f"  ❌ 请输入 1 到 {max_val} 之间的数字")
        except ValueError:
            print("  ❌ 请输入有效的数字")


def get_multiple_choice(prompt: str, max_val: int) -> List[int]:
    """获取多选输入"""
    while True:
        try:
            choice = input(f"{prompt} (1-{max_val}): ").strip()
            # 支持空格或逗号分隔
            parts = re.split(r'[,\s]+', choice)
            indices = []
            for p in parts:
                if p:
                    val = int(p)
                    if 1 <= val <= max_val:
                        indices.append(val - 1)
                    else:
                        raise ValueError(f"数字 {val} 超出范围")
            if indices:
                return indices
            print("  ❌ 至少选择一个选项")
        except ValueError as e:
            print(f"  ❌ 输入错误: {e}")


def fetch_ticket_info(url_or_id: str, request: BiliRequest) -> Dict[str, Any]:
    """获取票务信息"""
    # 提取ID
    if "http" in url_or_id:
        ticket_id = extract_id_from_url(url_or_id)
        if not ticket_id:
            raise ValueError("无法从URL中提取票务ID")
    else:
        ticket_id = url_or_id

    # 请求票务信息
    res = request.get(
        url=f"https://show.bilibili.com/api/ticket/project/getV2?version=134&id={ticket_id}&project_id={ticket_id}"
    )
    ret = res.json()

    if ret.get("errno", ret.get("code")) == 100001:
        raise ValueError("输入无效，请输入一个有效的票务ID或网址")
    elif ret.get("errno", ret.get("code")) != 0:
        raise ValueError(ret.get("msg", ret.get("message", "未知错误")))

    return ret["data"]


def fetch_buyers(request: BiliRequest, project_id: int) -> List[Dict]:
    """获取购票人列表"""
    res = request.get(
        url=f"https://show.bilibili.com/api/ticket/buyer/list?is_default&projectId={project_id}"
    )
    return res.json()["data"]["list"]


def fetch_addresses(request: BiliRequest) -> List[Dict]:
    """获取收货地址列表"""
    res = request.get(url="https://show.bilibili.com/api/ticket/addr/list")
    return res.json()["data"]["addr_list"]


def config_cmd_interactive():
    """交互式配置生成"""
    from util import main_request
    
    print("\n" + "="*60)
    print("  🎫 B站会员购抢票配置生成器 (命令行版)")
    print("="*60)

    # 检查登录状态
    try:
        username = main_request.get_request_name()
        if not username:
            print("\n⚠️  当前未登录，请先运行 'btb login' 登录")
            return
        print(f"\n✅ 当前登录账号: {username}")
    except Exception as e:
        print(f"\n❌ 登录状态检查失败: {e}")
        print("   请先运行 'btb login' 登录")
        return

    # 输入票务URL
    print("\n📝 请输入票务网址")
    print("   例如: https://show.bilibili.com/platform/detail.html?id=84096")
    url = input("   网址: ").strip()
    
    if not url:
        print("❌ 网址不能为空")
        return

    try:
        print("\n⏳ 正在获取票务信息...")
        data = fetch_ticket_info(url, main_request)
        project_id = data["id"]
        project_name = data["name"]
        is_hot_project = data["hotProject"]
        
        print(f"\n✅ 获取成功!")
        print(f"   项目名称: {project_name}")
        print(f"   热门项目: {'是' if is_hot_project else '否'}")

        # 解析票种信息
        ticket_list = []
        ticket_str_list = []
        
        for screen in data["screen_list"]:
            if "name" not in screen:
                continue
            screen_name = screen["name"]
            screen_id = screen["id"]
            screen_project_id = screen.get("project_id", project_id)
            
            express_fee = 0
            if data.get("has_eticket"):
                express_fee = 0
            else:
                if screen.get("express_fee", 0) >= 0:
                    express_fee = screen.get("express_fee", 0)

            for ticket in screen["ticket_list"]:
                ticket_desc = ticket["desc"]
                sale_start = ticket.get("sale_start", "未知")
                ticket_price = ticket["price"] + express_fee
                ticket["price"] = ticket_price
                ticket["screen"] = screen_name
                ticket["screen_id"] = screen_id
                ticket["is_hot_project"] = is_hot_project
                
                sale_status = SALES_FLAG_MAP.get(ticket.get("sale_flag_number", 0), "未知")
                ticket_str = f"{screen_name} - {ticket_desc} - ¥{ticket_price / 100:.2f} - {sale_status} - 【起售: {sale_start}】"
                ticket_str_list.append(ticket_str)
                ticket_list.append({
                    "project_id": screen_project_id,
                    "ticket": ticket
                })

        if not ticket_list:
            print("❌ 未找到可用的票种信息")
            return

        # 选择票种
        print_menu("选择票种", ticket_str_list)
        ticket_idx = get_single_choice("请选择票种", len(ticket_str_list))
        selected_ticket = ticket_list[ticket_idx]

        # 获取购票人列表
        print("\n⏳ 正在获取购票人列表...")
        buyers = fetch_buyers(main_request, project_id)
        if not buyers:
            print("❌ 没有找到购票人信息")
            print("   请在B站APP「会员购」-「个人中心」-「购票人信息」中添加")
            return

        buyer_str_list = [f"{b['name']} - {b['personal_id']}" for b in buyers]
        print_menu("选择购票人 (可多选)", buyer_str_list, allow_multiple=True)
        buyer_indices = get_multiple_choice("请选择购票人", len(buyer_str_list))
        selected_buyers = [buyers[i] for i in buyer_indices]
        print(f"   ✅ 已选择 {len(selected_buyers)} 位购票人")

        # 获取收货地址
        print("\n⏳ 正在获取收货地址...")
        addresses = fetch_addresses(main_request)
        if not addresses:
            print("❌ 没有找到收货地址")
            print("   请在B站APP「会员购」-「地址管理」中添加")
            return

        addr_str_list = [f"{a['name']} - {a['phone']} - {a['addr']}" for a in addresses]
        print_menu("选择收货地址", addr_str_list)
        addr_idx = get_single_choice("请选择收货地址", len(addr_str_list))
        selected_addr = addresses[addr_idx]

        # 输入联系人信息
        print("\n📝 联系人信息")
        default_name = ConfigDB.get("people_buyer_name") or ""
        default_phone = ConfigDB.get("people_buyer_phone") or ""
        
        buyer_name = input(f"   联系人姓名 [{default_name}]: ").strip() or default_name
        buyer_phone = input(f"   联系人电话 [{default_phone}]: ").strip() or default_phone

        if not buyer_name or not buyer_phone:
            print("❌ 联系人姓名和电话不能为空")
            return

        # 保存联系人信息
        ConfigDB.insert("people_buyer_name", buyer_name)
        ConfigDB.insert("people_buyer_phone", buyer_phone)

        # 生成配置
        username = main_request.get_request_name()
        detail = f"{username}-{project_name}-{ticket_str_list[ticket_idx]}"
        for p in selected_buyers:
            detail += f"-{p['name']}"

        config = {
            "username": username,
            "detail": detail,
            "count": len(selected_buyers),
            "screen_id": selected_ticket["ticket"]["screen_id"],
            "project_id": selected_ticket["project_id"],
            "is_hot_project": selected_ticket["ticket"]["is_hot_project"],
            "sku_id": selected_ticket["ticket"]["id"],
            "order_type": 1,
            "pay_money": selected_ticket["ticket"]["price"] * len(selected_buyers),
            "buyer_info": selected_buyers,
            "buyer": buyer_name,
            "tel": buyer_phone,
            "deliver_info": {
                "name": selected_addr["name"],
                "tel": selected_addr["phone"],
                "addr_id": selected_addr["id"],
                "addr": (
                    selected_addr.get("prov", "") +
                    selected_addr.get("city", "") +
                    selected_addr.get("area", "") +
                    selected_addr.get("addr", "")
                ),
            },
            "cookies": main_request.cookieManager.get_cookies(),
            "phone": main_request.cookieManager.get_config_value("phone", ""),
        }

        # 保存配置文件
        filename = filename_filter(detail) + ".json"
        filepath = os.path.join(TEMP_PATH, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=4)

        print("\n" + "="*60)
        print("  ✅ 配置生成成功!")
        print("="*60)
        print(f"   📄 配置文件: {filepath}")
        print(f"   👤 购票人数: {len(selected_buyers)}")
        print(f"   💰 总金额: ¥{config['pay_money'] / 100:.2f}")
        print("\n   使用以下命令开始抢票:")
        print(f'   btb buy "{filepath}"')
        print("="*60)

        return filepath

    except Exception as e:
        logger.exception(e)
        print(f"\n❌ 错误: {e}")
        return None


def config_cmd(args):
    """配置命令入口"""
    from argparse import Namespace
    
    if hasattr(args, 'cookies_file') and args.cookies_file:
        # 使用指定的cookies文件
        try:
            set_main_request(BiliRequest(cookies_config_path=args.cookies_file))
        except Exception as e:
            print(f"❌ 加载cookies文件失败: {e}")
            return
    
    config_cmd_interactive()
