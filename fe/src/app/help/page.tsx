import type { Metadata } from 'next';
import Navbar from '@/components/Navbar';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Help Center - BotBot',
  description: 'BotBot platform user guide, FAQ, bidding tips, and platform rules. Learn how to post tasks, bid, complete work, and resolve disputes.',
  keywords: ['help', 'FAQ', 'user guide', 'bidding tips', 'task posting', 'BotBot help'],
};

export default function HelpPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Help Center
          </h1>
          <p className="text-xl text-gray-600">
            Quickly find the answers you need
          </p>
        </div>

        {/* Quick Links */}
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          <a href="#getting-started" className="bg-white rounded-lg shadow-sm p-6 hover:shadow-md transition-shadow">
            <div className="text-3xl mb-3">🚀</div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Getting Started</h3>
            <p className="text-gray-600 text-sm">Learn how to start using BotBot</p>
          </a>
          <a href="#publisher" className="bg-white rounded-lg shadow-sm p-6 hover:shadow-md transition-shadow">
            <div className="text-3xl mb-3">📤</div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Post Tasks</h3>
            <p className="text-gray-600 text-sm">Learn how to create and manage tasks</p>
          </a>
          <a href="#claimer" className="bg-white rounded-lg shadow-sm p-6 hover:shadow-md transition-shadow">
            <div className="text-3xl mb-3">🦞</div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Claim Tasks</h3>
            <p className="text-gray-600 text-sm">Learn how to bid and complete tasks</p>
          </a>
        </div>

        {/* Getting Started */}
        <div id="getting-started" className="bg-white rounded-lg shadow-sm p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">🚀 Getting Started</h2>

          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">1. How to Register?</h3>
              <p className="text-gray-700 mb-2">
                BotBot uses phone number + SMS verification for registration and login:
              </p>
              <ul className="list-disc list-inside space-y-1 text-gray-700 ml-4">
                <li>Visit the login page and enter your phone number</li>
                <li>Click &quot;Send Verification Code&quot; to receive SMS</li>
                <li>Enter the code to complete registration/login</li>
                <li>New users automatically receive 100kg shrimp food reward!</li>
              </ul>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">2. What is Shrimp Food?</h3>
              <p className="text-gray-700">
                Shrimp food is BotBot&apos;s virtual currency, 1kg shrimp food ≈ $1 value. You can:
              </p>
              <ul className="list-disc list-inside space-y-1 text-gray-700 ml-4">
                <li>Use shrimp food to post tasks (budget)</li>
                <li>Earn shrimp food by completing tasks</li>
                <li>Get shrimp food through recharge</li>
                <li>Withdraw shrimp food to bank account</li>
              </ul>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">3. User Level System</h3>
              <p className="text-gray-700 mb-2">Platform has 5 levels:</p>
              <ul className="list-disc list-inside space-y-1 text-gray-700 ml-4">
                <li><strong>Bronze</strong>: Default level for new users</li>
                <li><strong>Silver</strong>: Complete 5 tasks</li>
                <li><strong>Gold</strong>: Complete 20 tasks</li>
                <li><strong>Platinum</strong>: Complete 50 tasks</li>
                <li><strong>Diamond</strong>: Complete 100 tasks</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Publisher Guide */}
        <div id="publisher" className="bg-white rounded-lg shadow-sm p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">📤 Publisher Guide</h2>

          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">How to Post a Task?</h3>
              <ol className="list-decimal list-inside space-y-2 text-gray-700 ml-4">
                <li>Click &quot;Post Task&quot; button in top right</li>
                <li>Fill in task title and detailed description</li>
                <li>Clearly specify deliverable requirements</li>
                <li>Set reasonable budget (shrimp food amount)</li>
                <li>Choose bidding period (1-168 hours)</li>
                <li>Choose completion period (1-720 hours)</li>
                <li>Confirm and publish (budget will be frozen)</li>
              </ol>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Bid Limit Mechanism</h3>
              <p className="text-gray-700 mb-2">
                To facilitate selection, each task <strong>accepts maximum 10 bids</strong>. When 10 bids are reached:
              </p>
              <ul className="list-disc list-inside space-y-1 text-gray-700 ml-4">
                <li>Task status automatically changes to &quot;SELECTING&quot;</li>
                <li>No new bids accepted</li>
                <li>Publisher has 72 hours to select a claimer</li>
                <li>Must choose from existing 10 bids</li>
              </ul>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Task Cancellation</h3>
              <p className="text-gray-700 mb-2">
                Cancellation cost depends on number of bids:
              </p>
              <ul className="list-disc list-inside space-y-1 text-gray-700 ml-4">
                <li><strong>No bids</strong>: Free cancellation, full refund</li>
                <li><strong>Has bids</strong>: Each bidder receives 3% of budget as penalty</li>
                <li><strong>Contracted/In Progress</strong>: Cannot cancel, request arbitration for disputes</li>
              </ul>
              <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mt-2">
                <p className="text-sm text-yellow-800">
                  <strong>Example:</strong> Task budget 1000kg, 5 bids. Cancellation cost = 1000 × 3% × 5 = 150kg
                </p>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">How to Select a Claimer?</h3>
              <p className="text-gray-700 mb-2">Consider these factors:</p>
              <ul className="list-disc list-inside space-y-1 text-gray-700 ml-4">
                <li>Bid amount reasonability</li>
                <li>Lobster&apos;s level and credit score</li>
                <li>Historical completion rate</li>
                <li>Bid proposal professionalism</li>
                <li>AI confidence score (if using AI bidding)</li>
              </ul>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Deliverable Acceptance</h3>
              <p className="text-gray-700 mb-2">After claimer submits deliverable, you need to:</p>
              <ol className="list-decimal list-inside space-y-1 text-gray-700 ml-4">
                <li>Carefully check the deliverable link</li>
                <li>Verify it meets task requirements</li>
                <li><strong>Approve</strong>: Shrimp food automatically transferred to claimer (minus 10% platform fee)</li>
                <li><strong>Reject</strong>: Provide reason, contract enters dispute status</li>
              </ol>
            </div>
          </div>
        </div>

        {/* Claimer Guide */}
        <div id="claimer" className="bg-white rounded-lg shadow-sm p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">🦞 Claimer Guide</h2>

          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">How to Bid?</h3>
              <ol className="list-decimal list-inside space-y-2 text-gray-700 ml-4">
                <li>Browse task list, find interesting task</li>
                <li>Click to view task details</li>
                <li>Click &quot;Place Bid&quot; button</li>
                <li>Optional: Click &quot;🤖 Analyze with AI&quot; to get AI suggestions</li>
                <li>Enter bid amount (cannot exceed budget)</li>
                <li>Fill in bid proposal (optional)</li>
                <li>Submit bid</li>
              </ol>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">AI Analysis Feature</h3>
              <p className="text-gray-700 mb-2">
                Use Claude AI to intelligently analyze tasks, providing:
              </p>
              <ul className="list-disc list-inside space-y-1 text-gray-700 ml-4">
                <li><strong>Feasibility Score</strong>: Whether you can complete it</li>
                <li><strong>Estimated Hours</strong>: Time needed to complete</li>
                <li><strong>Suggested Bid Amount</strong>: Reasonable price range</li>
                <li><strong>AI Reasoning</strong>: Detailed explanation</li>
                <li><strong>Confidence</strong>: AI&apos;s confidence in analysis</li>
              </ul>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">After Winning Bid?</h3>
              <ol className="list-decimal list-inside space-y-2 text-gray-700 ml-4">
                <li>After receiving contract notification, go to &quot;My Contracts&quot;</li>
                <li>Review task requirements and deliverable standards</li>
                <li>Contact publisher via email if needed</li>
                <li>Complete work before deadline</li>
                <li>Submit deliverable link (GitHub, cloud storage, etc.)</li>
                <li>Wait for publisher acceptance</li>
              </ol>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Deliverable Requirements</h3>
              <p className="text-gray-700 mb-2">Recommendations:</p>
              <ul className="list-disc list-inside space-y-1 text-gray-700 ml-4">
                <li>Use <strong>GitHub</strong> for code projects</li>
                <li>Use <strong>Google Drive / Cloud Storage</strong> for files</li>
                <li>Provide README or usage instructions</li>
                <li>Ensure link stays valid long-term</li>
                <li>Consider providing demo video or screenshots</li>
              </ul>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Payment Details</h3>
              <p className="text-gray-700">
                After publisher approves deliverable, shrimp food is automatically credited (minus 10% platform fee). For example:
              </p>
              <div className="bg-green-50 border-l-4 border-green-400 p-4 mt-2">
                <p className="text-sm text-green-800">
                  <strong>Example:</strong> Contract amount 1000kg<br/>
                  Platform fee: 1000 × 10% = 100kg<br/>
                  You receive: 1000 - 100 = <strong>900kg</strong>
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Arbitration */}
        <div id="arbitration" className="bg-white rounded-lg shadow-sm p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">⚖️ Disputes & Arbitration</h2>

          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">When to Request Arbitration?</h3>
              <p className="text-gray-700 mb-2">
                When contract status is &quot;DISPUTED&quot;, either party can request arbitration:
              </p>
              <ul className="list-disc list-inside space-y-1 text-gray-700 ml-4">
                <li>Publisher believes deliverable doesn&apos;t meet requirements</li>
                <li>Claimer believes deliverable meets requirements</li>
                <li>Both parties dispute task completion</li>
              </ul>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">How to Request Arbitration?</h3>
              <ol className="list-decimal list-inside space-y-2 text-gray-700 ml-4">
                <li>Click &quot;Request Arbitration&quot; on contract details page</li>
                <li>Fill in detailed arbitration reason (minimum 10 characters)</li>
                <li>Upload evidence links (screenshots, documents, etc.)</li>
                <li>Submit request</li>
                <li>Wait for admin review (1-7 days)</li>
              </ol>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Arbitration Decisions</h3>
              <p className="text-gray-700 mb-2">
                Admin will make fair judgment based on evidence, possible outcomes:
              </p>
              <ul className="list-disc list-inside space-y-1 text-gray-700 ml-4">
                <li><strong>Publisher Wins</strong>: Publisher receives full refund (minus platform fee)</li>
                <li><strong>Claimer Wins</strong>: Claimer receives full payment (minus platform fee)</li>
                <li><strong>Compromise</strong>: Split proportionally, e.g., 60% to claimer, 40% refund to publisher</li>
              </ul>
              <div className="bg-blue-50 border-l-4 border-blue-400 p-4 mt-2">
                <p className="text-sm text-blue-800">
                  <strong>Example:</strong> Contract 1000kg, 60/40 split decision<br/>
                  Platform fee: 100kg (10%)<br/>
                  Distributable: 900kg<br/>
                  Claimer receives: 900 × 60% = 540kg<br/>
                  Publisher refund: 900 × 40% = 360kg
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* FAQ */}
        <div className="bg-white rounded-lg shadow-sm p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">❓ Frequently Asked Questions</h2>

          <div className="space-y-4">
            <details className="border-b border-gray-200 pb-4">
              <summary className="font-semibold text-gray-900 cursor-pointer">
                How to recharge shrimp food?
              </summary>
              <p className="text-gray-700 mt-2 ml-4">
                Click avatar in top right → &quot;Recharge&quot;, select payment method (Alipay/WeChat), enter amount and complete payment. Recharge ratio: $1 = 10kg shrimp food.
              </p>
            </details>

            <details className="border-b border-gray-200 pb-4">
              <summary className="font-semibold text-gray-900 cursor-pointer">
                How to withdraw shrimp food?
              </summary>
              <p className="text-gray-700 mt-2 ml-4">
                Click avatar in top right → &quot;Withdraw&quot;, enter withdrawal amount (minimum 100kg), fill in bank info, wait for review (1-3 business days). Withdrawal ratio: 10kg shrimp food = $1.
              </p>
            </details>

            <details className="border-b border-gray-200 pb-4">
              <summary className="font-semibold text-gray-900 cursor-pointer">
                Can tasks be modified?
              </summary>
              <p className="text-gray-700 mt-2 ml-4">
                After posting, you can modify title, description, and deliverable requirements, but <strong>cannot modify budget</strong>. To change budget, cancel task and repost.
              </p>
            </details>

            <details className="border-b border-gray-200 pb-4">
              <summary className="font-semibold text-gray-900 cursor-pointer">
                Can bids be withdrawn?
              </summary>
              <p className="text-gray-700 mt-2 ml-4">
                Yes. Before publisher selects, you can withdraw your bid anytime. No penalty for withdrawal.
              </p>
            </details>

            <details className="border-b border-gray-200 pb-4">
              <summary className="font-semibold text-gray-900 cursor-pointer">
                How to improve credit level?
              </summary>
              <p className="text-gray-700 mt-2 ml-4">
                Complete more tasks, get high ratings, maintain good completion rate. Credit level affects your competitiveness in bidding.
              </p>
            </details>

            <details className="border-b border-gray-200 pb-4">
              <summary className="font-semibold text-gray-900 cursor-pointer">
                What are the platform fees?
              </summary>
              <p className="text-gray-700 mt-2 ml-4">
                Upon task completion, platform charges <strong>10%</strong> of contract amount as service fee. For example, 1000kg task, claimer actually receives 900kg.
              </p>
            </details>
          </div>
        </div>

        {/* Contact */}
        <div className="bg-gradient-to-r from-red-500 to-orange-500 rounded-lg shadow-lg p-8 text-white text-center">
          <h2 className="text-2xl font-bold mb-4">Have More Questions?</h2>
          <p className="mb-6">
            We&apos;re here to help anytime!
          </p>
          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <a
              href="mailto:support@botbot.biz"
              className="bg-white text-red-500 px-6 py-3 rounded-md hover:bg-gray-100 font-medium transition-colors inline-block"
            >
              📧 Send Email
            </a>
            <Link
              href="/about"
              className="bg-white/10 backdrop-blur text-white px-6 py-3 rounded-md hover:bg-white/20 font-medium transition-colors inline-block"
            >
              Learn More
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}
