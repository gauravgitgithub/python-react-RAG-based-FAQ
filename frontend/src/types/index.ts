// User types
export interface User {
  id: number;
  email: string;
  username: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export enum UserRole {
  ADMIN = 'admin',
  EDITOR = 'editor',
  VIEWER = 'viewer'
}

// Authentication types
export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
  role?: UserRole;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

// Document types
export interface Document {
  id: number;
  filename: string;
  original_filename: string;
  file_path: string;
  file_size: number;
  file_type: string;
  is_active: boolean;
  uploaded_by: number;
  created_at: string;
  updated_at?: string;
}

export interface DocumentChunk {
  id: number;
  document_id: number;
  chunk_index: number;
  content: string;
  start_char: number;
  end_char: number;
  embedding_id: string;
  created_at: string;
}

export interface DocumentListResponse {
  documents: Document[];
  total: number;
  page: number;
  size: number;
}

export interface DocumentSelectionRequest {
  document_ids: number[];
  is_active: boolean;
}

// Q&A types
export interface QuestionRequest {
  question: string;
  top_k?: number;
}

export interface SourceChunk {
  content: string;
  document_name: string;
  chunk_index: number;
  similarity_score: number;
}

export interface AnswerResponse {
  answer: string;
  sources: SourceChunk[];
  question: string;
}

// API Response types
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface ApiError {
  detail: string;
  error_code?: string;
  timestamp?: string;
}

// UI types
export interface LoadingState {
  isLoading: boolean;
  error?: string;
}

export interface UploadProgress {
  loaded: number;
  total: number;
  percentage: number;
} 