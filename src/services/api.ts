import type {
  VocabularyWord,
  AuthResponse,
  VocabularyResponse,
  LearningProgress,
  LearningStats
} from '@/types';
import { vocabularyData } from '@/data/vocabulary-data';

// ============================================
// 纯静态网站 - 所有数据存储在浏览器本地
// 无需后端服务器
// ============================================

// 为词汇数据添加 id
const allWords: VocabularyWord[] = vocabularyData.map((w, i) => ({
  id: i + 1,
  ...w,
}));

// 缓存
let cachedCategories: string[] | null = null;
let cachedStats: any = null;

// localStorage keys
const STORAGE_KEYS = {
  USERS: 'jl_users',
  CURRENT_USER: 'jl_current_user',
  FAVORITES: 'jl_favorites',
  PROGRESS: 'jl_progress',
  PREMIUM_CODE: 'jl_premium_activated',
};

// 激活码（用户可通过此码解锁会员）
const PREMIUM_ACTIVATION_CODE = 'JPLEARN2026';

// Simple hash for password (not secure, but sufficient for local-only auth)
const simpleHash = (str: string): string => {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash |= 0;
  }
  return hash.toString(36);
};

// Local user type
interface LocalUser {
  id: number;
  email: string;
  password: string;
  name: string;
  is_premium: boolean;
  createdAt: string;
}

// Get users from localStorage
const getUsers = (): LocalUser[] => {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEYS.USERS) || '[]');
  } catch {
    return [];
  }
};

// Save users to localStorage
const saveUsers = (users: LocalUser[]) => {
  localStorage.setItem(STORAGE_KEYS.USERS, JSON.stringify(users));
};

// Get current user
const getCurrentUserFromStorage = (): LocalUser | null => {
  try {
    const data = localStorage.getItem(STORAGE_KEYS.CURRENT_USER);
    if (!data) return null;
    const { email } = JSON.parse(data);
    const users = getUsers();
    return users.find(u => u.email === email) || null;
  } catch {
    return null;
  }
};

// Set current user
const setCurrentUser = (user: LocalUser | null) => {
  if (user) {
    localStorage.setItem(STORAGE_KEYS.CURRENT_USER, JSON.stringify({ email: user.email }));
  } else {
    localStorage.removeItem(STORAGE_KEYS.CURRENT_USER);
  }
};

// Get favorites from localStorage
const getFavoriteIds = (): Set<number> => {
  try {
    const data = localStorage.getItem(STORAGE_KEYS.FAVORITES);
    if (!data) return new Set();
    return new Set(JSON.parse(data));
  } catch {
    return new Set();
  }
};

// Save favorites
const saveFavoriteIds = (ids: Set<number>) => {
  localStorage.setItem(STORAGE_KEYS.FAVORITES, JSON.stringify([...ids]));
};

// Get progress from localStorage
interface LocalProgress {
  [wordId: number]: {
    times_correct: number;
    times_incorrect: number;
    last_reviewed: string;
    next_review_date: string;
    mastery_level: number;
  };
}

const getProgress = (): LocalProgress => {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEYS.PROGRESS) || '{}');
  } catch {
    return {};
  }
};

const saveProgress = (progress: LocalProgress) => {
  localStorage.setItem(STORAGE_KEYS.PROGRESS, JSON.stringify(progress));
};

// API service - mimics the old API interface but uses local data
export const api = {
  // ============================================
  // Auth
  // ============================================
  async register(email: string, password: string, name?: string): Promise<AuthResponse> {
    await new Promise(r => setTimeout(r, 300)); // simulate network delay

    const users = getUsers();
    if (users.find(u => u.email === email)) {
      return { success: false, error: '该邮箱已被注册' };
    }

    const user: LocalUser = {
      id: Date.now(),
      email,
      password: simpleHash(password),
      name: name || email.split('@')[0],
      is_premium: false,
      createdAt: new Date().toISOString(),
    };

    users.push(user);
    saveUsers(users);
    setCurrentUser(user);

    return {
      success: true,
      token: 'local_' + user.id,
      user: { id: user.id, email: user.email, name: user.name, is_premium: user.is_premium },
    };
  },

  async login(email: string, password: string): Promise<AuthResponse> {
    await new Promise(r => setTimeout(r, 300));

    const users = getUsers();
    const user = users.find(u => u.email === email);

    if (!user || user.password !== simpleHash(password)) {
      return { success: false, error: '邮箱或密码错误' };
    }

    setCurrentUser(user);

    return {
      success: true,
      token: 'local_' + user.id,
      user: { id: user.id, email: user.email, name: user.name, is_premium: user.is_premium },
    };
  },

  async getCurrentUser(): Promise<{ user: any }> {
    const user = getCurrentUserFromStorage();
    if (!user) return { user: null };
    return {
      user: { id: user.id, email: user.email, name: user.name, is_premium: user.is_premium },
    };
  },

  // ============================================
  // Vocabulary
  // ============================================
  async getVocabulary(params?: {
    jlpt_level?: string;
    category?: string;
    page?: number;
    limit?: number;
    search?: string;
  }): Promise<VocabularyResponse> {
    await new Promise(r => setTimeout(r, 100));

    let filtered = [...allWords];

    // Filter by JLPT level
    if (params?.jlpt_level) {
      filtered = filtered.filter(w => w.jlpt_level === params.jlpt_level);
    }

    // Filter by category
    if (params?.category) {
      filtered = filtered.filter(w => w.category === params.category);
    }

    // Search
    if (params?.search) {
      const term = params.search.toLowerCase();
      filtered = filtered.filter(w =>
        w.japanese.toLowerCase().includes(term) ||
        w.hiragana.toLowerCase().includes(term) ||
        w.romaji.toLowerCase().includes(term) ||
        w.meaning_en.toLowerCase().includes(term) ||
        w.meaning_zh.toLowerCase().includes(term)
      );
    }

    // Pagination
    const page = params?.page || 1;
    const limit = Math.min(params?.limit || 24, 100);
    const total = filtered.length;
    const totalPages = Math.ceil(total / limit);
    const start = (page - 1) * limit;
    const words = filtered.slice(start, start + limit);

    return {
      words,
      pagination: { page, limit, total, totalPages },
    };
  },

  async getWordById(id: number): Promise<{ word: VocabularyWord }> {
    return { word: allWords.find(w => w.id === id) || allWords[0] };
  },

  async getCategories(): Promise<{ categories: string[] }> {
    if (!cachedCategories) {
      cachedCategories = [...new Set(allWords.map(w => w.category))].sort();
    }
    return { categories: cachedCategories };
  },

  async getJlptLevels(): Promise<{ levels: string[] }> {
    return { levels: ['N5', 'N4', 'N3', 'N2', 'N1'] };
  },

  async getVocabStats(): Promise<any> {
    if (!cachedStats) {
      const byLevel: Record<string, number> = {};
      const byCategory: Record<string, number> = {};
      for (const w of allWords) {
        byLevel[w.jlpt_level] = (byLevel[w.jlpt_level] || 0) + 1;
        byCategory[w.category] = (byCategory[w.category] || 0) + 1;
      }
      cachedStats = {
        total: allWords.length,
        byLevel,
        byCategory,
      };
    }
    return { stats: cachedStats };
  },

  // ============================================
  // Favorites
  // ============================================
  async getFavorites(): Promise<{ words: VocabularyWord[]; count: number }> {
    const ids = getFavoriteIds();
    const words = allWords.filter(w => ids.has(w.id));
    return { words, count: words.length };
  },

  async getFavoriteIds(): Promise<{ ids: number[] }> {
    return { ids: [...getFavoriteIds()] };
  },

  async addFavorite(wordId: number): Promise<{ success: boolean }> {
    const ids = getFavoriteIds();
    ids.add(wordId);
    saveFavoriteIds(ids);
    return { success: true };
  },

  async removeFavorite(wordId: number): Promise<{ success: boolean }> {
    const ids = getFavoriteIds();
    ids.delete(wordId);
    saveFavoriteIds(ids);
    return { success: true };
  },

  // ============================================
  // Learning Progress
  // ============================================
  async getLearningProgress(): Promise<{ progress: LearningProgress[] }> {
    const progress = getProgress();
    const result: LearningProgress[] = Object.entries(progress).map(([id, p]) => {
      const word = allWords.find(w => w.id === parseInt(id));
      if (!word) return null as any;
      return {
        id: parseInt(id),
        user_id: 0,
        vocabulary_id: parseInt(id),
        times_correct: p.times_correct,
        times_incorrect: p.times_incorrect,
        last_reviewed: p.last_reviewed,
        next_review_date: p.next_review_date,
        mastery_level: p.mastery_level,
        japanese: word.japanese,
        hiragana: word.hiragana,
        romaji: word.romaji,
        meaning_en: word.meaning_en,
        meaning_zh: word.meaning_zh,
        jlpt_level: word.jlpt_level,
      };
    }).filter(Boolean);

    return { progress: result };
  },

  async updateProgress(vocabulary_id: number, correct: boolean): Promise<{ success: boolean }> {
    const progress = getProgress();
    const existing = progress[vocabulary_id] || {
      times_correct: 0,
      times_incorrect: 0,
      last_reviewed: '',
      next_review_date: '',
      mastery_level: 0,
    };

    if (correct) {
      existing.times_correct++;
      existing.mastery_level = Math.min(5, existing.mastery_level + 1);
    } else {
      existing.times_incorrect++;
      existing.mastery_level = Math.max(0, existing.mastery_level - 1);
    }

    existing.last_reviewed = new Date().toISOString();
    const next = new Date();
    next.setDate(next.getDate() + (correct ? 3 : 1));
    existing.next_review_date = next.toISOString();

    progress[vocabulary_id] = existing;
    saveProgress(progress);

    return { success: true };
  },

  async getReviewWords(): Promise<{ words: VocabularyWord[] }> {
    const progress = getProgress();
    const now = new Date();
    const reviewIds = Object.entries(progress)
      .filter(([_, p]) => new Date(p.next_review_date) <= now && p.mastery_level < 5)
      .map(([id]) => parseInt(id));
    const words = allWords.filter(w => reviewIds.includes(w.id));
    return { words };
  },

  async getStats(): Promise<{ stats: LearningStats }> {
    const progress = getProgress();
    const entries = Object.values(progress);

    const totalWordsLearned = entries.length;
    const mastered = entries.filter(e => e.mastery_level >= 5).length;
    const totalCorrect = entries.reduce((sum, e) => sum + e.times_correct, 0);
    const totalIncorrect = entries.reduce((sum, e) => sum + e.times_incorrect, 0);
    const accuracy = totalCorrect + totalIncorrect > 0
      ? Math.round((totalCorrect / (totalCorrect + totalIncorrect)) * 100)
      : 0;

    return {
      stats: {
        total_words_learned: totalWordsLearned,
        mastered,
        new_words: allWords.length - totalWordsLearned,
        total_correct: totalCorrect,
        total_incorrect: totalIncorrect,
        total_vocabulary: allWords.length,
        accuracy,
      },
    };
  },

  async resetProgress(): Promise<{ success: boolean }> {
    localStorage.removeItem(STORAGE_KEYS.PROGRESS);
    return { success: true };
  },

  // ============================================
  // Payment / Premium (本地激活码模式)
  // ============================================
  async getPaymentConfig(): Promise<any> {
    return {
      mode: 'activation_code',
      price: 49.9,
      product: 'lifetime_premium',
    };
  },

  async createPaymentOrder(method: 'wechat' | 'alipay'): Promise<any> {
    // 静态网站：返回联系信息
    return {
      success: true,
      orderId: 'local_' + Date.now(),
      message: '请扫码支付后输入激活码',
      paymentMethod: method,
      price: 49.9,
    };
  },

  async confirmPayment(_orderId: string, _method: string): Promise<any> {
    // 静态网站不使用此方法，改用 activateWithCode
    return { success: false, message: '请使用激活码' };
  },

  async getPremiumStatus(): Promise<{ is_premium: boolean }> {
    const user = getCurrentUserFromStorage();
    return { is_premium: user?.is_premium || false };
  },

  async getPaymentHistory(): Promise<any> {
    return { history: [] };
  },

  // ============================================
  // 新增：激活码解锁会员
  // ============================================
  async activateWithCode(code: string): Promise<{ success: boolean; message: string }> {
    await new Promise(r => setTimeout(r, 300));

    if (code.trim().toUpperCase() === PREMIUM_ACTIVATION_CODE) {
      const user = getCurrentUserFromStorage();
      if (!user) {
        return { success: false, message: '请先登录' };
      }

      // Update user in storage
      const users = getUsers();
      const idx = users.findIndex(u => u.email === user.email);
      if (idx >= 0) {
        users[idx].is_premium = true;
        saveUsers(users);
      }

      return { success: true, message: '激活成功！已解锁全部词汇。' };
    }

    return { success: false, message: '激活码无效' };
  },
};
