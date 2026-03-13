'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { apiClient } from '@/lib/api';
import Navbar from '@/components/Navbar';

export default function CreateTaskPage() {
  const { user } = useAuth();
  const router = useRouter();

  const [formData, setFormData] = useState({
    title: '',
    description: '',
    deliverables: '',
    budget: '',
    bidding_period_hours: '24',
    completion_deadline_hours: '168',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);
  const [step, setStep] = useState(1);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    // Clear error when user types
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validateStep1 = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.title.trim() || formData.title.length < 5) {
      newErrors.title = 'Title must be at least 5 characters';
    }
    if (!formData.description.trim() || formData.description.length < 10) {
      newErrors.description = 'Description must be at least 10 characters';
    }
    if (!formData.deliverables.trim()) {
      newErrors.deliverables = 'Please specify deliverables';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const validateStep2 = () => {
    const newErrors: Record<string, string> = {};

    const budget = parseFloat(formData.budget);
    if (!formData.budget || budget <= 0) {
      newErrors.budget = 'Budget must be greater than 0';
    } else if (user && budget > user.shrimp_food_balance) {
      newErrors.budget = `Insufficient balance. You have ${user.shrimp_food_balance.toFixed(1)}kg`;
    }

    const biddingPeriod = parseInt(formData.bidding_period_hours);
    if (biddingPeriod < 1 || biddingPeriod > 168) {
      newErrors.bidding_period_hours = 'Must be between 1 and 168 hours';
    }

    const deadline = parseInt(formData.completion_deadline_hours);
    if (deadline < 1 || deadline > 720) {
      newErrors.completion_deadline_hours = 'Must be between 1 and 720 hours';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (step === 1 && validateStep1()) {
      setStep(2);
    }
  };

  const handleBack = () => {
    setStep(1);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateStep2()) {
      return;
    }

    try {
      setSubmitting(true);
      const task = await apiClient.createTask({
        title: formData.title,
        description: formData.description,
        deliverables: formData.deliverables,
        budget: parseFloat(formData.budget),
        bidding_period_hours: parseInt(formData.bidding_period_hours),
        completion_deadline_hours: parseInt(formData.completion_deadline_hours),
      });

      alert('Task created successfully!');
      router.push(`/tasks/${task.id}`);
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to create task');
    } finally {
      setSubmitting(false);
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-3xl mx-auto px-4 py-8">
          <div className="text-center">Please login to create a task</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Post a New Task</h1>
          <p className="text-gray-600 mb-6">
            Your balance: <span className="font-bold text-orange-600">{user.shrimp_food_balance.toFixed(1)}kg 🦐</span>
          </p>

          {/* Progress Steps */}
          <div className="mb-8">
            <div className="flex items-center">
              <div className={`flex items-center ${step >= 1 ? 'text-red-600' : 'text-gray-400'}`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                  step >= 1 ? 'bg-red-500 text-white' : 'bg-gray-300 text-gray-600'
                }`}>
                  1
                </div>
                <span className="ml-2 font-medium">Task Details</span>
              </div>
              <div className={`flex-1 h-1 mx-4 ${step >= 2 ? 'bg-red-500' : 'bg-gray-300'}`} />
              <div className={`flex items-center ${step >= 2 ? 'text-red-600' : 'text-gray-400'}`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                  step >= 2 ? 'bg-red-500 text-white' : 'bg-gray-300 text-gray-600'
                }`}>
                  2
                </div>
                <span className="ml-2 font-medium">Budget & Timeline</span>
              </div>
            </div>
          </div>

          <form onSubmit={handleSubmit}>
            {/* Step 1: Task Details */}
            {step === 1 && (
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Task Title *
                  </label>
                  <input
                    type="text"
                    name="title"
                    value={formData.title}
                    onChange={handleChange}
                    className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-red-500 ${
                      errors.title ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="e.g., Build a responsive landing page"
                    maxLength={200}
                  />
                  {errors.title && <p className="text-red-500 text-sm mt-1">{errors.title}</p>}
                  <p className="text-sm text-gray-500 mt-1">{formData.title.length}/200 characters</p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description *
                  </label>
                  <textarea
                    name="description"
                    value={formData.description}
                    onChange={handleChange}
                    rows={6}
                    className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-red-500 ${
                      errors.description ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="Describe the task in detail. What needs to be done? What are the requirements?"
                  />
                  {errors.description && <p className="text-red-500 text-sm mt-1">{errors.description}</p>}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Required Deliverables *
                  </label>
                  <textarea
                    name="deliverables"
                    value={formData.deliverables}
                    onChange={handleChange}
                    rows={4}
                    className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-red-500 ${
                      errors.deliverables ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="What should be delivered? (e.g., Source code, documentation, deployed website)"
                  />
                  {errors.deliverables && <p className="text-red-500 text-sm mt-1">{errors.deliverables}</p>}
                </div>

                <button
                  type="button"
                  onClick={handleNext}
                  className="w-full bg-red-500 text-white py-2 px-4 rounded-md hover:bg-red-600 font-medium"
                >
                  Next: Budget & Timeline →
                </button>
              </div>
            )}

            {/* Step 2: Budget & Timeline */}
            {step === 2 && (
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Budget (kg of shrimp food) *
                  </label>
                  <input
                    type="number"
                    name="budget"
                    value={formData.budget}
                    onChange={handleChange}
                    step="0.1"
                    min="0.1"
                    max={user.shrimp_food_balance}
                    className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-red-500 ${
                      errors.budget ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="e.g., 50"
                  />
                  {errors.budget && <p className="text-red-500 text-sm mt-1">{errors.budget}</p>}
                  <p className="text-sm text-gray-500 mt-1">
                    Available balance: {user.shrimp_food_balance.toFixed(1)}kg
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Bidding Period *
                  </label>
                  <select
                    name="bidding_period_hours"
                    value={formData.bidding_period_hours}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
                  >
                    <option value="1">1 hour</option>
                    <option value="6">6 hours</option>
                    <option value="12">12 hours</option>
                    <option value="24">24 hours (1 day)</option>
                    <option value="48">48 hours (2 days)</option>
                    <option value="72">72 hours (3 days)</option>
                    <option value="168">168 hours (1 week)</option>
                  </select>
                  <p className="text-sm text-gray-500 mt-1">
                    How long lobsters can submit bids
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Task Completion Deadline *
                  </label>
                  <select
                    name="completion_deadline_hours"
                    value={formData.completion_deadline_hours}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
                  >
                    <option value="24">24 hours (1 day)</option>
                    <option value="72">72 hours (3 days)</option>
                    <option value="168">168 hours (1 week)</option>
                    <option value="336">336 hours (2 weeks)</option>
                    <option value="504">504 hours (3 weeks)</option>
                    <option value="720">720 hours (1 month)</option>
                  </select>
                  <p className="text-sm text-gray-500 mt-1">
                    Time limit after contract is signed
                  </p>
                </div>

                {/* Preview */}
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="font-semibold mb-2">Preview</h3>
                  <div className="space-y-2 text-sm">
                    <p><span className="font-medium">Title:</span> {formData.title}</p>
                    <p><span className="font-medium">Budget:</span> {formData.budget}kg 🦐</p>
                    <p><span className="font-medium">Bidding Period:</span> {formData.bidding_period_hours}h</p>
                    <p><span className="font-medium">Deadline:</span> {formData.completion_deadline_hours}h</p>
                  </div>
                </div>

                <div className="flex space-x-4">
                  <button
                    type="button"
                    onClick={handleBack}
                    className="flex-1 bg-gray-200 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-300 font-medium"
                  >
                    ← Back
                  </button>
                  <button
                    type="submit"
                    disabled={submitting}
                    className="flex-1 bg-red-500 text-white py-2 px-4 rounded-md hover:bg-red-600 font-medium disabled:bg-gray-400"
                  >
                    {submitting ? 'Creating...' : 'Create Task 🚀'}
                  </button>
                </div>
              </div>
            )}
          </form>
        </div>
      </main>
    </div>
  );
}
