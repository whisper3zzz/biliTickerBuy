"""
Command-line login module for biliTickerBuy.
Allows users to login via QR code in terminal.
"""
import os
import time
import sys
from argparse import Namespace

import requests
from loguru import logger

from util import GLOBAL_COOKIE_PATH, set_main_request
from util.BiliRequest import BiliRequest
from util.CookieManager import parse_cookie_list


def generate_qrcode_terminal(url: str) -> None:
    """
    在终端中显示二维码
    使用字符画方式绘制，无需GUI
    """
    try:
        import qrcode
    except ImportError:
        print("❌ 需要安装 qrcode 库: pip install qrcode")
        return

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=1,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    # 使用Unicode字符绘制二维码
    # 在终端中用 █ 和空格来表示
    print("\n")
    for row in qr.modules:
        line = "  "
        for cell in row:
            if cell:
                line += "██"  # 黑色方块
            else:
                line += "  "  # 空白
        print(line)
    print("\n")


def generate_qrcode_ascii(url: str) -> None:
    """
    使用更兼容的ASCII字符画方式绘制二维码
    适用于不支持Unicode的终端
    """
    try:
        import qrcode
    except ImportError:
        print("Error: qrcode library not installed")
        return

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=1,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    # 打印简单的ASCII版本
    qr.print_ascii(invert=True)


def get_qrcode() -> tuple:
    """
    获取登录二维码
    返回 (url, qrcode_key)
    """
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    }
    
    max_retry = 10
    for _ in range(max_retry):
        try:
            res = requests.get(
                "https://passport.bilibili.com/x/passport-login/web/qrcode/generate",
                headers=headers,
                timeout=10,
            )
            res_json = res.json()
            if res_json["code"] == 0:
                return res_json["data"]["url"], res_json["data"]["qrcode_key"]
        except Exception as e:
            logger.debug(f"获取二维码失败: {e}")
        time.sleep(1)
    
    return None, None


def poll_qrcode_status(qrcode_key: str) -> tuple:
    """
    轮询二维码扫描状态
    返回 (status_msg, cookies)
    """
    headers = {"User-Agent": "Mozilla/5.0"}
    
    for _ in range(240):  # 最多等待120秒
        try:
            res = requests.get(
                "https://passport.bilibili.com/x/passport-login/web/qrcode/poll",
                params={"qrcode_key": qrcode_key},
                headers=headers,
                timeout=5,
            )
            poll_res = res.json()
            
            if poll_res.get("code") == 0:
                code = poll_res["data"]["code"]
                if code == 0:
                    # 登录成功
                    cookies = parse_cookie_list(res.headers.get("set-cookie", ""))
                    return "登录成功", cookies
                elif code == 86101:
                    # 等待扫码
                    pass
                elif code == 86090:
                    # 已扫码，等待确认
                    print("\r   📱 已扫码，请在手机上确认登录...", end="", flush=True)
                elif code == 86038:
                    return "二维码已过期，请重新获取", None
                else:
                    return f"扫码失败: {poll_res['data'].get('message', '未知错误')}", None
        except Exception as e:
            logger.debug(f"轮询状态失败: {e}")
        
        time.sleep(0.5)
    
    return "登录超时，请重试", None


def show_login_status():
    """显示当前登录状态"""
    from util import main_request
    
    try:
        name = main_request.get_request_name()
        if name:
            print(f"✅ 当前登录账号: {name}")
            print(f"   Cookies文件: {GLOBAL_COOKIE_PATH}")
            return True
        else:
            print("❌ 当前未登录")
            return False
    except Exception as e:
        print(f"❌ 检查登录状态失败: {e}")
        return False


def login_with_qrcode() -> bool:
    """
    通过扫描二维码登录
    返回是否登录成功
    """
    print("\n" + "="*60)
    print("  🔐 B站扫码登录")
    print("="*60)
    
    print("\n⏳ 正在生成登录二维码...")
    url, qrcode_key = get_qrcode()
    
    if not url or not qrcode_key:
        print("❌ 生成二维码失败，请检查网络连接")
        return False
    
    print("\n📱 请使用B站APP扫描下方二维码登录:")
    print("   (如果二维码显示异常，请尝试调整终端字体或窗口大小)")
    
    # 尝试显示二维码
    try:
        generate_qrcode_terminal(url)
    except Exception:
        try:
            generate_qrcode_ascii(url)
        except Exception:
            print(f"\n   二维码链接: {url}")
            print("   请复制此链接到浏览器或使用其他二维码工具生成")
    
    print("   ⏰ 二维码有效期约120秒")
    print("   🔄 正在等待扫码...", end="", flush=True)
    
    status_msg, cookies = poll_qrcode_status(qrcode_key)
    print()  # 换行
    
    if cookies:
        try:
            # 保存cookies
            request = BiliRequest(cookies_config_path=GLOBAL_COOKIE_PATH)
            request.cookieManager.db.insert("cookie", cookies)
            set_main_request(request)
            
            name = request.get_request_name()
            print(f"\n✅ {status_msg}")
            print(f"   欢迎, {name}!")
            print(f"   Cookies已保存到: {GLOBAL_COOKIE_PATH}")
            return True
        except Exception as e:
            print(f"\n❌ 保存登录信息失败: {e}")
            return False
    else:
        print(f"\n❌ {status_msg}")
        return False


def login_with_cookies_file(filepath: str) -> bool:
    """
    通过cookies文件登录
    """
    if not os.path.exists(filepath):
        print(f"❌ 文件不存在: {filepath}")
        return False
    
    try:
        set_main_request(BiliRequest(cookies_config_path=filepath))
        from util import main_request
        name = main_request.get_request_name()
        if name:
            print(f"✅ 登录成功: {name}")
            return True
        else:
            print("❌ Cookies无效或已过期")
            return False
    except Exception as e:
        print(f"❌ 登录失败: {e}")
        return False


def logout():
    """注销当前账号"""
    from util import main_request
    try:
        main_request.cookieManager.db.delete("cookie")
        print("✅ 已注销登录")
        return True
    except Exception as e:
        print(f"❌ 注销失败: {e}")
        return False


def login_cmd(args: Namespace):
    """登录命令入口"""
    
    print("\n" + "="*60)
    print("  🎫 B站会员购登录")
    print("="*60)
    
    # 检查参数
    if hasattr(args, 'cookies') and args.cookies:
        # 使用cookies文件登录
        login_with_cookies_file(args.cookies)
        return
    
    if hasattr(args, 'status') and args.status:
        # 只显示状态
        show_login_status()
        return
    
    if hasattr(args, 'logout') and args.logout:
        # 注销
        logout()
        return
    
    # 显示当前状态
    print("\n📋 当前登录状态:")
    is_logged_in = show_login_status()
    
    if is_logged_in:
        print("\n是否要切换账号?")
        choice = input("   输入 'y' 重新登录，其他键退出: ").strip().lower()
        if choice != 'y':
            return
        logout()
    
    # 扫码登录
    login_with_qrcode()
