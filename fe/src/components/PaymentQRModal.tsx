'use client';

import { useEffect, useState } from 'react';
import QRCode from 'react-qr-code';
import { apiClient } from '@/lib/api';
import { PaymentMethod, RechargeStatus } from '@/types';

interface PaymentQRModalProps {
  isOpen: boolean;
  orderNo: string;
  qrCode?: string;
  paymentUrl?: string;
  paymentMethod: PaymentMethod;
  amountRmb: number;
  amountShrimp: number;
  onClose: () => void;
  onSuccess: () => void;
}

export default function PaymentQRModal({
  isOpen,
  orderNo,
  qrCode,
  paymentUrl,
  paymentMethod,
  amountRmb,
  amountShrimp,
  onClose,
  onSuccess,
}: PaymentQRModalProps) {
  const [status, setStatus] = useState<'pending' | 'success' | 'failed' | 'timeout'>('pending');
  const [timeLeft, setTimeLeft] = useState(300); // 5 minutes in seconds
  const [loading, setLoading] = useState(true);

  // Status polling
  useEffect(() => {
    if (!isOpen || status !== 'pending') return;

    setLoading(false);

    const pollStatus = async () => {
      try {
        const order = await apiClient.getRechargeOrder(orderNo);
        if (order.payment_status === RechargeStatus.Success) {
          setStatus('success');
          onSuccess();
          setTimeout(() => onClose(), 2000);
        } else if (order.payment_status === RechargeStatus.Failed) {
          setStatus('failed');
        }
      } catch (error) {
        console.error('Failed to poll order status:', error);
      }
    };

    const interval = setInterval(pollStatus, 3000);
    return () => clearInterval(interval);
  }, [isOpen, orderNo, status, onSuccess, onClose]);

  // Countdown timer
  useEffect(() => {
    if (!isOpen || status !== 'pending') return;

    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          setStatus('timeout');
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [isOpen, status]);

  // Reset state when modal opens
  useEffect(() => {
    if (isOpen) {
      setStatus('pending');
      setTimeLeft(300);
      setLoading(true);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleBackdropClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget && status !== 'success') {
      onClose();
    }
  };

  const handleOpenAlipay = () => {
    if (paymentUrl) {
      window.open(paymentUrl, '_blank');
    }
  };

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      onClick={handleBackdropClick}
    >
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
        {/* Header */}
        <div className="text-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            {paymentMethod === PaymentMethod.Wechat ? 'WeChat Pay' : 'Alipay'}
          </h2>
          <p className="text-gray-600">Scan to complete payment</p>
        </div>

        {/* Order Details */}
        <div className="bg-gray-50 rounded-lg p-4 mb-6">
          <div className="flex justify-between mb-2">
            <span className="text-gray-600">Order No:</span>
            <span className="font-mono text-sm">{orderNo}</span>
          </div>
          <div className="flex justify-between mb-2">
            <span className="text-gray-600">Amount:</span>
            <span className="font-bold text-lg text-red-600">¥{amountRmb.toFixed(2)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Shrimp Food:</span>
            <span className="font-bold text-orange-600">{amountShrimp.toFixed(1)} kg 🦐</span>
          </div>
        </div>

        {/* Content based on status */}
        {status === 'pending' && (
          <>
            {loading ? (
              <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
              </div>
            ) : (
              <>
                {/* QR Code for WeChat */}
                {paymentMethod === PaymentMethod.Wechat && qrCode && (
                  <div className="flex justify-center mb-6">
                    <div className="p-4 bg-white border-4 border-gray-200 rounded-lg">
                      <QRCode value={qrCode} size={256} />
                    </div>
                  </div>
                )}

                {/* Button for Alipay */}
                {paymentMethod === PaymentMethod.Alipay && paymentUrl && (
                  <div className="flex justify-center mb-6">
                    <button
                      onClick={handleOpenAlipay}
                      className="bg-blue-500 text-white px-8 py-4 rounded-lg text-lg font-bold hover:bg-blue-600 transition"
                    >
                      Open Alipay to Pay
                    </button>
                  </div>
                )}

                {/* Instructions */}
                <div className="text-center text-sm text-gray-600 mb-4">
                  {paymentMethod === PaymentMethod.Wechat
                    ? 'Open WeChat and scan the QR code to complete payment'
                    : 'Click the button above to open Alipay and complete payment'}
                </div>

                {/* Countdown Timer */}
                <div className="text-center mb-4">
                  <span className="text-gray-600">Time remaining: </span>
                  <span className="font-mono font-bold text-lg text-red-600">{formatTime(timeLeft)}</span>
                </div>
              </>
            )}
          </>
        )}

        {status === 'success' && (
          <div className="text-center py-8">
            <div className="text-6xl mb-4">✅</div>
            <h3 className="text-2xl font-bold text-green-600 mb-2">Payment Successful!</h3>
            <p className="text-gray-600">Your balance will be updated shortly...</p>
          </div>
        )}

        {status === 'failed' && (
          <div className="text-center py-8">
            <div className="text-6xl mb-4">❌</div>
            <h3 className="text-2xl font-bold text-red-600 mb-2">Payment Failed</h3>
            <p className="text-gray-600 mb-4">The payment could not be completed. Please try again.</p>
            <button
              onClick={onClose}
              className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600"
            >
              Try Again
            </button>
          </div>
        )}

        {status === 'timeout' && (
          <div className="text-center py-8">
            <div className="text-6xl mb-4">⏱️</div>
            <h3 className="text-2xl font-bold text-orange-600 mb-2">Payment Timeout</h3>
            <p className="text-gray-600 mb-4">The payment window has expired. Please create a new order.</p>
            <button
              onClick={onClose}
              className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600"
            >
              Create New Order
            </button>
          </div>
        )}

        {/* Cancel Button (only show for pending status) */}
        {status === 'pending' && !loading && (
          <div className="text-center">
            <button
              onClick={onClose}
              className="text-gray-600 hover:text-gray-800 text-sm underline"
            >
              Cancel
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
