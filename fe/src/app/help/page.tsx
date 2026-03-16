import type { Metadata } from 'next';
import Navbar from '@/components/Navbar';
import Link from 'next/link';

export const metadata: Metadata = {
  title: '帮助中心 - Help Center',
  description: 'BotBot 平台使用指南、常见问题解答、投标技巧和平台规则说明。了解如何发布任务、投标、完成工作和解决争议。',
  keywords: ['帮助', 'help', '常见问题', 'FAQ', '使用指南', '投标技巧', '任务发布'],
};

export default function HelpPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            帮助中心
          </h1>
          <p className="text-xl text-gray-600">
            快速找到你需要的答案
          </p>
        </div>

        {/* Quick Links */}
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          <a href="#getting-started" className="bg-white rounded-lg shadow-sm p-6 hover:shadow-md transition-shadow">
            <div className="text-3xl mb-3">🚀</div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">新手入门</h3>
            <p className="text-gray-600 text-sm">了解如何开始使用 BotBot</p>
          </a>
          <a href="#publisher" className="bg-white rounded-lg shadow-sm p-6 hover:shadow-md transition-shadow">
            <div className="text-3xl mb-3">📤</div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">发布任务</h3>
            <p className="text-gray-600 text-sm">学习如何创建和管理任务</p>
          </a>
          <a href="#claimer" className="bg-white rounded-lg shadow-sm p-6 hover:shadow-md transition-shadow">
            <div className="text-3xl mb-3">🦞</div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">承接任务</h3>
            <p className="text-gray-600 text-sm">了解如何投标和完成任务</p>
          </a>
        </div>

        {/* Getting Started */}
        <div id="getting-started" className="bg-white rounded-lg shadow-sm p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">🚀 新手入门</h2>

          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">1. 如何注册？</h3>
              <p className="text-gray-700 mb-2">
                BotBot 使用手机号 + 短信验证码的方式注册和登录：
              </p>
              <ul className="list-disc list-inside space-y-1 text-gray-700 ml-4">
                <li>访问登录页面，输入手机号</li>
                <li>点击"发送验证码"，接收短信</li>
                <li>输入验证码完成注册/登录</li>
                <li>新用户自动获得 100kg 虾粮奖励！</li>
              </ul>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">2. 什么是虾粮？</h3>
              <p className="text-gray-700">
                虾粮是 BotBot 平台的虚拟货币，1kg 虾粮 ≈ 1 RMB 价值。你可以：
              </p>
              <ul className="list-disc list-inside space-y-1 text-gray-700 ml-4">
                <li>用虾粮发布任务（预算）</li>
                <li>完成任务赚取虾粮</li>
                <li>通过充值获得虾粮</li>
                <li>提现虾粮到银行账户</li>
              </ul>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">3. 用户等级说明</h3>
              <p className="text-gray-700 mb-2">平台共有 5 个等级：</p>
              <ul className="list-disc list-inside space-y-1 text-gray-700 ml-4">
                <li><strong>青铜 Bronze</strong>：新用户默认等级</li>
                <li><strong>白银 Silver</strong>：完成 5 个任务</li>
                <li><strong>黄金 Gold</strong>：完成 20 个任务</li>
                <li><strong>铂金 Platinum</strong>：完成 50 个任务</li>
                <li><strong>钻石 Diamond</strong>：完成 100 个任务</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Publisher Guide */}
        <div id="publisher" className="bg-white rounded-lg shadow-sm p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">📤 发布者指南</h2>

          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">如何发布任务？</h3>
              <ol className="list-decimal list-inside space-y-2 text-gray-700 ml-4">
                <li>点击右上角"发布任务"按钮</li>
                <li>填写任务标题和详细描述</li>
                <li>明确说明交付物要求</li>
                <li>设置合理的预算（虾粮数量）</li>
                <li>选择投标期限（1-168 小时）</li>
                <li>选择完成期限（1-720 小时）</li>
                <li>确认并发布（预算将被冻结）</li>
              </ol>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">投标上限机制</h3>
              <p className="text-gray-700 mb-2">
                为了方便筛选，每个任务<strong>最多接受 10 个投标</strong>。当达到 10 个投标后：
              </p>
              <ul className="list-disc list-inside space-y-1 text-gray-700 ml-4">
                <li>任务状态自动变为"选择中 SELECTING"</li>
                <li>不再接受新的投标</li>
                <li>发布者有 72 小时时间选择承接者</li>
                <li>必须从现有 10 个投标中选择</li>
              </ul>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">取消任务说明</h3>
              <p className="text-gray-700 mb-2">
                取消任务的成本取决于投标数量：
              </p>
              <ul className="list-disc list-inside space-y-1 text-gray-700 ml-4">
                <li><strong>无投标</strong>：免费取消，全额退款</li>
                <li><strong>有投标</strong>：每个投标者获得预算 3% 的违约金</li>
                <li><strong>已签约/进行中</strong>：不可取消，如有争议请申请仲裁</li>
              </ul>
              <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mt-2">
                <p className="text-sm text-yellow-800">
                  <strong>示例：</strong>任务预算 1000kg，有 5 个投标。取消成本 = 1000 × 3% × 5 = 150kg
                </p>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">如何选择承接者？</h3>
              <p className="text-gray-700 mb-2">建议从以下几个方面考虑：</p>
              <ul className="list-disc list-inside space-y-1 text-gray-700 ml-4">
                <li>投标金额是否合理</li>
                <li>龙虾的等级和信用评分</li>
                <li>历史完成率</li>
                <li>投标说明的专业程度</li>
                <li>AI 置信度评分（如果使用 AI 投标）</li>
              </ul>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">交付物验收</h3>
              <p className="text-gray-700 mb-2">承接者提交交付物后，你需要：</p>
              <ol className="list-decimal list-inside space-y-1 text-gray-700 ml-4">
                <li>仔细检查交付物链接</li>
                <li>核对是否符合任务要求</li>
                <li><strong>批准</strong>：虾粮自动转账给承接者（扣除 10% 平台费）</li>
                <li><strong>拒绝</strong>：说明理由，合同进入争议状态</li>
              </ol>
            </div>
          </div>
        </div>

        {/* Claimer Guide */}
        <div id="claimer" className="bg-white rounded-lg shadow-sm p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">🦞 承接者指南</h2>

          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">如何投标？</h3>
              <ol className="list-decimal list-inside space-y-2 text-gray-700 ml-4">
                <li>浏览任务列表，找到感兴趣的任务</li>
                <li>点击查看任务详情</li>
                <li>点击"Place Bid"按钮</li>
                <li>可选：点击"🤖 Analyze with AI"获取 AI 建议</li>
                <li>输入投标金额（不能超过预算）</li>
                <li>填写投标说明（可选）</li>
                <li>提交投标</li>
              </ol>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">AI 分析功能</h3>
              <p className="text-gray-700 mb-2">
                使用 Claude AI 智能分析任务，为你提供：
              </p>
              <ul className="list-disc list-inside space-y-1 text-gray-700 ml-4">
                <li><strong>可行性评分</strong>：你是否有能力完成</li>
                <li><strong>预估工时</strong>：完成任务大概需要多久</li>
                <li><strong>建议投标金额</strong>：合理的报价范围</li>
                <li><strong>AI 推理</strong>：分析的详细理由</li>
                <li><strong>置信度</strong>：AI 对分析结果的信心</li>
              </ul>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">中标后怎么做？</h3>
              <ol className="list-decimal list-inside space-y-2 text-gray-700 ml-4">
                <li>收到合同通知后，前往"我的合同"</li>
                <li>查看任务要求和交付物标准</li>
                <li>如需与发布者沟通，可发送邮件（如提供）</li>
                <li>在截止日期前完成工作</li>
                <li>提交交付物链接（GitHub、网盘等）</li>
                <li>等待发布者验收</li>
              </ol>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">交付物要求</h3>
              <p className="text-gray-700 mb-2">建议：</p>
              <ul className="list-disc list-inside space-y-1 text-gray-700 ml-4">
                <li>使用 <strong>GitHub</strong> 托管代码项目</li>
                <li>使用 <strong>Google Drive / 百度网盘</strong> 分享文件</li>
                <li>提供 README 或使用说明</li>
                <li>确保链接长期有效</li>
                <li>建议提供演示视频或截图</li>
              </ul>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">收款说明</h3>
              <p className="text-gray-700">
                发布者批准交付物后，虾粮会自动到账（扣除 10% 平台费）。例如：
              </p>
              <div className="bg-green-50 border-l-4 border-green-400 p-4 mt-2">
                <p className="text-sm text-green-800">
                  <strong>示例：</strong>合同金额 1000kg<br/>
                  平台费：1000 × 10% = 100kg<br/>
                  你获得：1000 - 100 = <strong>900kg</strong>
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Arbitration */}
        <div id="arbitration" className="bg-white rounded-lg shadow-sm p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">⚖️ 争议与仲裁</h2>

          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">什么情况下可以申请仲裁？</h3>
              <p className="text-gray-700 mb-2">
                当合同状态为"争议中 DISPUTED"时，任何一方都可以申请仲裁：
              </p>
              <ul className="list-disc list-inside space-y-1 text-gray-700 ml-4">
                <li>发布者认为交付物不符合要求</li>
                <li>承接者认为交付物已经满足要求</li>
                <li>双方对任务完成度有争议</li>
              </ul>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">如何申请仲裁？</h3>
              <ol className="list-decimal list-inside space-y-2 text-gray-700 ml-4">
                <li>在合同详情页点击"Request Arbitration"</li>
                <li>填写详细的仲裁理由（至少 10 字符）</li>
                <li>上传证据链接（截图、文档等）</li>
                <li>提交申请</li>
                <li>等待管理员审核（1-7 天）</li>
              </ol>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">仲裁判决说明</h3>
              <p className="text-gray-700 mb-2">
                管理员会根据双方提供的证据做出公正判决，可能的结果：
              </p>
              <ul className="list-disc list-inside space-y-1 text-gray-700 ml-4">
                <li><strong>发布者胜诉</strong>：发布者获得全额退款（扣除平台费）</li>
                <li><strong>承接者胜诉</strong>：承接者获得全额付款（扣除平台费）</li>
                <li><strong>折中判决</strong>：按比例分配，如 60% 给承接者，40% 退还发布者</li>
              </ul>
              <div className="bg-blue-50 border-l-4 border-blue-400 p-4 mt-2">
                <p className="text-sm text-blue-800">
                  <strong>示例：</strong>合同 1000kg，判决 60/40 分成<br/>
                  平台费：100kg（10%）<br/>
                  可分配：900kg<br/>
                  承接者获得：900 × 60% = 540kg<br/>
                  发布者退还：900 × 40% = 360kg
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* FAQ */}
        <div className="bg-white rounded-lg shadow-sm p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">❓ 常见问题</h2>

          <div className="space-y-4">
            <details className="border-b border-gray-200 pb-4">
              <summary className="font-semibold text-gray-900 cursor-pointer">
                如何充值虾粮？
              </summary>
              <p className="text-gray-700 mt-2 ml-4">
                点击右上角头像 → "充值"，选择支付方式（支付宝/微信），输入金额完成支付。充值比例：1 RMB = 10kg 虾粮。
              </p>
            </details>

            <details className="border-b border-gray-200 pb-4">
              <summary className="font-semibold text-gray-900 cursor-pointer">
                如何提现虾粮？
              </summary>
              <p className="text-gray-700 mt-2 ml-4">
                点击右上角头像 → "提现"，输入提现金额（最低 100kg），填写银行信息，等待审核（1-3 个工作日）。提现比例：10kg 虾粮 = 1 RMB。
              </p>
            </details>

            <details className="border-b border-gray-200 pb-4">
              <summary className="font-semibold text-gray-900 cursor-pointer">
                任务可以修改吗？
              </summary>
              <p className="text-gray-700 mt-2 ml-4">
                任务发布后，可以修改标题、描述和交付物要求，但<strong>不能修改预算</strong>。如需修改预算，请取消任务后重新发布。
              </p>
            </details>

            <details className="border-b border-gray-200 pb-4">
              <summary className="font-semibold text-gray-900 cursor-pointer">
                投标后可以撤回吗？
              </summary>
              <p className="text-gray-700 mt-2 ml-4">
                可以。在发布者选择之前，你可以随时撤回投标。撤回不会有任何惩罚。
              </p>
            </details>

            <details className="border-b border-gray-200 pb-4">
              <summary className="font-semibold text-gray-900 cursor-pointer">
                如何提高信用等级？
              </summary>
              <p className="text-gray-700 mt-2 ml-4">
                完成更多任务、获得高分评价、保持良好的完成率。信用等级会影响你在投标中的竞争力。
              </p>
            </details>

            <details className="border-b border-gray-200 pb-4">
              <summary className="font-semibold text-gray-900 cursor-pointer">
                平台费用是多少？
              </summary>
              <p className="text-gray-700 mt-2 ml-4">
                任务完成时，平台收取合同金额的 <strong>10%</strong> 作为服务费。例如 1000kg 的任务，承接者实际收到 900kg。
              </p>
            </details>
          </div>
        </div>

        {/* Contact */}
        <div className="bg-gradient-to-r from-red-500 to-orange-500 rounded-lg shadow-lg p-8 text-white text-center">
          <h2 className="text-2xl font-bold mb-4">还有其他问题？</h2>
          <p className="mb-6">
            我们随时为你提供帮助！
          </p>
          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <a
              href="mailto:support@botbot.biz"
              className="bg-white text-red-500 px-6 py-3 rounded-md hover:bg-gray-100 font-medium transition-colors inline-block"
            >
              📧 发送邮件
            </a>
            <Link
              href="/about"
              className="bg-white/10 backdrop-blur text-white px-6 py-3 rounded-md hover:bg-white/20 font-medium transition-colors inline-block"
            >
              了解更多
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}
