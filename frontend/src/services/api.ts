import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import { toast } from 'react-hot-toast';

// Types
import { 
  LoginRequest, 
  RegisterRequest, 
  AuthResponse, 
  User, 
  Document, 
  DocumentListResponse,
  QuestionRequest,
  AnswerResponse,
  ApiError 
} from '../types';

// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

// Create axios instance with longer timeout for uploads
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 minutes for general requests
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error: AxiosError<ApiError>) => {
    if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
      toast.error('Request timed out. Please try again or upload a smaller file.');
    } else if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
      toast.error('Session expired. Please login again.');
    } else if (error.response?.data?.detail) {
      toast.error(error.response.data.detail);
    } else {
      toast.error('An unexpected error occurred.');
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: async (credentials: LoginRequest): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/auth/login', credentials);
    return response.data;
  },

  register: async (userData: RegisterRequest): Promise<User> => {
    const response = await api.post<User>('/auth/signup', userData);
    return response.data;
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await api.get<User>('/auth/me');
    return response.data;
  },

  updateUser: async (userData: Partial<User>): Promise<User> => {
    const response = await api.put<User>('/auth/me', userData);
    return response.data;
  },

  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
  },
};

// Documents API
export const documentsAPI = {
  uploadDocument: async (file: File, onUploadProgress?: (progress: number) => void): Promise<Document> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post<Document>('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 600000, // 10 minutes for file uploads
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total && onUploadProgress) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onUploadProgress(progress);
        }
      },
    });
    return response.data;
  },

  getDocuments: async (params?: {
    skip?: number;
    limit?: number;
    is_active?: boolean;
  }): Promise<DocumentListResponse> => {
    const response = await api.get<DocumentListResponse>('/documents', { params });
    return response.data;
  },

  getDocument: async (id: number): Promise<Document> => {
    const response = await api.get<Document>(`/documents/${id}`);
    return response.data;
  },

  updateDocument: async (id: number, data: Partial<Document>): Promise<Document> => {
    const response = await api.put<Document>(`/documents/${id}`, data);
    return response.data;
  },

  deleteDocument: async (id: number): Promise<void> => {
    await api.delete(`/documents/${id}`);
  },

  toggleDocumentActive: async (id: number): Promise<Document> => {
    const response = await api.post<Document>(`/documents/${id}/toggle-active`);
    return response.data;
  },

  selectDocuments: async (data: { document_ids: number[]; is_active: boolean }): Promise<any> => {
    const response = await api.post('/documents/select-documents', data);
    return response.data;
  },

  getDocumentChunks: async (id: number): Promise<{ document_id: number; total_chunks: number; chunks: any[] }> => {
    const response = await api.get(`/documents/${id}/chunks`);
    return response.data;
  },
};

// Q&A API
export const qaAPI = {
  askQuestion: async (question: QuestionRequest): Promise<AnswerResponse> => {
    const response = await api.post<AnswerResponse>('/qa/ask', question);
    return response.data;
  },

  getStats: async (): Promise<any> => {
    const response = await api.get('/qa/stats');
    return response.data;
  },
};

export default api; 