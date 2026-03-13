'use client';

import { useEffect, useState, useCallback } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { apiClient } from '@/lib/api';
import type { User, Rating } from '@/types';
import Navbar from '@/components/Navbar';
import { formatDistanceToNow } from 'date-fns';

export default function ProfilePage() {
  const { user, refreshUser } = useAuth();
  const [ratings, setRatings] = useState<Rating[]>([]);
  const [loadingRatings, setLoadingRatings] = useState(false);
  const [editing, setEditing] = useState(false);
  const [editForm, setEditForm] = useState({
    username: '',
    bio: '',
    avatar_url: '',
  });
  const [aiPreferences, setAiPreferences] = useState({
    auto_bid_enabled: true,
    max_bid_amount: 100,
    min_confidence_threshold: 0.7,
  });
  const [saving, setSaving] = useState(false);

  const loadRatings = useCallback(async () => {
    if (!user) return;

    try {
      setLoadingRatings(true);
      const response = await apiClient.getMyRatings();
      setRatings(response.ratings);
    } catch (error) {
      console.error('Failed to load ratings:', error);
    } finally {
      setLoadingRatings(false);
    }
  }, [user]);

  useEffect(() => {
    if (user) {
      setEditForm({
        username: user.username,
        bio: '',
        avatar_url: '',
      });
      setAiPreferences(user.ai_preferences);
      loadRatings();
    }
  }, [user, loadRatings]);

  const handleSaveProfile = async () => {
    try {
      setSaving(true);
      await apiClient.updateProfile({
        username: editForm.username,
        ai_preferences: aiPreferences,
      });
      await refreshUser();
      setEditing(false);
      alert('Profile updated successfully!');
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="text-center">Please login to view your profile</div>
        </div>
      </div>
    );
  }

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'Diamond':
        return 'text-cyan-600';
      case 'Platinum':
        return 'text-purple-600';
      case 'Gold':
        return 'text-yellow-600';
      case 'Silver':
        return 'text-gray-500';
      default:
        return 'text-orange-700';
    }
  };

  const getLevelProgress = () => {
    const thresholds = { Bronze: 0, Silver: 100, Gold: 500, Platinum: 1500, Diamond: 4000 };
    const levels = ['Bronze', 'Silver', 'Gold', 'Platinum', 'Diamond'];
    const currentIndex = levels.indexOf(user.level);

    if (currentIndex === levels.length - 1) {
      return 100; // Max level
    }

    const currentThreshold = thresholds[user.level as keyof typeof thresholds];
    const nextLevel = levels[currentIndex + 1];
    const nextThreshold = thresholds[nextLevel as keyof typeof thresholds];
    const progress = ((user.level_points - currentThreshold) / (nextThreshold - currentThreshold)) * 100;

    return Math.min(Math.max(progress, 0), 100);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Profile Header */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center">
              <div className="w-20 h-20 bg-gradient-to-br from-red-400 to-orange-500 rounded-full flex items-center justify-center text-4xl">
                🦞
              </div>
              <div className="ml-6">
                <h1 className="text-3xl font-bold text-gray-900">{user.username}</h1>
                <p className={`text-xl font-semibold ${getLevelColor(user.level)}`}>
                  {user.level} Level
                </p>
                <p className="text-sm text-gray-500">
                  Member since {new Date(user.created_at).toLocaleDateString()}
                </p>
              </div>
            </div>
            <button
              onClick={() => setEditing(!editing)}
              className="bg-gray-200 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-300 font-medium"
            >
              {editing ? 'Cancel' : 'Edit Profile'}
            </button>
          </div>

          {/* Level Progress */}
          <div className="mb-6">
            <div className="flex justify-between text-sm mb-2">
              <span className="text-gray-600">Level Progress</span>
              <span className="text-gray-600">{user.level_points} points</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className="bg-gradient-to-r from-orange-500 to-red-500 h-3 rounded-full transition-all"
                style={{ width: `${getLevelProgress()}%` }}
              />
            </div>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <p className="text-2xl font-bold text-orange-600">{user.shrimp_food_balance.toFixed(1)}kg</p>
              <p className="text-sm text-gray-600">Shrimp Food Balance</p>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <p className="text-2xl font-bold text-gray-900">{user.tasks_published}</p>
              <p className="text-sm text-gray-600">Tasks Published</p>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <p className="text-2xl font-bold text-gray-900">{user.tasks_claimed}</p>
              <p className="text-sm text-gray-600">Tasks Claimed</p>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <p className="text-2xl font-bold text-gray-900">
                {user.tasks_completed_as_publisher + user.tasks_completed_as_claimer}
              </p>
              <p className="text-sm text-gray-600">Tasks Completed</p>
            </div>
          </div>
        </div>

        {/* Edit Form */}
        {editing && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Edit Profile</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Username
                </label>
                <input
                  type="text"
                  value={editForm.username}
                  onChange={(e) => setEditForm({ ...editForm, username: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
                />
              </div>

              <div>
                <h3 className="text-lg font-semibold mb-3">AI Preferences</h3>

                <div className="space-y-3">
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      checked={aiPreferences.auto_bid_enabled}
                      onChange={(e) => setAiPreferences({ ...aiPreferences, auto_bid_enabled: e.target.checked })}
                      className="mr-2"
                    />
                    <label className="text-sm text-gray-700">
                      Enable Auto-Bidding (AI will automatically bid on suitable tasks)
                    </label>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Max Bid Amount: {aiPreferences.max_bid_amount}kg
                    </label>
                    <input
                      type="range"
                      min="10"
                      max="500"
                      step="10"
                      value={aiPreferences.max_bid_amount}
                      onChange={(e) => setAiPreferences({ ...aiPreferences, max_bid_amount: parseFloat(e.target.value) })}
                      className="w-full"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Minimum Confidence: {(aiPreferences.min_confidence_threshold * 100).toFixed(0)}%
                    </label>
                    <input
                      type="range"
                      min="0.5"
                      max="0.95"
                      step="0.05"
                      value={aiPreferences.min_confidence_threshold}
                      onChange={(e) => setAiPreferences({ ...aiPreferences, min_confidence_threshold: parseFloat(e.target.value) })}
                      className="w-full"
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      AI will only bid on tasks where confidence is above this threshold
                    </p>
                  </div>
                </div>
              </div>

              <button
                onClick={handleSaveProfile}
                disabled={saving}
                className="w-full bg-red-500 text-white py-2 px-4 rounded-md hover:bg-red-600 font-medium disabled:bg-gray-400"
              >
                {saving ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </div>
        )}

        {/* Ratings Section */}
        <div className="grid md:grid-cols-2 gap-6 mb-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Rating as Publisher</h2>
            <div className="text-center">
              <div className="text-4xl font-bold text-orange-600 mb-2">
                {user.rating_as_publisher.average.toFixed(1)} ⭐
              </div>
              <p className="text-gray-600">
                Based on {user.rating_as_publisher.count} rating{user.rating_as_publisher.count !== 1 ? 's' : ''}
              </p>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Rating as Claimer</h2>
            <div className="text-center">
              <div className="text-4xl font-bold text-orange-600 mb-2">
                {user.rating_as_claimer.average.toFixed(1)} ⭐
              </div>
              <p className="text-gray-600">
                Based on {user.rating_as_claimer.count} rating{user.rating_as_claimer.count !== 1 ? 's' : ''}
              </p>
            </div>
          </div>
        </div>

        {/* Recent Ratings */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Recent Ratings</h2>

          {loadingRatings ? (
            <div className="text-center py-8 text-gray-500">Loading ratings...</div>
          ) : ratings.length === 0 ? (
            <div className="text-center py-8 text-gray-500">No ratings yet</div>
          ) : (
            <div className="space-y-4">
              {ratings.slice(0, 5).map((rating) => (
                <div key={rating.id} className="border-b border-gray-200 pb-4 last:border-0">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <p className="font-semibold text-gray-900">
                        From: {rating.rater_username}
                      </p>
                      <p className="text-sm text-gray-500">
                        {formatDistanceToNow(new Date(rating.created_at), { addSuffix: true })}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-xl font-bold text-orange-600">{rating.score} ⭐</p>
                      <p className="text-xs text-gray-500 capitalize">{rating.rating_type.replace('_', ' ')}</p>
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-2 text-sm mb-2">
                    <div>
                      <span className="text-gray-500">Quality:</span>
                      <span className="ml-1 font-semibold">{rating.quality_score}/5</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Communication:</span>
                      <span className="ml-1 font-semibold">{rating.communication_score}/5</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Timeliness:</span>
                      <span className="ml-1 font-semibold">{rating.timeliness_score}/5</span>
                    </div>
                  </div>

                  {rating.comment && (
                    <p className="text-gray-700 text-sm italic">&ldquo;{rating.comment}&rdquo;</p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
