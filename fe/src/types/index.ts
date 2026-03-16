// Type definitions for BotBot frontend

export enum UserLevel {
  Bronze = "Bronze",
  Silver = "Silver",
  Gold = "Gold",
  Platinum = "Platinum",
  Diamond = "Diamond",
}

export enum TaskStatus {
  Open = "open",
  Bidding = "bidding",
  Contracted = "contracted",
  InProgress = "in_progress",
  Completed = "completed",
  Cancelled = "cancelled",
}

export enum BidStatus {
  Active = "active",
  Accepted = "accepted",
  Rejected = "rejected",
  Withdrawn = "withdrawn",
}

export enum ContractStatus {
  Active = "active",
  Completed = "completed",
  Disputed = "disputed",
}

export interface User {
  id: string;
  phone_number: string;
  username: string;
  email?: string;
  phone_verified: boolean;
  shrimp_food_balance: number;
  shrimp_food_frozen: number;
  level: UserLevel;
  level_points: number;
  tasks_published: number;
  tasks_completed_as_publisher: number;
  tasks_claimed: number;
  tasks_completed_as_claimer: number;
  rating_as_publisher: RatingInfo;
  rating_as_claimer: RatingInfo;
  ai_preferences: AIPreferences;
  created_at: string;
}

export interface RatingInfo {
  average: number;
  count: number;
  total: number;
}

export interface AIPreferences {
  auto_bid_enabled: boolean;
  max_bid_amount: number;
  min_confidence_threshold: number;
}

export interface Task {
  id: string;
  publisher_id: string;
  publisher_username?: string;
  title: string;
  description: string;
  deliverables: string;
  budget: number;
  bidding_period_hours: number;
  completion_deadline_hours: number;
  status: TaskStatus;
  created_at: string;
  bidding_ends_at?: string;
  deadline_at?: string;
  view_count: number;
  bid_count: number;
}

export interface Bid {
  id: string;
  task_id: string;
  bidder_id: string;
  bidder_username?: string;
  amount: number;
  message?: string;
  ai_analysis?: AIAnalysis;
  status: BidStatus;
  created_at: string;
}

export interface AIAnalysis {
  feasibility_score: number;
  estimated_hours: number;
  confidence: number;
  reasoning: string;
}

export interface Contract {
  id: string;
  task_id: string;
  task_title?: string;
  publisher_id: string;
  publisher_username?: string;
  publisher_email?: string;
  claimer_id: string;
  claimer_username?: string;
  amount: number;
  status: ContractStatus;
  deliverables_submitted: boolean;
  deliverables_url?: string;
  deliverables_submitted_at?: string;
  completed_at?: string;
  created_at: string;
}

export interface Rating {
  id: string;
  contract_id: string;
  task_id: string;
  rater_id: string;
  rater_username?: string;
  ratee_id: string;
  ratee_username?: string;
  rating_type: string;
  score: number;
  quality_score: number;
  communication_score: number;
  timeliness_score: number;
  comment?: string;
  created_at: string;
}

// API Response types
export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user_id: string;
}

export interface TaskListResponse {
  tasks: Task[];
  total: number;
  page: number;
  page_size: number;
}

export interface BidListResponse {
  bids: Bid[];
  total: number;
}

export interface ContractListResponse {
  contracts: Contract[];
  total: number;
}

export interface RatingListResponse {
  ratings: Rating[];
  total: number;
}

export interface AnalyzeTaskResponse {
  can_complete: boolean;
  suggested_bid_amount?: number;
  analysis: AIAnalysis;
  should_bid: boolean;
}

// Payment enums
export enum PaymentMethod {
  Alipay = "alipay",
  Wechat = "wechat",
}

export enum RechargeStatus {
  Pending = "pending",
  Success = "success",
  Failed = "failed",
  Cancelled = "cancelled",
}

// Payment interfaces
export interface RechargeCreateRequest {
  amount_rmb: number;
  payment_method: PaymentMethod;
}

export interface RechargeCreateResponse {
  success: boolean;
  order: {
    order_no: string;
    amount_rmb: number;
    amount_shrimp: number;
    status: RechargeStatus;
  };
  payment_info: {
    order_no: string;
    payment_method: string;
    payment_url?: string;  // Alipay
    qr_code?: string;      // WeChat code_url
  };
}

export interface RechargeOrder {
  id: string;
  order_no: string;
  amount_rmb: number;
  amount_shrimp: number;
  payment_status: RechargeStatus;
  payment_time?: string;
  created_at: string;
}
