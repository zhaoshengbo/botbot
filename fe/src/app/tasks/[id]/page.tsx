'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { apiClient } from '@/lib/api';
import type { Task, Bid, AnalyzeTaskResponse } from '@/types';
import { TaskStatus } from '@/types';
import Navbar from '@/components/Navbar';
import ConfirmDialog from '@/components/ConfirmDialog';
import { formatDistanceToNow } from 'date-fns';
import toast from 'react-hot-toast';

export default function TaskDetailPage() {
  const params = useParams();
  const taskId = params.id as string;
  const { user } = useAuth();
  const router = useRouter();

  const [task, setTask] = useState<Task | null>(null);
  const [bids, setBids] = useState<Bid[]>([]);
  const [loading, setLoading] = useState(true);
  const [aiAnalysis, setAiAnalysis] = useState<AnalyzeTaskResponse | null>(null);
  const [analyzingAI, setAnalyzingAI] = useState(false);

  // Bid form
  const [showBidForm, setShowBidForm] = useState(false);
  const [bidAmount, setBidAmount] = useState('');
  const [bidMessage, setBidMessage] = useState('');
  const [submittingBid, setSubmittingBid] = useState(false);

  // Cancel task
  const [showCancelDialog, setShowCancelDialog] = useState(false);
  const [cancellationEstimate, setCancellationEstimate] = useState<any>(null);
  const [cancellationReason, setCancellationReason] = useState('');
  const [cancellingTask, setCancellingTask] = useState(false);
  const [showCancelConfirm, setShowCancelConfirm] = useState(false);

  // Accept bid confirmation
  const [showAcceptBidConfirm, setShowAcceptBidConfirm] = useState(false);
  const [bidToAccept, setBidToAccept] = useState<string | null>(null);

  const loadTaskData = useCallback(async () => {
    try {
      setLoading(true);
      const [taskData, bidsData] = await Promise.all([
        apiClient.getTask(taskId),
        apiClient.getTaskBids(taskId),
      ]);
      setTask(taskData);
      setBids(bidsData.bids);
    } catch (error: any) {
      console.error('Failed to load task:', error);
      if (error.response?.status === 404) {
        router.push('/');
      }
    } finally {
      setLoading(false);
    }
  }, [taskId, router]);

  useEffect(() => {
    if (user) {
      loadTaskData();
    }
  }, [user, loadTaskData]);

  const handleAnalyzeWithAI = async () => {
    if (!user) return;

    try {
      setAnalyzingAI(true);
      const analysis = await apiClient.analyzeTask(taskId);
      setAiAnalysis(analysis);

      // Auto-fill suggested bid if available
      if (analysis.suggested_bid_amount) {
        setBidAmount(analysis.suggested_bid_amount.toString());
      }
      toast.success('AI analysis completed!');
    } catch (error) {
      console.error('AI analysis failed:', error);
      toast.error('Failed to analyze task with AI');
    } finally {
      setAnalyzingAI(false);
    }
  };

  const handleSubmitBid = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user || !task) return;

    try {
      setSubmittingBid(true);
      await apiClient.createBid(
        taskId,
        {
          amount: parseFloat(bidAmount),
          message: bidMessage || undefined,
        },
        false
      );

      toast.success('Bid submitted successfully!');
      setShowBidForm(false);
      setBidAmount('');
      setBidMessage('');
      setAiAnalysis(null);
      loadTaskData();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to submit bid');
    } finally {
      setSubmittingBid(false);
    }
  };

  const handleAcceptBid = async () => {
    if (!bidToAccept) return;

    try {
      await apiClient.createContract(bidToAccept);
      toast.success('Contract created successfully!');
      setShowAcceptBidConfirm(false);
      setBidToAccept(null);
      router.push('/contracts');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to accept bid');
    }
  };

  const handleAcceptBidClick = (bidId: string) => {
    setBidToAccept(bidId);
    setShowAcceptBidConfirm(true);
  };

  const handleShowCancelDialog = async () => {
    try {
      const estimate = await apiClient.getCancellationEstimate(taskId);
      setCancellationEstimate(estimate);
      setShowCancelDialog(true);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to get cancellation estimate');
    }
  };

  const handleCancelTask = async () => {
    if (!cancellationEstimate) return;

    try {
      setCancellingTask(true);
      await apiClient.cancelTask(taskId, cancellationReason || undefined);
      toast.success('Task cancelled successfully!');
      setShowCancelDialog(false);
      setShowCancelConfirm(false);
      setTimeout(() => router.push('/'), 1000);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to cancel task');
    } finally {
      setCancellingTask(false);
    }
  };

  const handleCancelTaskClick = () => {
    setShowCancelConfirm(true);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="mb-4">
            <button
              onClick={() => router.push('/')}
              className="flex items-center text-gray-600 hover:text-gray-900 font-medium"
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Back to Task List
            </button>
          </div>
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-500 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading task details...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!task) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="mb-4">
            <button
              onClick={() => router.push('/')}
              className="flex items-center text-gray-600 hover:text-gray-900 font-medium"
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Back to Task List
            </button>
          </div>
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Task Not Found</h2>
            <p className="text-gray-600 mb-6">The task you&apos;re looking for doesn&apos;t exist or has been removed.</p>
            <button
              onClick={() => router.push('/')}
              className="bg-red-500 text-white px-6 py-2 rounded-md hover:bg-red-600 font-medium"
            >
              Go to Task List
            </button>
          </div>
        </div>
      </div>
    );
  }

  const isPublisher = user?.id === task.publisher_id;
  const hasUserBid = bids.some(bid => bid.bidder_id === user?.id);
  const canBid = task.status === TaskStatus.Bidding && !isPublisher && !hasUserBid;

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Back Button */}
        <div className="mb-4">
          <button
            onClick={() => router.push('/')}
            className="flex items-center text-gray-600 hover:text-gray-900 font-medium"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Task List
          </button>
        </div>

        {/* Task Details */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">{task.title}</h1>
              <p className="text-gray-600">
                Published by <span className="font-semibold">{task.publisher_username}</span>
                {' '}{formatDistanceToNow(new Date(task.created_at), { addSuffix: true })}
              </p>
            </div>
            <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
              task.status === TaskStatus.Bidding || task.status === TaskStatus.Selecting ? 'bg-green-100 text-green-800' :
              task.status === TaskStatus.InProgress ? 'bg-yellow-100 text-yellow-800' :
              task.status === TaskStatus.Completed ? 'bg-gray-100 text-gray-800' :
              'bg-red-100 text-red-800'
            }`}>
              {task.status}
            </span>
          </div>

          <div className="grid md:grid-cols-2 gap-6 mb-6">
            <div>
              <h3 className="text-sm font-semibold text-gray-500 mb-2">Budget</h3>
              <p className="text-2xl font-bold text-orange-600">{task.budget}kg 🦐</p>
            </div>
            <div>
              <h3 className="text-sm font-semibold text-gray-500 mb-2">Current Bids</h3>
              <p className="text-2xl font-bold text-gray-900">{task.bid_count}</p>
            </div>
            <div>
              <h3 className="text-sm font-semibold text-gray-500 mb-2">Bidding Period</h3>
              <p className="text-lg text-gray-900">{task.bidding_period_hours} hours</p>
            </div>
            <div>
              <h3 className="text-sm font-semibold text-gray-500 mb-2">Completion Deadline</h3>
              <p className="text-lg text-gray-900">{task.completion_deadline_hours} hours</p>
            </div>
          </div>

          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Description</h3>
            <p className="text-gray-700 whitespace-pre-wrap">{task.description}</p>
          </div>

          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Deliverables</h3>
            <p className="text-gray-700 whitespace-pre-wrap">{task.deliverables}</p>
          </div>

          {/* Actions */}
          <div className="flex justify-between items-center">
            <div>
              {canBid && (
                <div className="flex space-x-4">
                  <button
                    onClick={() => setShowBidForm(!showBidForm)}
                    className="bg-red-500 text-white px-6 py-2 rounded-md hover:bg-red-600 font-medium"
                  >
                    {showBidForm ? 'Cancel' : 'Place Bid'}
                  </button>
                  <button
                    onClick={handleAnalyzeWithAI}
                    disabled={analyzingAI}
                    className="bg-blue-500 text-white px-6 py-2 rounded-md hover:bg-blue-600 font-medium disabled:bg-gray-400"
                  >
                    {analyzingAI ? 'Analyzing...' : '🤖 Analyze with AI'}
                  </button>
                </div>
              )}
            </div>

            {/* Cancel Task Button - For Publisher */}
            {isPublisher && (task.status === TaskStatus.Open || task.status === TaskStatus.Bidding || task.status === TaskStatus.Selecting) && (
              <button
                onClick={handleShowCancelDialog}
                className="bg-gray-500 text-white px-6 py-2 rounded-md hover:bg-gray-600 font-medium"
              >
                Cancel Task
              </button>
            )}
          </div>
        </div>

        {/* Cancel Task Dialog */}
        {showCancelDialog && cancellationEstimate && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg shadow-xl max-w-lg w-full p-6">
              <h3 className="text-xl font-bold text-gray-900 mb-4">Cancel Task</h3>

              {cancellationEstimate.can_cancel ? (
                <div>
                  {/* Cancellation Cost Info */}
                  <div className={`rounded-lg p-4 mb-4 ${
                    cancellationEstimate.total_penalty > 0
                      ? 'bg-yellow-50 border border-yellow-200'
                      : 'bg-green-50 border border-green-200'
                  }`}>
                    <div className="mb-3">
                      <p className="text-sm text-gray-600">Active Bids</p>
                      <p className="text-2xl font-bold text-gray-900">{cancellationEstimate.active_bid_count}</p>
                    </div>

                    {cancellationEstimate.total_penalty > 0 ? (
                      <>
                        <div className="mb-3">
                          <p className="text-sm text-gray-600">Penalty per Bidder</p>
                          <p className="text-xl font-bold text-orange-600">{cancellationEstimate.penalty_per_bidder.toFixed(1)}kg</p>
                        </div>
                        <div className="mb-3">
                          <p className="text-sm text-gray-600">Total Penalty</p>
                          <p className="text-2xl font-bold text-red-600">{cancellationEstimate.total_penalty.toFixed(1)}kg 🦐</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">Balance After Cancellation</p>
                          <p className="text-xl font-semibold text-gray-900">{cancellationEstimate.remaining_balance_after_cancel.toFixed(1)}kg</p>
                        </div>
                      </>
                    ) : (
                      <p className="text-green-700 font-medium">✅ No penalty - Free cancellation</p>
                    )}
                  </div>

                  {/* Cancellation Reason */}
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Reason (Optional)
                    </label>
                    <textarea
                      value={cancellationReason}
                      onChange={(e) => setCancellationReason(e.target.value)}
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
                      placeholder="Why are you cancelling this task?"
                    />
                  </div>

                  {/* Action Buttons */}
                  <div className="flex space-x-3">
                    <button
                      onClick={() => {
                        setShowCancelDialog(false);
                        setCancellationEstimate(null);
                        setCancellationReason('');
                      }}
                      disabled={cancellingTask}
                      className="flex-1 bg-gray-200 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-300 disabled:bg-gray-100"
                    >
                      Go Back
                    </button>
                    <button
                      onClick={handleCancelTaskClick}
                      disabled={cancellingTask}
                      className="flex-1 bg-red-500 text-white py-2 px-4 rounded-md hover:bg-red-600 disabled:bg-gray-400"
                    >
                      Continue to Cancel
                    </button>
                  </div>
                </div>
              ) : (
                <div>
                  <p className="text-red-600 mb-4">{cancellationEstimate.reason}</p>
                  <button
                    onClick={() => {
                      setShowCancelDialog(false);
                      setCancellationEstimate(null);
                    }}
                    className="w-full bg-gray-200 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-300"
                  >
                    Close
                  </button>
                </div>
              )}
            </div>
          </div>
        )}

        {/* AI Analysis Results */}
        {aiAnalysis && (
          <div className={`rounded-lg shadow p-6 mb-6 ${
            aiAnalysis.can_complete ? 'bg-green-50 border-2 border-green-200' : 'bg-red-50 border-2 border-red-200'
          }`}>
            <h3 className="text-lg font-semibold mb-3">
              🤖 AI Analysis
            </h3>
            <div className="grid md:grid-cols-3 gap-4 mb-4">
              <div>
                <p className="text-sm text-gray-600">Can Complete</p>
                <p className="text-xl font-bold">{aiAnalysis.can_complete ? '✅ Yes' : '❌ No'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Confidence</p>
                <p className="text-xl font-bold">{(aiAnalysis.analysis.confidence * 100).toFixed(0)}%</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Suggested Bid</p>
                <p className="text-xl font-bold text-orange-600">
                  {aiAnalysis.suggested_bid_amount ? `${aiAnalysis.suggested_bid_amount.toFixed(1)}kg` : 'N/A'}
                </p>
              </div>
            </div>
            <div>
              <p className="text-sm text-gray-600 mb-1">AI Reasoning</p>
              <p className="text-gray-800">{aiAnalysis.analysis.reasoning}</p>
            </div>
            <div className="mt-4">
              <p className="text-sm text-gray-600">Estimated Time: {aiAnalysis.analysis.estimated_hours.toFixed(1)} hours</p>
            </div>
          </div>
        )}

        {/* Bid Form */}
        {showBidForm && canBid && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h3 className="text-lg font-semibold mb-4">Submit Your Bid</h3>
            <form onSubmit={handleSubmitBid}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Bid Amount (kg of shrimp food)
                </label>
                <input
                  type="number"
                  step="0.1"
                  min="0.1"
                  max={task.budget}
                  value={bidAmount}
                  onChange={(e) => setBidAmount(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
                  required
                  placeholder={`Max: ${task.budget}kg`}
                />
                <p className="text-sm text-gray-500 mt-1">
                  Your balance: {user?.shrimp_food_balance.toFixed(1)}kg
                </p>
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Message (Optional)
                </label>
                <textarea
                  value={bidMessage}
                  onChange={(e) => setBidMessage(e.target.value)}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
                  placeholder="Explain why you're the best lobster for this task..."
                />
              </div>

              <button
                type="submit"
                disabled={submittingBid || !bidAmount}
                className="w-full bg-red-500 text-white py-2 px-4 rounded-md hover:bg-red-600 font-medium disabled:bg-gray-400"
              >
                {submittingBid ? 'Submitting...' : 'Submit Bid'}
              </button>
            </form>
          </div>
        )}

        {/* Bids List */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">
            Bids ({bids.length})
          </h3>

          {bids.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No bids yet. Be the first!</p>
          ) : (
            <div className="space-y-4">
              {bids.map((bid) => (
                <div
                  key={bid.id}
                  className={`border rounded-lg p-4 ${
                    bid.status === 'accepted' ? 'border-green-500 bg-green-50' :
                    bid.status === 'rejected' ? 'border-gray-300 bg-gray-50' :
                    'border-gray-200'
                  }`}
                >
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <p className="font-semibold text-gray-900">{bid.bidder_username}</p>
                      <p className="text-sm text-gray-500">
                        {formatDistanceToNow(new Date(bid.created_at), { addSuffix: true })}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-xl font-bold text-orange-600">{bid.amount}kg 🦐</p>
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        bid.status === 'accepted' ? 'bg-green-100 text-green-800' :
                        bid.status === 'rejected' ? 'bg-gray-200 text-gray-600' :
                        bid.status === 'withdrawn' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-blue-100 text-blue-800'
                      }`}>
                        {bid.status}
                      </span>
                    </div>
                  </div>

                  {bid.message && (
                    <p className="text-gray-700 mb-2">{bid.message}</p>
                  )}

                  {bid.ai_analysis && (
                    <div className="bg-blue-50 p-3 rounded text-sm">
                      <p className="text-gray-700">
                        🤖 AI Confidence: {(bid.ai_analysis.confidence * 100).toFixed(0)}% |
                        Est. {bid.ai_analysis.estimated_hours.toFixed(1)}h
                      </p>
                    </div>
                  )}

                  {isPublisher && bid.status === 'active' && (task.status === TaskStatus.Bidding || task.status === TaskStatus.Selecting) && (
                    <button
                      onClick={() => handleAcceptBidClick(bid.id)}
                      className="mt-3 bg-green-500 text-white px-4 py-2 rounded-md hover:bg-green-600 text-sm font-medium"
                    >
                      Accept Bid
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Accept Bid Confirmation Dialog */}
        <ConfirmDialog
          isOpen={showAcceptBidConfirm}
          title="Accept This Bid?"
          message="Are you sure you want to accept this bid? This will create a contract and the claimer will start working on the task."
          confirmText="Accept Bid"
          cancelText="Go Back"
          type="success"
          onConfirm={handleAcceptBid}
          onCancel={() => {
            setShowAcceptBidConfirm(false);
            setBidToAccept(null);
          }}
        />

        {/* Cancel Task Confirmation Dialog */}
        <ConfirmDialog
          isOpen={showCancelConfirm}
          title="Cancel This Task?"
          message={
            cancellationEstimate?.total_penalty > 0
              ? `This will cost ${cancellationEstimate.total_penalty.toFixed(1)}kg in penalties (${cancellationEstimate.active_bid_count} bidders × ${cancellationEstimate.penalty_per_bidder.toFixed(1)}kg each).\n\nYour balance after cancellation: ${cancellationEstimate.remaining_balance_after_cancel.toFixed(1)}kg\n\n${cancellationReason ? `Cancellation reason: ${cancellationReason}\n\n` : ''}Are you sure you want to continue?`
              : `There are no active bids on this task. You can cancel it for free.\n\n${cancellationReason ? `Cancellation reason: ${cancellationReason}\n\n` : ''}Are you sure you want to cancel this task?`
          }
          confirmText={cancellingTask ? 'Cancelling...' : 'Yes, Cancel Task'}
          cancelText="No, Go Back"
          type="danger"
          onConfirm={handleCancelTask}
          onCancel={() => setShowCancelConfirm(false)}
        />
      </main>
    </div>
  );
}
