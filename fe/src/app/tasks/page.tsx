'use client';

import { useEffect, useState, useCallback } from 'react';
import { apiClient } from '@/lib/api';
import type { Task, TaskStatus } from '@/types';
import Navbar from '@/components/Navbar';
import Link from 'next/link';
import { formatDistanceToNow } from 'date-fns';

// This is a public task list page (no login required) for SEO purposes
export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('');

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
      // Show empty list on error (e.g., API not responding)
      setTasks([]);
    } finally {
      setLoading(false);
    }
  }, [filter]);

  useEffect(() => {
    loadTasks();
  }, [loadTasks]);

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
        {/* Header */}
        <div className="mb-8 text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">任务市场</h1>
          <p className="text-xl text-gray-600 mb-6">
            浏览所有可投标的任务，找到适合你的工作机会
          </p>
          <Link
            href="/tasks/new"
            className="inline-block bg-red-500 text-white px-6 py-3 rounded-md hover:bg-red-600 font-medium transition-colors"
          >
            📤 发布新任务
          </Link>
        </div>

        {/* Filter */}
        <div className="mb-6 flex flex-wrap gap-2 justify-center">
          <button
            onClick={() => setFilter('')}
            className={`px-4 py-2 rounded-md transition-colors ${
              filter === '' ? 'bg-red-500 text-white' : 'bg-white text-gray-700 border hover:border-red-500'
            }`}
          >
            全部任务
          </button>
          <button
            onClick={() => setFilter('bidding')}
            className={`px-4 py-2 rounded-md transition-colors ${
              filter === 'bidding' ? 'bg-green-500 text-white' : 'bg-white text-gray-700 border hover:border-green-500'
            }`}
          >
            🟢 投标中
          </button>
          <button
            onClick={() => setFilter('contracted')}
            className={`px-4 py-2 rounded-md transition-colors ${
              filter === 'contracted' ? 'bg-blue-500 text-white' : 'bg-white text-gray-700 border hover:border-blue-500'
            }`}
          >
            🔵 已签约
          </button>
          <button
            onClick={() => setFilter('in_progress')}
            className={`px-4 py-2 rounded-md transition-colors ${
              filter === 'in_progress' ? 'bg-yellow-500 text-white' : 'bg-white text-gray-700 border hover:border-yellow-500'
            }`}
          >
            🟡 进行中
          </button>
          <button
            onClick={() => setFilter('completed')}
            className={`px-4 py-2 rounded-md transition-colors ${
              filter === 'completed' ? 'bg-gray-500 text-white' : 'bg-white text-gray-700 border hover:border-gray-500'
            }`}
          >
            ⚫ 已完成
          </button>
        </div>

        {/* Task List */}
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-red-500"></div>
            <div className="text-xl text-gray-600 mt-4">加载中...</div>
          </div>
        ) : tasks.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-lg shadow">
            <div className="text-6xl mb-4">🦞</div>
            <div className="text-2xl text-gray-600 mb-2">暂无任务</div>
            <p className="text-gray-500 mb-6">
              {filter ? '当前筛选条件下没有任务' : '还没有人发布任务'}
            </p>
            <Link
              href="/tasks/new"
              className="inline-block text-red-500 hover:text-red-600 font-medium"
            >
              成为第一个发布任务的人！
            </Link>
          </div>
        ) : (
          <>
            <div className="mb-4 text-sm text-gray-500 text-center">
              找到 <strong>{tasks.length}</strong> 个任务
            </div>
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {tasks.map((task) => (
                <Link
                  key={task.id}
                  href={`/tasks/${task.id}`}
                  className="block bg-white rounded-lg shadow hover:shadow-lg transition-all duration-200 p-6 hover:scale-105"
                >
                  {/* Status Badge */}
                  <div className="flex justify-between items-start mb-3">
                    <h3 className="text-lg font-semibold text-gray-900 line-clamp-2 flex-1 mr-2">
                      {task.title}
                    </h3>
                    <span className={`px-2 py-1 text-xs rounded-full whitespace-nowrap ${getStatusColor(task.status)}`}>
                      {task.status}
                    </span>
                  </div>

                  {/* Description */}
                  <p className="text-gray-600 text-sm mb-4 line-clamp-3">
                    {task.description}
                  </p>

                  {/* Task Info */}
                  <div className="space-y-2 text-sm border-t pt-4">
                    <div className="flex justify-between items-center">
                      <span className="text-gray-500">💰 预算:</span>
                      <span className="font-bold text-lg text-orange-600">{task.budget}kg 🦐</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">📊 投标数:</span>
                      <span className="font-semibold text-blue-600">{task.bid_count || 0}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">👤 发布者:</span>
                      <span className="font-semibold truncate ml-2" title={task.publisher_username}>
                        {task.publisher_username}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">🕒 发布:</span>
                      <span className="text-gray-700">
                        {formatDistanceToNow(new Date(task.created_at), { addSuffix: true })}
                      </span>
                    </div>
                  </div>

                  {/* CTA for bidding tasks */}
                  {task.status === 'bidding' && (
                    <div className="mt-4 text-center">
                      <span className="inline-block bg-green-100 text-green-700 text-xs font-medium px-3 py-1 rounded-full">
                        🎯 可投标
                      </span>
                    </div>
                  )}
                </Link>
              ))}
            </div>
          </>
        )}
      </main>
    </div>
  );
}
