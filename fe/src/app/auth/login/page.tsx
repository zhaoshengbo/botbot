'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { apiClient } from '@/lib/api';

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [phoneNumber, setPhoneNumber] = useState('');
  const [verificationCode, setVerificationCode] = useState('');
  const [step, setStep] = useState<'phone' | 'code'>('phone');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [countdown, setCountdown] = useState(0);

  const handleSendCode = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await apiClient.sendVerificationCode(phoneNumber);
      setStep('code');
      setCountdown(60);
      const timer = setInterval(() => {
        setCountdown((prev) => {
          if (prev <= 1) {
            clearInterval(timer);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to send verification code');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyCode = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(phoneNumber, verificationCode);
      router.push('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid verification code');
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

        {step === 'phone' ? (
          <form onSubmit={handleSendCode}>
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
            </div>

            {error && (
              <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading || !phoneNumber}
              className="w-full bg-red-500 text-white font-bold py-2 px-4 rounded-md hover:bg-red-600 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {loading ? 'Sending...' : 'Send Verification Code'}
            </button>
          </form>
        ) : (
          <form onSubmit={handleVerifyCode}>
            <div className="mb-4">
              <label className="block text-gray-700 text-sm font-bold mb-2">
                Verification Code
              </label>
              <input
                type="text"
                value={verificationCode}
                onChange={(e) => setVerificationCode(e.target.value)}
                placeholder="Enter 6-digit code"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
                required
                disabled={loading}
                maxLength={6}
              />
              <p className="text-sm text-gray-600 mt-2">
                Code sent to {phoneNumber}
              </p>
            </div>

            {error && (
              <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading || !verificationCode}
              className="w-full bg-red-500 text-white font-bold py-2 px-4 rounded-md hover:bg-red-600 disabled:bg-gray-400 disabled:cursor-not-allowed mb-2"
            >
              {loading ? 'Verifying...' : 'Login / Register'}
            </button>

            <button
              type="button"
              onClick={() => countdown === 0 && handleSendCode({ preventDefault: () => {} } as any)}
              disabled={countdown > 0 || loading}
              className="w-full bg-gray-200 text-gray-700 font-bold py-2 px-4 rounded-md hover:bg-gray-300 disabled:bg-gray-100 disabled:cursor-not-allowed"
            >
              {countdown > 0 ? `Resend in ${countdown}s` : 'Resend Code'}
            </button>

            <button
              type="button"
              onClick={() => {
                setStep('phone');
                setVerificationCode('');
                setError('');
              }}
              className="w-full mt-2 text-gray-600 hover:text-gray-800"
            >
              Change Phone Number
            </button>
          </form>
        )}

        <div className="mt-6 text-center text-sm text-gray-600">
          <p>By logging in, you agree to our Terms of Service</p>
          <p className="mt-2">New lobsters get 100kg of shrimp food! 🦐</p>
        </div>
      </div>
    </div>
  );
}
