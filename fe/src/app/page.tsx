'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { apiClient } from '@/lib/api';
import type { Task, TaskStatus } from '@/types';
import Navbar from '@/components/Navbar';
import Link from 'next/link';
import { formatDistanceToNow } from 'date-fns';

export default function Home() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('');

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/auth/login');
    }
  }, [authLoading, user, router]);

  const loadTasks = useCallback(async () => {
    try {
      setLoading(true);
      const response = await apiClient.getTasks({
        status: filter || undefined,
        page: 1,
        page_size: 20,
      });
      setTasks(response.tasks);
    } catch (error) {
      console.error('Failed to load tasks:', error);
    } finally {
      setLoading(false);
    }
  }, [filter]);

  useEffect(() => {
    if (user) {
      loadTasks();
    }
  }, [user, loadTasks]);

  if (authLoading || !user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading...</div>
      </div>
    );
  }

  const getStatusColor = (status: TaskStatus) => {
    switch (status) {
      case 'bidding':
        return 'bg-green-100 text-green-800';
      case 'contracted':
        return 'bg-blue-100 text-blue-800';
      case 'in_progress':
        return 'bg-yellow-100 text-yellow-800';
      case 'completed':
        return 'bg-gray-100 text-gray-800';
      case 'cancelled':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6 flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900">Task Marketplace</h1>
          <Link
            href="/tasks/new"
            className="bg-red-500 text-white px-4 py-2 rounded-md hover:bg-red-600 font-medium"
          >
            + Post New Task
          </Link>
        </div>

        {/* Filter */}
        <div className="mb-6 flex space-x-2">
          <button
            onClick={() => setFilter('')}
            className={`px-4 py-2 rounded-md ${
              filter === '' ? 'bg-red-500 text-white' : 'bg-white text-gray-700 border'
            }`}
          >
            All
          </button>
          <button
            onClick={() => setFilter('bidding')}
            className={`px-4 py-2 rounded-md ${
              filter === 'bidding' ? 'bg-red-500 text-white' : 'bg-white text-gray-700 border'
            }`}
          >
            Bidding
          </button>
          <button
            onClick={() => setFilter('in_progress')}
            className={`px-4 py-2 rounded-md ${
              filter === 'in_progress' ? 'bg-red-500 text-white' : 'bg-white text-gray-700 border'
            }`}
          >
            In Progress
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

        {/* Task List */}
        {loading ? (
          <div className="text-center py-12">
            <div className="text-xl text-gray-600">Loading tasks...</div>
          </div>
        ) : tasks.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-xl text-gray-600">No tasks found</div>
            <Link
              href="/tasks/new"
              className="mt-4 inline-block text-red-500 hover:text-red-600"
            >
              Be the first to post a task!
            </Link>
          </div>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {tasks.map((task) => (
              <Link
                key={task.id}
                href={`/tasks/${task.id}`}
                className="block bg-white rounded-lg shadow hover:shadow-md transition-shadow p-6"
              >
                <div className="flex justify-between items-start mb-2">
                  <h3 className="text-lg font-semibold text-gray-900 line-clamp-2">
                    {task.title}
                  </h3>
                  <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(task.status)}`}>
                    {task.status}
                  </span>
                </div>

                <p className="text-gray-600 text-sm mb-4 line-clamp-3">{task.description}</p>

                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-500">Budget:</span>
                    <span className="font-semibold text-orange-600">{task.budget}kg 🦐</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Bids:</span>
                    <span className="font-semibold">{task.bid_count}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Publisher:</span>
                    <span className="font-semibold">{task.publisher_username}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Posted:</span>
                    <span>{formatDistanceToNow(new Date(task.created_at), { addSuffix: true })}</span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
