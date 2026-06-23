// Type definitions for Japanese Learning App

export interface VocabularyWord {
  id: number;
  japanese: string;
  hiragana: string;
  romaji: string;
  meaning_en: string;
  meaning_zh: string;
  jlpt_level: string;
  category: string;
  is_premium: number;
  example_sentence?: string;
  example_translation?: string;
  favorited_at?: string;
}

export interface User {
  id: number;
  email: string;
  name: string;
  is_premium: boolean;
}

export interface AuthResponse {
  success: boolean;
  token?: string;
  user?: User;
  error?: string;
}

export interface LearningProgress {
  id: number;
  user_id: number;
  vocabulary_id: number;
  times_correct: number;
  times_incorrect: number;
  last_reviewed: string;
  next_review_date: string;
  mastery_level: number;
  japanese: string;
  hiragana: string;
  romaji: string;
  meaning_en: string;
  meaning_zh: string;
  jlpt_level: string;
}

export interface LearningStats {
  total_words_learned: number;
  mastered: number;
  new_words: number;
  total_correct: number;
  total_incorrect: number;
  total_vocabulary: number;
  accuracy: number;
}

export interface PaginationInfo {
  page: number;
  limit: number;
  total: number;
  totalPages: number;
}

export interface VocabularyResponse {
  words: VocabularyWord[];
  pagination: PaginationInfo;
}

export interface PaymentPlan {
  id: string;
  name: string;
  price: number;
  duration: string;
  features: string[];
}

export type JLPTLevel = 'N5' | 'N4' | 'N3' | 'N2' | 'N1';

export type Category = '动词' | '名词' | '形容词' | '副词' | '代词' | '数字' | '接续词' | '助词';
