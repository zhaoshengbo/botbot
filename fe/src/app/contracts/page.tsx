'use client';

import { useEffect, useState, useCallback } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { apiClient } from '@/lib/api';
import type { Contract } from '@/types';
import Navbar from '@/components/Navbar';
import Link from 'next/link';
import { formatDistanceToNow } from 'date-fns';

export default function ContractsPage() {
  const { user } = useAuth();
  const [contracts, setContracts] = useState<Contract[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('');
  const [roleFilter, setRoleFilter] = useState<string>('');

  const loadContracts = useCallback(async () => {
    try {
      setLoading(true);
      const response = await apiClient.getContracts({
        status: filter || undefined,
        role: roleFilter || undefined,
      });
      setContracts(response.contracts);
    } catch (error) {
      console.error('Failed to load contracts:', error);
    } finally {
      setLoading(false);
    }
  }, [filter, roleFilter]);

  useEffect(() => {
    if (user) {
      loadContracts();
    }
  }, [user, loadContracts]);

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="text-center">Please login to view contracts</div>
        </div>
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-blue-100 text-blue-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'disputed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">My Contracts</h1>

        {/* Filters */}
        <div className="mb-6 flex flex-wrap gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Role</label>
            <div className="flex space-x-2">
              <button
                onClick={() => setRoleFilter('')}
                className={`px-4 py-2 rounded-md ${
                  roleFilter === '' ? 'bg-red-500 text-white' : 'bg-white text-gray-700 border'
                }`}
              >
                All
              </button>
              <button
                onClick={() => setRoleFilter('publisher')}
                className={`px-4 py-2 rounded-md ${
                  roleFilter === 'publisher' ? 'bg-red-500 text-white' : 'bg-white text-gray-700 border'
                }`}
              >
                As Publisher
              </button>
              <button
                onClick={() => setRoleFilter('claimer')}
                className={`px-4 py-2 rounded-md ${
                  roleFilter === 'claimer' ? 'bg-red-500 text-white' : 'bg-white text-gray-700 border'
                }`}
              >
                As Claimer
              </button>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
            <div className="flex space-x-2">
              <button
                onClick={() => setFilter('')}
                className={`px-4 py-2 rounded-md ${
                  filter === '' ? 'bg-red-500 text-white' : 'bg-white text-gray-700 border'
                }`}
              >
                All
              </button>
              <button
                onClick={() => setFilter('active')}
                className={`px-4 py-2 rounded-md ${
                  filter === 'active' ? 'bg-red-500 text-white' : 'bg-white text-gray-700 border'
                }`}
              >
                Active
              </button>
              <button
                onClick={() => setFilter('completed')}
                className={`px-4 py-2 rounded-md ${
                  filter === 'completed' ? 'bg-red-500 text-white' : 'bg-white text-gray-700 border'
                }`}
              >
                Completed
              </button>
            </div>
          </div>
        </div>

        {/* Contracts List */}
        {loading ? (
          <div className="text-center py-12">
            <div className="text-xl text-gray-600">Loading contracts...</div>
          </div>
        ) : contracts.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-xl text-gray-600 mb-4">No contracts found</div>
            <Link href="/marketplace" className="text-red-500 hover:text-red-600">
              Browse tasks to get started
            </Link>
          </div>
        ) : (
          <div className="grid gap-6">
            {contracts.map((contract) => {
              const isPublisher = contract.publisher_id === user.id;
              const role = isPublisher ? 'Publisher' : 'Claimer';
              const otherParty = isPublisher ? contract.claimer_username : contract.publisher_username;

              return (
                <Link
                  key={contract.id}
                  href={`/contracts/${contract.id}`}
                  className="block bg-white rounded-lg shadow hover:shadow-md transition-shadow p-6"
                >
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-1">
                        {contract.task_title}
                      </h3>
                      <p className="text-sm text-gray-600">
                        Your role: <span className="font-medium">{role}</span>
                        {' • '}
                        {isPublisher ? 'With' : 'For'}: <span className="font-medium">{otherParty}</span>
                      </p>
                    </div>
                    <span className={`px-3 py-1 text-sm rounded-full font-semibold ${getStatusColor(contract.status)}`}>
                      {contract.status}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <p className="text-gray-500">Amount</p>
                      <p className="font-semibold text-orange-600">{contract.amount}kg 🦐</p>
                    </div>
                    <div>
                      <p className="text-gray-500">Deliverables</p>
                      <p className="font-semibold">
                        {contract.deliverables_submitted ? '✅ Submitted' : '⏳ Pending'}
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-500">Created</p>
                      <p className="font-semibold">
                        {formatDistanceToNow(new Date(contract.created_at), { addSuffix: true })}
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-500">Status</p>
                      <p className="font-semibold capitalize">{contract.status}</p>
                    </div>
                  </div>

                  {/* Action needed indicators */}
                  {contract.status === 'active' && (
                    <div className="mt-4 pt-4 border-t border-gray-200">
                      {!isPublisher && !contract.deliverables_submitted && (
                        <p className="text-sm text-blue-600 font-medium">
                          ⚡ Action needed: Submit deliverables
                        </p>
                      )}
                      {isPublisher && contract.deliverables_submitted && (
                        <p className="text-sm text-blue-600 font-medium">
                          ⚡ Action needed: Review and approve deliverables
                        </p>
                      )}
                    </div>
                  )}
                </Link>
              );
            })}
          </div>
        )}
      </main>
    </div>
  );
}
