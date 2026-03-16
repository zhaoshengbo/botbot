'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { apiClient } from '@/lib/api';
import { PaymentMethod } from '@/types';
import PaymentQRModal from '@/components/PaymentQRModal';

export default function RechargePage() {
  const { user, loading: authLoading, refreshUser } = useAuth();
  const router = useRouter();

  const [amount, setAmount] = useState<number>(100);
  const [paymentMethod, setPaymentMethod] = useState<PaymentMethod>(PaymentMethod.Wechat);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Modal state
  const [modalData, setModalData] = useState<{
    isOpen: boolean;
    orderNo: string;
    qrCode?: string;
    paymentUrl?: string;
    paymentMethod: PaymentMethod;
    amountRmb: number;
    amountShrimp: number;
  }>({
    isOpen: false,
    orderNo: '',
    paymentMethod: PaymentMethod.Wechat,
    amountRmb: 0,
    amountShrimp: 0,
  });

  // Auth check
  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/auth/login');
    }
  }, [user, authLoading, router]);

  const validateAmount = (amount: number): string | null => {
    if (isNaN(amount) || amount <= 0) return 'Please enter a valid amount';
    if (amount < 1) return 'Minimum recharge amount is 1 RMB';
    if (amount > 50000) return 'Maximum recharge amount is 50,000 RMB';
    return null;
  };

  const handleQuickAmount = (value: number) => {
    setAmount(value);
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const validationError = validateAmount(amount);
    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.createRechargeOrder({
        amount_rmb: amount,
        payment_method: paymentMethod,
      });

      // Open QR modal with payment info
      setModalData({
        isOpen: true,
        orderNo: response.order.order_no,
        qrCode: response.payment_info.qr_code,
        paymentUrl: response.payment_info.payment_url,
        paymentMethod: paymentMethod,
        amountRmb: amount,
        amountShrimp: response.order.amount_shrimp,
      });
    } catch (err: any) {
      console.error('Failed to create recharge order:', err);
      setError(err.response?.data?.detail || 'Failed to create order. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleModalClose = () => {
    setModalData({ ...modalData, isOpen: false });
  };

  const handlePaymentSuccess = async () => {
    // Refresh user balance
    await refreshUser();
  };

  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Recharge Shrimp Food 🦐</h1>
          <p className="text-gray-600">Top up your account balance</p>
        </div>

        {/* Current Balance */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <div className="text-center">
            <p className="text-gray-600 mb-2">Current Balance</p>
            <p className="text-4xl font-bold text-orange-600">
              {user.shrimp_food_balance.toFixed(1)} kg 🦐
            </p>
          </div>
        </div>

        {/* Recharge Form */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <form onSubmit={handleSubmit}>
            {/* Amount Input */}
            <div className="mb-6">
              <label htmlFor="amount" className="block text-sm font-medium text-gray-700 mb-2">
                Recharge Amount (RMB)
              </label>
              <div className="relative">
                <span className="absolute left-3 top-3 text-gray-500 text-lg">¥</span>
                <input
                  type="number"
                  id="amount"
                  value={amount}
                  onChange={(e) => {
                    setAmount(parseFloat(e.target.value));
                    setError(null);
                  }}
                  className="w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
                  placeholder="Enter amount"
                  min="1"
                  max="50000"
                  step="1"
                />
              </div>
              {/* Conversion Display */}
              <p className="mt-2 text-sm text-gray-600">
                You will receive:{' '}
                <span className="font-bold text-orange-600">
                  {(amount * 10).toFixed(1)} kg shrimp food
                </span>
              </p>
            </div>

            {/* Quick Amount Buttons */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">Quick Select</label>
              <div className="grid grid-cols-4 gap-2">
                {[10, 50, 100, 500].map((value) => (
                  <button
                    key={value}
                    type="button"
                    onClick={() => handleQuickAmount(value)}
                    className={`py-2 px-4 rounded-lg border-2 font-medium transition ${
                      amount === value
                        ? 'border-blue-500 bg-blue-50 text-blue-700'
                        : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400'
                    }`}
                  >
                    ¥{value}
                  </button>
                ))}
              </div>
            </div>

            {/* Payment Method Selection */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-3">Payment Method</label>
              <div className="grid grid-cols-2 gap-4">
                {/* WeChat Pay */}
                <button
                  type="button"
                  onClick={() => setPaymentMethod(PaymentMethod.Wechat)}
                  className={`p-4 rounded-lg border-2 transition ${
                    paymentMethod === PaymentMethod.Wechat
                      ? 'border-green-500 bg-green-50'
                      : 'border-gray-300 bg-white hover:border-gray-400'
                  }`}
                >
                  <div className="text-3xl mb-2">💬</div>
                  <div className="font-medium text-gray-900">WeChat Pay</div>
                  <div className="text-xs text-gray-500">Scan QR code</div>
                </button>

                {/* Alipay */}
                <button
                  type="button"
                  onClick={() => setPaymentMethod(PaymentMethod.Alipay)}
                  className={`p-4 rounded-lg border-2 transition ${
                    paymentMethod === PaymentMethod.Alipay
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-300 bg-white hover:border-gray-400'
                  }`}
                >
                  <div className="text-3xl mb-2">💳</div>
                  <div className="font-medium text-gray-900">Alipay</div>
                  <div className="text-xs text-gray-500">Open in browser</div>
                </button>
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-red-800 text-sm">{error}</p>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className={`w-full py-4 rounded-lg font-bold text-lg transition ${
                loading
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-red-500 hover:bg-red-600 text-white'
              }`}
            >
              {loading ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                      fill="none"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    />
                  </svg>
                  Processing...
                </span>
              ) : (
                'Recharge Now'
              )}
            </button>
          </form>

          {/* Exchange Rate Info */}
          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <p className="text-xs text-gray-600 text-center">
              Exchange Rate: 1 RMB = 10 kg Shrimp Food 🦐
            </p>
          </div>
        </div>
      </div>

      {/* Payment QR Modal */}
      <PaymentQRModal
        isOpen={modalData.isOpen}
        orderNo={modalData.orderNo}
        qrCode={modalData.qrCode}
        paymentUrl={modalData.paymentUrl}
        paymentMethod={modalData.paymentMethod}
        amountRmb={modalData.amountRmb}
        amountShrimp={modalData.amountShrimp}
        onClose={handleModalClose}
        onSuccess={handlePaymentSuccess}
      />
    </div>
  );
}
