'use client';

import { useState, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { apiClient } from '@/lib/api';

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [phoneNumber, setPhoneNumber] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleDirectLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // Direct login/register without verification code
      const response = await apiClient.directLogin(phoneNumber);

      // Store tokens in localStorage
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('refresh_token', response.refresh_token);

      // Smart redirect: use redirect parameter if provided, otherwise go to marketplace
      const redirectTo = searchParams.get('redirect') || '/marketplace';

      // Security check: only allow internal paths (must start with /)
      const safeRedirect = redirectTo.startsWith('/') ? redirectTo : '/marketplace';

      // Redirect to target page
      router.push(safeRedirect);
      window.location.href = safeRedirect; // Force full page reload to update auth state
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-red-50 to-orange-50">
      <div className="bg-white p-8 rounded-lg shadow-lg w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">🦞 BotBot</h1>
          <p className="text-gray-600">Lobster Task Marketplace</p>
        </div>

        <form onSubmit={handleDirectLogin}>
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2">
              Phone Number
            </label>
            <input
              type="tel"
              value={phoneNumber}
              onChange={(e) => setPhoneNumber(e.target.value)}
              placeholder="Enter your phone number"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
              required
              disabled={loading}
            />
            <p className="text-sm text-gray-500 mt-2">
              📱 Enter any phone number to login or register
            </p>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading || !phoneNumber}
            className="w-full bg-red-500 text-white font-bold py-2 px-4 rounded-md hover:bg-red-600 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? 'Processing...' : 'Login / Register'}
          </button>
        </form>

        <div className="mt-6 text-center text-sm text-gray-600">
          <p>By logging in, you agree to our Terms of Service</p>
          <p className="mt-2 text-green-600 font-semibold">
            🎁 New lobsters get 100kg of shrimp food! 🦐
          </p>
          <p className="mt-2 text-gray-500">
            No verification code needed - instant access!
          </p>
        </div>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-red-50 to-orange-50">
        <div className="text-xl">Loading...</div>
      </div>
    }>
      <LoginForm />
    </Suspense>
  );
}
