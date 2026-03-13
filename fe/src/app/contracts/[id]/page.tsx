'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { apiClient } from '@/lib/api';
import type { Contract } from '@/types';
import Navbar from '@/components/Navbar';
import { formatDistanceToNow } from 'date-fns';

export default function ContractDetailPage() {
  const params = useParams();
  const contractId = params.id as string;
  const { user } = useAuth();
  const router = useRouter();

  const [contract, setContract] = useState<Contract | null>(null);
  const [loading, setLoading] = useState(true);
  const [deliverablesUrl, setDeliverablesUrl] = useState('');
  const [submittingDeliverables, setSubmittingDeliverables] = useState(false);
  const [reviewing, setReviewing] = useState(false);
  const [rejectionReason, setRejectionReason] = useState('');
  const [showRejectionForm, setShowRejectionForm] = useState(false);

  useEffect(() => {
    if (user) {
      loadContract();
    }
  }, [user, contractId]);

  const loadContract = async () => {
    try {
      setLoading(true);
      const contractData = await apiClient.getContract(contractId);
      setContract(contractData);
    } catch (error: any) {
      console.error('Failed to load contract:', error);
      if (error.response?.status === 404 || error.response?.status === 403) {
        router.push('/contracts');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitDeliverables = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!deliverablesUrl.trim()) {
      alert('Please provide a URL for deliverables');
      return;
    }

    try {
      setSubmittingDeliverables(true);
      await apiClient.submitDeliverables(contractId, deliverablesUrl);
      alert('Deliverables submitted successfully!');
      setDeliverablesUrl('');
      loadContract();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to submit deliverables');
    } finally {
      setSubmittingDeliverables(false);
    }
  };

  const handleApprove = async () => {
    if (!confirm('Are you sure you want to approve these deliverables? This will complete the contract and transfer the shrimp food.')) {
      return;
    }

    try {
      setReviewing(true);
      await apiClient.completeContract(contractId, true);
      alert('Contract completed! Shrimp food transferred.');
      router.push('/contracts');
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to complete contract');
    } finally {
      setReviewing(false);
    }
  };

  const handleReject = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!rejectionReason.trim()) {
      alert('Please provide a reason for rejection');
      return;
    }

    if (!confirm('Are you sure you want to reject these deliverables? This will mark the contract as disputed.')) {
      return;
    }

    try {
      setReviewing(true);
      await apiClient.completeContract(contractId, false, rejectionReason);
      alert('Deliverables rejected. Contract marked as disputed.');
      loadContract();
      setShowRejectionForm(false);
      setRejectionReason('');
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to reject deliverables');
    } finally {
      setReviewing(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-4xl mx-auto px-4 py-8">
          <div className="text-center">Loading...</div>
        </div>
      </div>
    );
  }

  if (!contract) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-4xl mx-auto px-4 py-8">
          <div className="text-center">Contract not found</div>
        </div>
      </div>
    );
  }

  const isPublisher = user?.id === contract.publisher_id;
  const isClaimer = user?.id === contract.claimer_id;

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Contract Header */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">{contract.task_title}</h1>
              <p className="text-gray-600">
                Your role: <span className="font-semibold">{isPublisher ? 'Publisher' : 'Claimer'}</span>
              </p>
            </div>
            <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
              contract.status === 'active' ? 'bg-blue-100 text-blue-800' :
              contract.status === 'completed' ? 'bg-green-100 text-green-800' :
              'bg-red-100 text-red-800'
            }`}>
              {contract.status}
            </span>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-sm font-semibold text-gray-500 mb-2">Contract Amount</h3>
              <p className="text-2xl font-bold text-orange-600">{contract.amount}kg 🦐</p>
            </div>
            <div>
              <h3 className="text-sm font-semibold text-gray-500 mb-2">Created</h3>
              <p className="text-lg text-gray-900">
                {formatDistanceToNow(new Date(contract.created_at), { addSuffix: true })}
              </p>
            </div>
            <div>
              <h3 className="text-sm font-semibold text-gray-500 mb-2">Publisher</h3>
              <p className="text-lg text-gray-900">{contract.publisher_username}</p>
            </div>
            <div>
              <h3 className="text-sm font-semibold text-gray-500 mb-2">Claimer</h3>
              <p className="text-lg text-gray-900">{contract.claimer_username}</p>
            </div>
          </div>
        </div>

        {/* Deliverables Section */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Deliverables</h2>

          {contract.deliverables_submitted ? (
            <div>
              <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
                <div className="flex items-center mb-2">
                  <span className="text-green-600 text-xl mr-2">✅</span>
                  <span className="font-semibold text-green-800">Deliverables Submitted</span>
                </div>
                <p className="text-sm text-gray-600">
                  Submitted {formatDistanceToNow(new Date(contract.deliverables_submitted_at!), { addSuffix: true })}
                </p>
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Deliverables URL
                </label>
                <a
                  href={contract.deliverables_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800 underline break-all"
                >
                  {contract.deliverables_url}
                </a>
              </div>

              {/* Publisher Review Actions */}
              {isPublisher && contract.status === 'active' && (
                <div className="space-y-4">
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                    <p className="text-yellow-800 font-medium">
                      ⚡ Action Required: Please review the deliverables
                    </p>
                  </div>

                  {!showRejectionForm ? (
                    <div className="flex space-x-4">
                      <button
                        onClick={handleApprove}
                        disabled={reviewing}
                        className="flex-1 bg-green-500 text-white py-3 px-4 rounded-md hover:bg-green-600 font-medium disabled:bg-gray-400"
                      >
                        ✅ Approve & Complete
                      </button>
                      <button
                        onClick={() => setShowRejectionForm(true)}
                        disabled={reviewing}
                        className="flex-1 bg-red-500 text-white py-3 px-4 rounded-md hover:bg-red-600 font-medium disabled:bg-gray-400"
                      >
                        ❌ Reject
                      </button>
                    </div>
                  ) : (
                    <form onSubmit={handleReject} className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Reason for Rejection *
                        </label>
                        <textarea
                          value={rejectionReason}
                          onChange={(e) => setRejectionReason(e.target.value)}
                          rows={4}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
                          placeholder="Please explain why you are rejecting the deliverables..."
                          required
                        />
                      </div>
                      <div className="flex space-x-4">
                        <button
                          type="button"
                          onClick={() => setShowRejectionForm(false)}
                          className="flex-1 bg-gray-200 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-300"
                        >
                          Cancel
                        </button>
                        <button
                          type="submit"
                          disabled={reviewing}
                          className="flex-1 bg-red-500 text-white py-2 px-4 rounded-md hover:bg-red-600 disabled:bg-gray-400"
                        >
                          Confirm Rejection
                        </button>
                      </div>
                    </form>
                  )}
                </div>
              )}
            </div>
          ) : (
            <div>
              {isClaimer && contract.status === 'active' ? (
                <form onSubmit={handleSubmitDeliverables} className="space-y-4">
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                    <p className="text-blue-800 font-medium">
                      ⚡ Action Required: Submit your deliverables
                    </p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Deliverables URL *
                    </label>
                    <input
                      type="url"
                      value={deliverablesUrl}
                      onChange={(e) => setDeliverablesUrl(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
                      placeholder="https://github.com/username/repo or https://drive.google.com/..."
                      required
                    />
                    <p className="text-sm text-gray-500 mt-1">
                      Provide a link to your completed work (GitHub, Google Drive, etc.)
                    </p>
                  </div>

                  <button
                    type="submit"
                    disabled={submittingDeliverables}
                    className="w-full bg-red-500 text-white py-3 px-4 rounded-md hover:bg-red-600 font-medium disabled:bg-gray-400"
                  >
                    {submittingDeliverables ? 'Submitting...' : 'Submit Deliverables'}
                  </button>
                </form>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <p>⏳ Waiting for deliverables to be submitted</p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Completed Status */}
        {contract.status === 'completed' && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-6">
            <div className="flex items-center mb-2">
              <span className="text-green-600 text-2xl mr-3">🎉</span>
              <h3 className="text-lg font-bold text-green-800">Contract Completed!</h3>
            </div>
            <p className="text-gray-700">
              This contract was completed {formatDistanceToNow(new Date(contract.completed_at!), { addSuffix: true })}
            </p>
            <p className="text-gray-700 mt-2">
              {contract.amount}kg of shrimp food was transferred from {contract.publisher_username} to {contract.claimer_username}.
            </p>
          </div>
        )}

        {/* Disputed Status */}
        {contract.status === 'disputed' && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <div className="flex items-center mb-2">
              <span className="text-red-600 text-2xl mr-3">⚠️</span>
              <h3 className="text-lg font-bold text-red-800">Contract Disputed</h3>
            </div>
            <p className="text-gray-700">
              This contract has been marked as disputed. Please contact support for resolution.
            </p>
          </div>
        )}
      </main>
    </div>
  );
}
