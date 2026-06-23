import type {
  VocabularyWord,
  AuthResponse,
  VocabularyResponse,
  LearningProgress,
  LearningStats
} from '@/types';

// 同源部署：前端和后端在同一个服务，直接使用相对路径 /api
// 开发环境通过 Vite proxy 转发到 localhost:3001
const API_BASE_URL = '/api';

// Get token from localStorage
const getToken = () => localStorage.getItem('token');

// Headers with auth
const getHeaders = (includeAuth = true) => {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  if (includeAuth) {
    const token = getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
  }

  return headers;
};

// API service
export const api = {
  // Auth
  async register(email: string, password: string, name?: string): Promise<AuthResponse> {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: getHeaders(false),
      body: JSON.stringify({ email, password, name }),
    });
    return response.json();
  },

  async login(email: string, password: string): Promise<AuthResponse> {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: getHeaders(false),
      body: JSON.stringify({ email, password }),
    });
    return response.json();
  },

  async getCurrentUser(): Promise<{ user: any }> {
    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: getHeaders(),
    });
    return response.json();
  },

  // Vocabulary
  async getVocabulary(params?: {
    jlpt_level?: string;
    category?: string;
    page?: number;
    limit?: number;
    search?: string;
  }): Promise<VocabularyResponse> {
    const query = new URLSearchParams();
    if (params?.jlpt_level) query.append('jlpt_level', params.jlpt_level);
    if (params?.category) query.append('category', params.category);
    if (params?.page) query.append('page', params.page.toString());
    if (params?.limit) query.append('limit', params.limit.toString());
    if (params?.search) query.append('search', params.search);

    const response = await fetch(`${API_BASE_URL}/vocabulary?${query.toString()}`, {
      headers: getHeaders(),
    });
    return response.json();
  },

  async getWordById(id: number): Promise<{ word: VocabularyWord }> {
    const response = await fetch(`${API_BASE_URL}/vocabulary/${id}`, {
      headers: getHeaders(),
    });
    return response.json();
  },

  async getCategories(): Promise<{ categories: string[] }> {
    const response = await fetch(`${API_BASE_URL}/vocabulary/meta/categories`);
    return response.json();
  },

  async getJlptLevels(): Promise<{ levels: string[] }> {
    const response = await fetch(`${API_BASE_URL}/vocabulary/meta/jlpt-levels`);
    return response.json();
  },

  async getVocabStats(): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/vocabulary/meta/stats`);
    return response.json();
  },

  // Favorites
  async getFavorites(): Promise<{ words: VocabularyWord[]; count: number }> {
    const response = await fetch(`${API_BASE_URL}/vocabulary/favorites/list`, {
      headers: getHeaders(),
    });
    return response.json();
  },

  async getFavoriteIds(): Promise<{ ids: number[] }> {
    const response = await fetch(`${API_BASE_URL}/vocabulary/favorites/ids`, {
      headers: getHeaders(),
    });
    return response.json();
  },

  async addFavorite(wordId: number): Promise<{ success: boolean }> {
    const response = await fetch(`${API_BASE_URL}/vocabulary/favorites/${wordId}`, {
      method: 'POST',
      headers: getHeaders(),
    });
    return response.json();
  },

  async removeFavorite(wordId: number): Promise<{ success: boolean }> {
    const response = await fetch(`${API_BASE_URL}/vocabulary/favorites/${wordId}`, {
      method: 'DELETE',
      headers: getHeaders(),
    });
    return response.json();
  },

  // Progress
  async getLearningProgress(): Promise<{ progress: LearningProgress[] }> {
    const response = await fetch(`${API_BASE_URL}/progress/`, {
      headers: getHeaders(),
    });
    return response.json();
  },

  async updateProgress(vocabulary_id: number, correct: boolean): Promise<{ success: boolean }> {
    const response = await fetch(`${API_BASE_URL}/progress/update`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ vocabulary_id, correct }),
    });
    return response.json();
  },

  async getReviewWords(): Promise<{ words: VocabularyWord[] }> {
    const response = await fetch(`${API_BASE_URL}/progress/review`, {
      headers: getHeaders(),
    });
    return response.json();
  },

  async getStats(): Promise<{ stats: LearningStats }> {
    const response = await fetch(`${API_BASE_URL}/progress/stats`, {
      headers: getHeaders(),
    });
    return response.json();
  },

  async resetProgress(): Promise<{ success: boolean }> {
    const response = await fetch(`${API_BASE_URL}/progress/reset`, {
      method: 'DELETE',
      headers: getHeaders(),
    });
    return response.json();
  },

  // Payments
  async getPaymentConfig(): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/payments/config`);
    return response.json();
  },

  async createPaymentOrder(method: 'wechat' | 'alipay'): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/payments/create-order`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ method }),
    });
    return response.json();
  },

  async confirmPayment(orderId: string, method: string): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/payments/confirm-payment`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ orderId, method }),
    });
    return response.json();
  },

  async getPremiumStatus(): Promise<{ is_premium: boolean; premium_expires_at?: string; premium_type?: string }> {
    const response = await fetch(`${API_BASE_URL}/payments/status`, {
      headers: getHeaders(),
    });
    return response.json();
  },

  async getPaymentHistory(): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/payments/history`, {
      headers: getHeaders(),
    });
    return response.json();
  },
};
