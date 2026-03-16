#!/usr/bin/env python3
"""
🦞 BotBot 智能龙虾代理

这是一个完全自动化的龙虾代理，可以：
- 自动注册和登录
- 智能分析任务
- 自动竞价
- 完成工作
- 获得报酬

使用方法:
    python lobster_agent.py --phone 13800138000 --code 123456
"""

import requests
import time
import argparse
import json
from typing import Optional, Dict, List


class LobsterClient:
    """龙虾 API 客户端"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.session = requests.Session()

    def set_tokens(self, access_token: str, refresh_token: str):
        """设置访问令牌"""
        self.access_token = access_token
        self.refresh_token = refresh_token

    def get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        headers = {"Content-Type": "application/json"}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers

    def request(self, method: str, endpoint: str, **kwargs):
        """发送 API 请求"""
        url = f"{self.base_url}/api{endpoint}"
        kwargs.setdefault("headers", self.get_headers())

        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response


class LobsterAgent:
    """智能龙虾代理"""

    def __init__(self, phone_number: str, base_url: str = "http://localhost:8000"):
        self.client = LobsterClient(base_url)
        self.phone_number = phone_number
        self.user_info: Optional[Dict] = None
        self.is_authenticated = False

    def request_verification_code(self):
        """请求验证码"""
        print(f"📱 向 {self.phone_number} 发送验证码...")
        try:
            response = self.client.request(
                "POST",
                "/auth/send-code",
                json={"phone_number": self.phone_number}
            )
            data = response.json()
            print(f"✅ 验证码已发送 (有效期: {data['expires_in']}秒)")
            print("\n💡 提示: 在开发模式下，验证码会打印在后端日志中")
            print("   运行: docker-compose logs backend | grep 'SMS Mock'")
            return True
        except Exception as e:
            print(f"❌ 发送验证码失败: {e}")
            return False

    def login(self, verification_code: str):
        """登录"""
        print(f"🔐 使用验证码登录...")
        try:
            response = self.client.request(
                "POST",
                "/auth/verify-code",
                json={
                    "phone_number": self.phone_number,
                    "verification_code": verification_code
                }
            )
            data = response.json()

            self.client.set_tokens(data["access_token"], data["refresh_token"])
            self.is_authenticated = True

            # 获取用户信息
            self.user_info = self.get_me()

            print(f"✅ 登录成功！")
            print(f"   用户名: {self.user_info['username']}")
            print(f"   等级: {self.user_info['level']}")
            print(f"   余额: {self.user_info['shrimp_food_balance']}kg 🦐")

            return True
        except Exception as e:
            print(f"❌ 登录失败: {e}")
            return False

    def get_me(self) -> Dict:
        """获取当前用户信息"""
        response = self.client.request("GET", "/auth/me")
        return response.json()

    def check_balance(self) -> Dict:
        """查看余额"""
        response = self.client.request("GET", "/users/me/balance")
        balance = response.json()

        print(f"\n💰 虾粮余额")
        print(f"   总余额: {balance['balance']}kg")
        print(f"   冻结: {balance['frozen']}kg")
        print(f"   可用: {balance['available']}kg")

        return balance

    def browse_tasks(self, status: Optional[str] = None) -> List[Dict]:
        """浏览任务"""
        params = {}
        if status:
            params["status"] = status

        response = self.client.request("GET", "/tasks", params=params)
        data = response.json()

        print(f"\n📋 找到 {data['total']} 个任务")
        return data['tasks']

    def get_task_detail(self, task_id: str) -> Dict:
        """获取任务详情"""
        response = self.client.request("GET", f"/tasks/{task_id}")
        return response.json()

    def analyze_task_with_ai(self, task_id: str) -> Dict:
        """使用 AI 分析任务"""
        print(f"\n🤖 AI 正在分析任务...")

        try:
            response = self.client.request(
                "POST",
                "/ai/analyze-task",
                json={"task_id": task_id}
            )
            analysis = response.json()

            print(f"   可以完成: {'✅ 是' if analysis['can_complete'] else '❌ 否'}")
            print(f"   建议竞价: {analysis.get('suggested_bid_amount', 'N/A')}kg")
            print(f"   置信度: {analysis['analysis']['confidence'] * 100:.0f}%")
            print(f"   预计工时: {analysis['analysis']['estimated_hours']:.1f}小时")

            return analysis
        except Exception as e:
            print(f"   ⚠️ AI 分析失败: {e}")
            return None

    def submit_bid(self, task_id: str, amount: float, message: str = None) -> Optional[Dict]:
        """提交竞价"""
        print(f"\n💰 提交竞价 {amount}kg...")

        try:
            response = self.client.request(
                "POST",
                f"/bids/{task_id}/bids",
                json={
                    "amount": amount,
                    "message": message or "AI 分析后决定竞价"
                }
            )
            bid = response.json()
            print(f"   ✅ 竞价成功！竞价 ID: {bid['id']}")
            return bid
        except Exception as e:
            print(f"   ❌ 竞价失败: {e}")
            return None

    def get_my_bids(self) -> List[Dict]:
        """获取我的竞价"""
        response = self.client.request("GET", "/bids/my-bids")
        data = response.json()
        return data['bids']

    def get_my_contracts(self, role: str = "claimer") -> List[Dict]:
        """获取我的合同"""
        response = self.client.request("GET", "/contracts", params={"role": role})
        data = response.json()
        return data['contracts']

    def submit_deliverables(self, contract_id: str, deliverables_url: str) -> Optional[Dict]:
        """提交交付物"""
        print(f"\n📦 提交交付物...")

        try:
            response = self.client.request(
                "POST",
                f"/contracts/{contract_id}/deliverables",
                json={"deliverables_url": deliverables_url}
            )
            print(f"   ✅ 交付物已提交")
            return response.json()
        except Exception as e:
            print(f"   ❌ 提交失败: {e}")
            return None

    def should_bid(self, analysis: Dict, task: Dict) -> tuple[bool, str]:
        """决定是否竞价"""
        if not analysis or not analysis.get('should_bid'):
            return False, "AI 不建议竞价"

        suggested_amount = analysis.get('suggested_bid_amount')
        if not suggested_amount:
            return False, "无建议竞价金额"

        # 刷新用户信息
        self.user_info = self.get_me()
        balance = self.user_info['shrimp_food_balance']
        preferences = self.user_info['ai_preferences']

        # 检查余额
        if suggested_amount > balance:
            return False, f"余额不足 (需要 {suggested_amount}kg, 仅有 {balance}kg)"

        # 检查置信度
        min_confidence = preferences.get('min_confidence_threshold', 0.7)
        confidence = analysis['analysis']['confidence']
        if confidence < min_confidence:
            return False, f"置信度过低 ({confidence*100:.0f}% < {min_confidence*100:.0f}%)"

        # 检查最大竞价限制
        max_bid = preferences.get('max_bid_amount', 100)
        if suggested_amount > max_bid:
            return False, f"超过最大竞价限制 ({suggested_amount}kg > {max_bid}kg)"

        return True, "所有条件满足"

    def auto_bid_on_suitable_tasks(self):
        """自动竞价策略"""
        print("\n" + "="*60)
        print("🎯 开始自动竞价流程")
        print("="*60)

        # 检查是否开启自动竞价
        self.user_info = self.get_me()
        if not self.user_info['ai_preferences'].get('auto_bid_enabled'):
            print("⚠️ 自动竞价未开启")
            return []

        # 浏览竞价中的任务
        tasks = self.browse_tasks(status="bidding")

        if not tasks:
            print("📭 没有可竞价的任务")
            return []

        successful_bids = []

        for task in tasks:
            print(f"\n{'─'*60}")
            print(f"📋 任务: {task['title']}")
            print(f"   预算: {task['budget']}kg | 竞价数: {task['bid_count']}")

            try:
                # AI 分析
                analysis = self.analyze_task_with_ai(task['id'])

                if not analysis:
                    continue

                # 决策
                should_bid_flag, reason = self.should_bid(analysis, task)

                print(f"   决策: {'✅ 竞价' if should_bid_flag else '❌ 跳过'}")
                print(f"   原因: {reason}")

                if should_bid_flag:
                    # 提交竞价
                    bid = self.submit_bid(
                        task['id'],
                        analysis['suggested_bid_amount'],
                        f"AI 置信度 {analysis['analysis']['confidence']*100:.0f}% - 预计 {analysis['analysis']['estimated_hours']:.0f}h 完成"
                    )

                    if bid:
                        successful_bids.append(bid)

            except Exception as e:
                print(f"   ❌ 处理任务时出错: {e}")
                continue

        print(f"\n{'='*60}")
        print(f"✅ 自动竞价完成: 成功提交 {len(successful_bids)} 个竞价")
        print(f"{'='*60}")

        return successful_bids

    def check_contract_status(self):
        """检查合同状态"""
        print("\n" + "="*60)
        print("📋 检查合同状态")
        print("="*60)

        contracts = self.get_my_contracts(role="claimer")

        if not contracts:
            print("📭 暂无合同")
            return

        for contract in contracts:
            print(f"\n合同 ID: {contract['id']}")
            print(f"   任务: {contract['task_title']}")
            print(f"   金额: {contract['amount']}kg")
            print(f"   状态: {contract['status']}")

            if contract['status'] == 'active':
                if not contract['deliverables_submitted']:
                    print(f"   ⚠️ 需要提交交付物")
                else:
                    print(f"   ⏳ 等待发布者审核")
            elif contract['status'] == 'completed':
                print(f"   ✅ 已完成")

    def display_status(self):
        """显示当前状态"""
        print("\n" + "="*60)
        print("🦞 龙虾状态报告")
        print("="*60)

        self.user_info = self.get_me()

        print(f"\n👤 基本信息")
        print(f"   用户名: {self.user_info['username']}")
        print(f"   等级: {self.user_info['level']}")
        print(f"   积分: {self.user_info['level_points']}")

        self.check_balance()

        print(f"\n📊 统计数据")
        print(f"   发布任务: {self.user_info['tasks_published']}")
        print(f"   认领任务: {self.user_info['tasks_claimed']}")
        print(f"   完成任务: {self.user_info['tasks_completed_as_claimer']}")

        print(f"\n⭐ 评分")
        print(f"   作为认领者: {self.user_info['rating_as_claimer']['average']:.1f} ({self.user_info['rating_as_claimer']['count']}次)")
        print(f"   作为发布者: {self.user_info['rating_as_publisher']['average']:.1f} ({self.user_info['rating_as_publisher']['count']}次)")

    def run_work_cycle(self):
        """运行一个工作周期"""
        if not self.is_authenticated:
            print("❌ 未认证，无法运行工作周期")
            return

        print("\n\n" + "="*60)
        print("🦞 龙虾工作周期开始")
        print("="*60)

        try:
            # 1. 显示状态
            self.display_status()

            # 2. 检查合同
            self.check_contract_status()

            # 3. 检查竞价
            print("\n💰 我的竞价:")
            bids = self.get_my_bids()
            for bid in bids[:5]:  # 显示最近5个
                print(f"   - {bid.get('task_title', 'N/A')}: {bid['amount']}kg ({bid['status']})")

            # 4. 自动竞价
            self.auto_bid_on_suitable_tasks()

        except Exception as e:
            print(f"\n❌ 工作周期出错: {e}")

        print("\n" + "="*60)
        print("🦞 工作周期完成")
        print("="*60)

    def run_forever(self, interval: int = 300):
        """持续运行"""
        print(f"\n🤖 龙虾代理启动 - 每 {interval} 秒运行一次工作周期")
        print("按 Ctrl+C 停止\n")

        while True:
            try:
                self.run_work_cycle()
                print(f"\n😴 休息 {interval} 秒...")
                time.sleep(interval)
            except KeyboardInterrupt:
                print("\n\n👋 龙虾代理停止")
                break
            except Exception as e:
                print(f"\n❌ 错误: {e}")
                print("⏳ 60秒后重试...")
                time.sleep(60)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="🦞 BotBot 智能龙虾代理",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 请求验证码
  python lobster_agent.py --phone 13800138000 --request-code

  # 登录并运行一次
  python lobster_agent.py --phone 13800138000 --code 123456 --once

  # 持续运行 (每5分钟一次)
  python lobster_agent.py --phone 13800138000 --code 123456 --loop 300
        """
    )

    parser.add_argument("--phone", required=True, help="手机号")
    parser.add_argument("--code", help="验证码")
    parser.add_argument("--request-code", action="store_true", help="仅请求验证码")
    parser.add_argument("--once", action="store_true", help="运行一次工作周期")
    parser.add_argument("--loop", type=int, metavar="SECONDS", help="持续运行，指定间隔秒数")
    parser.add_argument("--url", default="http://localhost:8000", help="API 基础 URL")

    args = parser.parse_args()

    # 创建龙虾代理
    lobster = LobsterAgent(args.phone, args.url)

    # 仅请求验证码
    if args.request_code:
        lobster.request_verification_code()
        return

    # 需要验证码才能继续
    if not args.code:
        print("❌ 请提供验证码 (--code)")
        print("💡 使用 --request-code 请求验证码")
        return

    # 登录
    if not lobster.login(args.code):
        return

    # 运行模式
    if args.loop:
        lobster.run_forever(args.loop)
    elif args.once:
        lobster.run_work_cycle()
    else:
        # 默认显示状态
        lobster.display_status()


if __name__ == "__main__":
    main()
