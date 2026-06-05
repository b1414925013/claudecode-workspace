"""
夸克网盘自动签到脚本
通过 GitHub Actions 每日自动执行，实现夸克网盘的自动签到，并支持企业微信机器人推送
"""
import json
import math
import os
import re
import sys
import time
from typing import List, Dict, Tuple, Optional

import requests


# ============ 配置 ============
TIMEOUT = 10  # 请求超时时间（秒）
MAX_RETRIES = 3  # 最大重试次数


# ============ 工具函数 ============
def get_env() -> Tuple[List[str], Optional[str]]:
    """
    获取环境变量
    :return: (cookie列表, webhook地址)
    """
    webhook = os.environ.get('WebHook') or os.environ.get('WEBHOOK')

    if "COOKIE_QUARK" not in os.environ:
        error_msg = "❌ 未添加COOKIE_QUARK变量"
        print(error_msg)
        if webhook:
            send_text(webhook, error_msg)
        sys.exit(0)

    cookie_str = os.environ.get('COOKIE_QUARK', '')
    cookie_list = re.split(r'\n|&&', cookie_str)
    # 过滤空字符串
    cookie_list = [c.strip() for c in cookie_list if c.strip()]

    return cookie_list, webhook


def send_text(webhook: str, content: str, mentioned_list: Optional[List[str]] = None,
              mentioned_mobile_list: Optional[List[str]] = None) -> Optional[str]:
    """
    企业微信机器人推送
    :param webhook: WebHook地址
    :param content: 推送内容
    :param mentioned_list: @用户列表
    :param mentioned_mobile_list: @手机号列表
    """
    if not webhook:
        return None

    header = {"Content-Type": "application/json", "Charset": "UTF-8"}
    data = {
        "msgtype": "text",
        "text": {
            "content": content,
            "mentioned_list": mentioned_list or [],
            "mentioned_mobile_list": mentioned_mobile_list or []
        }
    }
    try:
        resp = requests.post(url=webhook, json=data, headers=header, timeout=10)
        return resp.content.decode('utf-8')
    except Exception as e:
        print(f"推送失败: {e}")
        return None


def retry_request(func, *args, retries=MAX_RETRIES, **kwargs):
    """
    带重试的请求封装
    :param func: 请求函数
    :param retries: 重试次数
    """
    for i in range(retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if i < retries - 1:
                time.sleep(1)
                continue
            raise e


# ============ 签到核心类 ============
class Quark:
    """夸克网盘签到类"""

    def __init__(self, user_data: Dict[str, str]):
        self.param = user_data
        self.querystring = {
            "pr": "ucpro",
            "fr": "android",
            "kps": self.param.get('kps'),
            "sign": self.param.get('sign'),
            "vcode": self.param.get('vcode')
        }

    @staticmethod
    def convert_bytes(b: int) -> str:
        """将字节转换为 MB/GB/TB 等人类可读格式"""
        if b <= 0:
            return "0 B"
        units = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        unit_index = min(int(math.log(b, 1024)), len(units) - 1)
        converted_value = b / (1024 ** unit_index)
        return f"{converted_value:.2f} {units[unit_index]}"

    def get_growth_info(self) -> Optional[Dict]:
        """获取用户当前的签到信息"""
        url = "https://drive-m.quark.cn/1/clouddrive/capacity/growth/info"
        try:
            resp = requests.get(url=url, params=self.querystring, timeout=TIMEOUT)
            data = resp.json()
            return data.get("data")
        except Exception as e:
            print(f"获取签到信息失败: {e}")
            return None

    def get_growth_sign(self) -> Tuple[bool, any]:
        """执行签到"""
        url = "https://drive-m.quark.cn/1/clouddrive/capacity/growth/sign"
        data = {"sign_cyclic": True}
        try:
            resp = requests.post(url=url, json=data, params=self.querystring, timeout=TIMEOUT)
            result = resp.json()
            if result.get("data"):
                return True, result["data"]["sign_daily_reward"]
            return False, result.get("message", "签到失败")
        except Exception as e:
            print(f"签到请求失败: {e}")
            return False, str(e)

    def query_balance(self) -> Optional[int]:
        """查询抽奖余额"""
        url = "https://coral2.quark.cn/currency/v1/queryBalance"
        querystring = {
            "moduleCode": "1f3563d38896438db994f118d4ff53cb",
            "kps": self.param.get('kps'),
        }
        try:
            resp = requests.get(url=url, params=querystring, timeout=TIMEOUT)
            data = resp.json()
            if data.get("data"):
                return data["data"]["balance"]
            return None
        except Exception:
            return None

    def do_sign(self) -> str:
        """执行签到任务并返回日志"""
        growth_info = self.get_growth_info()
        if not growth_info:
            return "❌ 签到异常: 获取成长信息失败\n"

        log = (
            f" {'88VIP' if growth_info.get('88VIP') else '普通用户'} {self.param.get('user', '未知')}\n"
            f"💾 网盘总容量: {self.convert_bytes(growth_info.get('total_capacity', 0))}\n"
            f"签到总容量: "
        )

        cap_composition = growth_info.get('cap_composition', {})
        if "sign_reward" in cap_composition:
            log += f"{self.convert_bytes(cap_composition['sign_reward'])}\n"
        else:
            log += "0 MB\n"

        cap_sign = growth_info.get("cap_sign", {})
        if cap_sign.get("sign_daily"):
            log += (
                f"✅ 今日已签到 +{self.convert_bytes(cap_sign.get('sign_daily_reward', 0))}\n"
                f"连签进度({cap_sign.get('sign_progress', 0)}/{cap_sign.get('sign_target', 0)})\n"
            )
        else:
            success, sign_result = self.get_growth_sign()
            if success:
                new_progress = cap_sign.get('sign_progress', 0) + 1
                target = cap_sign.get('sign_target', 0)
                log += (
                    f"✅ 执行签到 +{self.convert_bytes(sign_result)}，"
                    f"连签进度({new_progress}/{target})\n"
                )
            else:
                log += f"❌ 签到异常: {sign_result}\n"

        return log


# ============ 主函数 ============
def parse_user_data(cookie_str: str) -> Dict[str, str]:
    """解析用户数据字符串"""
    user_data = {}
    for item in cookie_str.replace(' ', '').split(';'):
        if '=' in item:
            k, v = item.split('=', 1)
            user_data[k] = v
    return user_data


def main() -> str:
    """主函数"""
    cookie_list, webhook = get_env()

    if not cookie_list:
        print("❌ 未检测到有效账号")
        return ""

    print(f"✅ 检测到共 {len(cookie_list)} 个夸克账号\n")
    msg = ""

    for i, cookie in enumerate(cookie_list):
        user_data = parse_user_data(cookie)
        if not user_data.get('kps') or not user_data.get('sign') or not user_data.get('vcode'):
            msg += f"❌ 第{i + 1}个账号参数不完整，已跳过\n"
            print(f"❌ 第{i + 1}个账号参数不完整，已跳过")
            continue

        print(f"正在处理第{i + 1}个账号: {user_data.get('user', '未知')}")
        msg += f"🙍🏻 第{i + 1}个账号 "
        msg += Quark(user_data).do_sign()

    # 统一推送
    if webhook and msg:
        send_text(webhook, "夸克网盘签到报告\n\n" + msg)

    return msg


if __name__ == "__main__":
    print("----------夸克网盘开始签到----------")
    result = main()
    if result:
        print("\n" + result)
    print("----------夸克网盘签到完毕----------")
