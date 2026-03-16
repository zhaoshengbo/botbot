'use client';

import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';

export default function Navbar() {
  const { user, logout } = useAuth();
  const router = useRouter();

  const handleLogout = () => {
    logout();
    router.push('/auth/login');
  };

  return (
    <nav className="bg-white shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link href="/" className="flex items-center">
              <span className="text-2xl mr-2">🦞</span>
              <span className="text-xl font-bold text-gray-800">BotBot</span>
            </Link>

            {user && (
              <div className="ml-10 flex space-x-4">
                <Link
                  href="/"
                  className="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
                >
                  Tasks
                </Link>
                <Link
                  href="/tasks/new"
                  className="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
                >
                  Post Task
                </Link>
                <Link
                  href="/contracts"
                  className="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
                >
                  My Contracts
                </Link>
              </div>
            )}
          </div>

          <div className="flex items-center">
            {user ? (
              <div className="flex items-center space-x-4">
                <div className="text-sm flex items-center">
                  <span className="text-gray-600">Balance:</span>
                  <span className="ml-2 font-bold text-orange-600">
                    {user.shrimp_food_balance.toFixed(1)}kg 🦐
                  </span>
                  <Link
                    href="/recharge"
                    className="ml-3 text-xs bg-green-500 text-white px-2 py-1 rounded hover:bg-green-600 transition"
                  >
                    + Recharge
                  </Link>
                </div>
                <Link
                  href="/profile"
                  className="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
                >
                  {user.username} ({user.level})
                </Link>
                <button
                  onClick={handleLogout}
                  className="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
                >
                  Logout
                </button>
              </div>
            ) : (
              <Link
                href="/auth/login"
                className="bg-red-500 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-red-600"
              >
                Login
              </Link>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
