// API Client for BotBot Backend
import axios, { AxiosInstance } from 'axios';
import type {
  AuthTokens,
  User,
  Task,
  TaskListResponse,
  Bid,
  BidListResponse,
  Contract,
  ContractListResponse,
  Rating,
  RatingListResponse,
  AnalyzeTaskResponse,
  PaymentMethod,
  RechargeCreateResponse,
  RechargeOrder,
} from '@/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: `${API_URL}/api`,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor to attach token
    this.client.interceptors.request.use((config) => {
      const token = this.getToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Add response interceptor to handle token refresh
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          // Token expired, try to refresh
          const refreshToken = this.getRefreshToken();
          if (refreshToken) {
            try {
              const { data } = await axios.post(`${API_URL}/api/auth/refresh`, {
                refresh_token: refreshToken,
              });
              this.setToken(data.access_token);
              // Retry original request
              error.config.headers.Authorization = `Bearer ${data.access_token}`;
              return this.client.request(error.config);
            } catch (refreshError) {
              // Refresh failed, clear tokens
              this.clearTokens();
              window.location.href = '/auth/login';
            }
          }
        }
        return Promise.reject(error);
      }
    );
  }

  // Token management
  getToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('access_token');
  }

  getRefreshToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('refresh_token');
  }

  setToken(token: string) {
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', token);
    }
  }

  setRefreshToken(token: string) {
    if (typeof window !== 'undefined') {
      localStorage.setItem('refresh_token', token);
    }
  }

  clearTokens() {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  }

  // Auth APIs
  async sendVerificationCode(phone_number: string) {
    const { data } = await this.client.post('/auth/send-code', { phone_number });
    return data;
  }

  async verifyCode(phone_number: string, verification_code: string): Promise<AuthTokens> {
    const { data } = await this.client.post('/auth/verify-code', {
      phone_number,
      verification_code,
    });
    this.setToken(data.access_token);
    this.setRefreshToken(data.refresh_token);
    return data;
  }

  async directLogin(phone_number: string): Promise<AuthTokens> {
    const { data } = await this.client.post('/auth/direct-login', {
      phone_number,
    });
    this.setToken(data.access_token);
    this.setRefreshToken(data.refresh_token);
    return data;
  }

  async getCurrentUser(): Promise<User> {
    const { data } = await this.client.get('/auth/me');
    return data;
  }

  async logout() {
    this.clearTokens();
  }

  // User APIs
  async getUser(userId: string): Promise<User> {
    const { data } = await this.client.get(`/users/${userId}`);
    return data;
  }

  async updateProfile(updates: Partial<User>): Promise<User> {
    const { data } = await this.client.patch('/users/me', updates);
    return data;
  }

  async getBalance() {
    const { data } = await this.client.get('/users/me/balance');
    return data;
  }

  // Task APIs
  async createTask(taskData: {
    title: string;
    description: string;
    deliverables: string;
    budget: number;
    bidding_period_hours: number;
    completion_deadline_hours: number;
  }): Promise<Task> {
    const { data } = await this.client.post('/tasks', taskData);
    return data;
  }

  async getTasks(params?: {
    status?: string;
    publisher_id?: string;
    page?: number;
    page_size?: number;
  }): Promise<TaskListResponse> {
    const { data } = await this.client.get('/tasks', { params });
    return data;
  }

  async getTask(taskId: string): Promise<Task> {
    const { data } = await this.client.get(`/tasks/${taskId}`);
    return data;
  }

  async updateTask(taskId: string, updates: Partial<Task>): Promise<Task> {
    const { data } = await this.client.patch(`/tasks/${taskId}`, updates);
    return data;
  }

  async getCancellationEstimate(taskId: string): Promise<{
    can_cancel: boolean;
    reason: string;
    active_bid_count: number;
    penalty_per_bidder: number;
    total_penalty: number;
    remaining_balance_after_cancel: number;
  }> {
    const { data } = await this.client.get(`/tasks/${taskId}/cancellation-estimate`);
    return data;
  }

  async cancelTask(taskId: string, cancellation_reason?: string): Promise<Task> {
    const { data } = await this.client.delete(`/tasks/${taskId}`, {
      params: { cancellation_reason },
    });
    return data;
  }

  async getMyTasks(params?: {
    status?: string;
    page?: number;
    page_size?: number;
  }): Promise<TaskListResponse> {
    const { data } = await this.client.get('/tasks/my/tasks', { params });
    return data;
  }

  // AI APIs
  async analyzeTask(taskId: string): Promise<AnalyzeTaskResponse> {
    const { data } = await this.client.post('/ai/analyze-task', { task_id: taskId });
    return data;
  }

  // Bid APIs
  async createBid(
    taskId: string,
    bidData: { amount: number; message?: string },
    useAI: boolean = false
  ): Promise<Bid> {
    const { data } = await this.client.post('/bids/', {
      task_id: taskId,
      ...bidData,
    }, {
      params: { use_ai: useAI },
    });
    return data;
  }

  async getTaskBids(taskId: string): Promise<BidListResponse> {
    const { data } = await this.client.get(`/tasks/${taskId}/bids`);
    // Backend returns { bids: [], total: number }
    return data;
  }

  async getMyBids(status?: string): Promise<BidListResponse> {
    const { data } = await this.client.get('/bids/my-bids', { params: { status } });
    return data;
  }

  async withdrawBid(bidId: string): Promise<Bid> {
    const { data } = await this.client.delete(`/bids/${bidId}`);
    return data;
  }

  // Contract APIs
  async acceptBid(bidId: string): Promise<{ message: string; contract_id: string; bid_id: string }> {
    const { data } = await this.client.post(`/bids/${bidId}/accept`);
    return data;
  }

  async createContract(bidId: string): Promise<Contract> {
    const { data } = await this.client.post('/contracts', { bid_id: bidId });
    return data;
  }

  async getContracts(params?: {
    role?: string;
    status?: string;
  }): Promise<ContractListResponse> {
    const { data } = await this.client.get('/contracts', { params });
    return data;
  }

  async getContract(contractId: string): Promise<Contract> {
    const { data } = await this.client.get(`/contracts/${contractId}`);
    return data;
  }

  async submitDeliverables(contractId: string, deliverablesUrl: string, notes?: string): Promise<Contract> {
    const { data } = await this.client.post(`/contracts/${contractId}/submit`, {
      deliverable_url: deliverablesUrl,
      notes,
    });
    return data;
  }

  async completeContract(
    contractId: string,
    approved: boolean,
    rejectionReason?: string
  ): Promise<Contract> {
    const { data } = await this.client.post(`/contracts/${contractId}/complete`, {
      approved,
      rejection_reason: rejectionReason,
    });
    return data;
  }

  // Rating APIs
  async createRating(ratingData: {
    contract_id: string;
    score: number;
    quality_score: number;
    communication_score: number;
    timeliness_score: number;
    comment?: string;
  }): Promise<Rating> {
    const { data } = await this.client.post('/ratings', ratingData);
    return data;
  }

  async getUserRatings(userId: string, ratingType?: string): Promise<RatingListResponse> {
    const { data } = await this.client.get(`/ratings/users/${userId}/ratings`, {
      params: { rating_type: ratingType },
    });
    return data;
  }

  async getMyRatings(ratingType?: string): Promise<RatingListResponse> {
    const { data } = await this.client.get('/ratings/my-ratings', {
      params: { rating_type: ratingType },
    });
    return data;
  }

  // Payment APIs
  async createRechargeOrder(data: {
    amount_rmb: number;
    payment_method: PaymentMethod;
  }): Promise<RechargeCreateResponse> {
    const { data: response } = await this.client.post('/payment/recharge/create', data);
    return response;
  }

  async getRechargeOrder(orderNo: string): Promise<RechargeOrder> {
    const { data } = await this.client.get(`/payment/recharge/${orderNo}`);
    return data;
  }

  // Arbitration APIs
  async createArbitration(data: {
    contract_id: string;
    requester_role: 'publisher' | 'claimer';
    reason: string;
    evidence_urls?: string[];
  }): Promise<any> {
    const { data: response } = await this.client.post('/arbitration', data);
    return response;
  }

  async getMyArbitrations(page: number = 1, page_size: number = 20): Promise<any> {
    const { data } = await this.client.get('/arbitration/my-cases', {
      params: { page, page_size },
    });
    return data;
  }

  async getArbitrationDetails(arbitrationId: string): Promise<any> {
    const { data } = await this.client.get(`/arbitration/${arbitrationId}`);
    return data;
  }
}

export const apiClient = new APIClient();
