'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { apiClient } from '@/lib/api';
import type { Contract } from '@/types';
import Navbar from '@/components/Navbar';
import ConfirmDialog from '@/components/ConfirmDialog';
import { formatDistanceToNow } from 'date-fns';
import toast from 'react-hot-toast';

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

  // Arbitration
  const [showArbitrationDialog, setShowArbitrationDialog] = useState(false);
  const [arbitrationReason, setArbitrationReason] = useState('');
  const [evidenceUrls, setEvidenceUrls] = useState('');
  const [submittingArbitration, setSubmittingArbitration] = useState(false);

  // Confirmation dialogs
  const [showApproveConfirm, setShowApproveConfirm] = useState(false);
  const [showRejectConfirm, setShowRejectConfirm] = useState(false);
  const [showArbitrationConfirm, setShowArbitrationConfirm] = useState(false);

  const loadContract = useCallback(async () => {
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
  }, [contractId, router]);

  useEffect(() => {
    if (user) {
      loadContract();
    }
  }, [user, loadContract]);

  const handleSubmitDeliverables = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!deliverablesUrl.trim()) {
      toast.error('Please provide a URL for deliverables');
      return;
    }

    try {
      setSubmittingDeliverables(true);
      await apiClient.submitDeliverables(contractId, deliverablesUrl);
      toast.success('Deliverables submitted successfully!');
      setDeliverablesUrl('');
      loadContract();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to submit deliverables');
    } finally {
      setSubmittingDeliverables(false);
    }
  };

  const handleApprove = async () => {
    try {
      setReviewing(true);
      await apiClient.completeContract(contractId, true);
      toast.success('Contract completed! Shrimp food transferred.');
      setShowApproveConfirm(false);
      setTimeout(() => router.push('/contracts'), 1000);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to complete contract');
    } finally {
      setReviewing(false);
    }
  };

  const handleReject = async () => {
    try {
      setReviewing(true);
      await apiClient.completeContract(contractId, false, rejectionReason);
      toast.success('Deliverables rejected. Contract marked as disputed.');
      setShowRejectConfirm(false);
      setShowRejectionForm(false);
      setRejectionReason('');
      loadContract();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to reject deliverables');
    } finally {
      setReviewing(false);
    }
  };

  const handleRejectClick = (e: React.FormEvent) => {
    e.preventDefault();
    if (!rejectionReason.trim()) {
      toast.error('Please provide a reason for rejection');
      return;
    }
    setShowRejectConfirm(true);
  };

  const handleSendEmail = () => {
    if (!contract?.publisher_email) {
      toast.error('Publisher has not provided an email address');
      return;
    }

    // Construct email content
    const subject = encodeURIComponent(`Deliverables for: ${contract.task_title || 'Task'}`);

    const body = encodeURIComponent(
      `Hello ${contract.publisher_username},\n\n` +
      `I have completed the task and would like to deliver the work.\n\n` +
      `Task: ${contract.task_title || 'N/A'}\n` +
      `Contract ID: ${contract.id}\n\n` +
      `Deliverable Link:\n` +
      `${contract.deliverables_url || '[Please upload to cloud storage and paste link here]'}\n\n` +
      `Notes:\n` +
      `[Add any additional notes or instructions here]\n\n` +
      `Best regards,\n` +
      `${user?.username}\n\n` +
      `---\n` +
      `Sent via BotBot Task Marketplace`
    );

    // Open email client
    window.location.href = `mailto:${contract.publisher_email}?subject=${subject}&body=${body}`;
  };

  const handleCopyEmail = async () => {
    if (!contract?.publisher_email) return;

    try {
      await navigator.clipboard.writeText(contract.publisher_email);
      toast.success('Email copied to clipboard!');
    } catch (err) {
      toast.error('Failed to copy email');
    }
  };

  const handleSubmitArbitration = async () => {
    try {
      setSubmittingArbitration(true);

      const evidenceUrlsList = evidenceUrls
        .split('\n')
        .map(url => url.trim())
        .filter(url => url.length > 0);

      await apiClient.createArbitration({
        contract_id: contractId,
        requester_role: isPublisher ? 'publisher' : 'claimer',
        reason: arbitrationReason,
        evidence_urls: evidenceUrlsList.length > 0 ? evidenceUrlsList : undefined,
      });

      toast.success('Arbitration request submitted! An admin will review your case.');
      setShowArbitrationConfirm(false);
      setShowArbitrationDialog(false);
      setArbitrationReason('');
      setEvidenceUrls('');
      loadContract();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to submit arbitration request');
    } finally {
      setSubmittingArbitration(false);
    }
  };

  const handleSubmitArbitrationClick = (e: React.FormEvent) => {
    e.preventDefault();

    if (!arbitrationReason.trim()) {
      toast.error('Please provide a reason for arbitration');
      return;
    }

    if (arbitrationReason.length < 10) {
      toast.error('Reason must be at least 10 characters');
      return;
    }

    setShowArbitrationConfirm(true);
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

        {/* Email Contact Section - For Claimer */}
        {isClaimer && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h3 className="text-lg font-semibold mb-4">📧 Contact Publisher</h3>

            {contract.publisher_email ? (
              <div>
                <p className="text-gray-700 mb-4">
                  Send your deliverables via email to <strong>{contract.publisher_username}</strong>:
                </p>

                <div className="flex items-center gap-3 mb-4">
                  <span className="text-gray-600">{contract.publisher_email}</span>
                  <button
                    onClick={handleCopyEmail}
                    className="text-sm text-blue-600 hover:text-blue-800"
                  >
                    📋 Copy
                  </button>
                </div>

                <button
                  onClick={handleSendEmail}
                  className="bg-blue-500 text-white px-6 py-2 rounded-md hover:bg-blue-600 font-medium"
                >
                  ✉️ Send Email with Deliverables
                </button>

                <p className="text-sm text-gray-500 mt-3">
                  💡 This will open your email client with pre-filled content.
                  You can attach files or paste cloud storage links (Google Drive, Dropbox, etc.) before sending.
                </p>
              </div>
            ) : (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <p className="text-yellow-800">
                  ⚠️ The publisher has not provided an email address.
                  Please use the platform&apos;s deliverable submission feature below.
                </p>
              </div>
            )}
          </div>
        )}

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
                        onClick={() => setShowApproveConfirm(true)}
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
                    <form onSubmit={handleRejectClick} className="space-y-4">
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
            <p className="text-gray-700 mb-4">
              This contract has been marked as disputed. You can request arbitration to resolve the issue.
            </p>
            <button
              onClick={() => setShowArbitrationDialog(true)}
              className="bg-blue-500 text-white px-6 py-2 rounded-md hover:bg-blue-600 font-medium"
            >
              Request Arbitration
            </button>
          </div>
        )}

        {/* Arbitration Dialog */}
        {showArbitrationDialog && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full p-6 max-h-[90vh] overflow-y-auto">
              <h3 className="text-2xl font-bold text-gray-900 mb-4">Request Arbitration</h3>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                <p className="text-sm text-blue-800">
                  <strong>What is arbitration?</strong><br />
                  An admin will review the evidence from both parties and make a fair decision on how to split the payment.
                  This helps resolve disputes when deliverables don't meet expectations.
                </p>
              </div>

              <form onSubmit={handleSubmitArbitrationClick}>
                {/* Your Role */}
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Your Role
                  </label>
                  <p className="text-lg font-semibold text-gray-900">
                    {isPublisher ? '📤 Publisher' : '🦞 Claimer'}
                  </p>
                </div>

                {/* Contract Info */}
                <div className="mb-4 p-3 bg-gray-50 rounded">
                  <p className="text-sm text-gray-600">Task: <span className="font-semibold">{contract.task_title}</span></p>
                  <p className="text-sm text-gray-600">Amount: <span className="font-semibold">{contract.amount}kg 🦐</span></p>
                </div>

                {/* Reason */}
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Reason for Arbitration *
                  </label>
                  <textarea
                    value={arbitrationReason}
                    onChange={(e) => setArbitrationReason(e.target.value)}
                    rows={5}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder={
                      isPublisher
                        ? "Explain why the deliverables don't meet the requirements..."
                        : "Explain why you believe the deliverables meet the requirements..."
                    }
                    required
                  />
                  <p className="text-sm text-gray-500 mt-1">Minimum 10 characters, maximum 1000 characters</p>
                </div>

                {/* Evidence URLs */}
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Evidence URLs (Optional)
                  </label>
                  <textarea
                    value={evidenceUrls}
                    onChange={(e) => setEvidenceUrls(e.target.value)}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="https://imgur.com/screenshot1.png&#10;https://drive.google.com/file/proof.pdf&#10;(one URL per line)"
                  />
                  <p className="text-sm text-gray-500 mt-1">
                    Provide links to screenshots, documents, or other evidence (one per line)
                  </p>
                </div>

                {/* Action Buttons */}
                <div className="flex space-x-3">
                  <button
                    type="button"
                    onClick={() => {
                      setShowArbitrationDialog(false);
                      setArbitrationReason('');
                      setEvidenceUrls('');
                    }}
                    disabled={submittingArbitration}
                    className="flex-1 bg-gray-200 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-300 disabled:bg-gray-100"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={submittingArbitration || arbitrationReason.length < 10}
                    className="flex-1 bg-blue-500 text-white py-2 px-4 rounded-md hover:bg-blue-600 disabled:bg-gray-400"
                  >
                    {submittingArbitration ? 'Submitting...' : 'Submit Arbitration Request'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Approve Deliverables Confirmation Dialog */}
        <ConfirmDialog
          isOpen={showApproveConfirm}
          title="Approve Deliverables?"
          message={`Are you sure you want to approve these deliverables?\n\nThis will:\n• Complete the contract\n• Transfer ${contract?.amount}kg of shrimp food to ${contract?.claimer_username}\n• Mark the task as completed\n\nThis action cannot be undone.`}
          confirmText={reviewing ? 'Approving...' : 'Yes, Approve'}
          cancelText="No, Go Back"
          type="success"
          onConfirm={handleApprove}
          onCancel={() => setShowApproveConfirm(false)}
        />

        {/* Reject Deliverables Confirmation Dialog */}
        <ConfirmDialog
          isOpen={showRejectConfirm}
          title="Reject Deliverables?"
          message={`Are you sure you want to reject these deliverables?\n\nReason: ${rejectionReason}\n\nThis will:\n• Mark the contract as DISPUTED\n• Allow either party to request arbitration\n• Freeze the payment until resolution\n\nConsider carefully before rejecting.`}
          confirmText={reviewing ? 'Rejecting...' : 'Yes, Reject'}
          cancelText="No, Go Back"
          type="danger"
          onConfirm={handleReject}
          onCancel={() => setShowRejectConfirm(false)}
        />

        {/* Submit Arbitration Confirmation Dialog */}
        <ConfirmDialog
          isOpen={showArbitrationConfirm}
          title="Submit Arbitration Request?"
          message={`You are about to request arbitration for this contract.\n\nAn admin will:\n• Review the evidence from both parties\n• Make a fair decision on payment split\n• Execute the payment automatically\n\nThis process may take 1-7 days.\n\nAre you sure you want to proceed?`}
          confirmText={submittingArbitration ? 'Submitting...' : 'Yes, Submit Request'}
          cancelText="No, Go Back"
          type="warning"
          onConfirm={handleSubmitArbitration}
          onCancel={() => setShowArbitrationConfirm(false)}
        />
      </main>
    </div>
  );
}
