import { useState, useEffect, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Search, Star, BookOpen, ChevronLeft, ChevronRight, Lock, Volume2, BookMarked, Languages, Lightbulb, AlertCircle } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { api } from '@/services/api';
import { toast } from 'sonner';
import type { VocabularyWord } from '@/types';
import { Link } from 'react-router-dom';

// TTS: preload Japanese voice
let japaneseVoice: SpeechSynthesisVoice | null = null;
let ttsWarned = false;

function loadJapaneseVoice(): SpeechSynthesisVoice | null {
  if (typeof window === 'undefined' || !('speechSynthesis' in window)) return null;
  const voices = window.speechSynthesis.getVoices();
  const jaVoice = voices.find(v => v.lang === 'ja-JP' || v.lang.startsWith('ja'));
  return jaVoice || null;
}

function hasJapaneseVoice(): boolean {
  if (typeof window === 'undefined' || !('speechSynthesis' in window)) return false;
  const voices = window.speechSynthesis.getVoices();
  return voices.some(v => v.lang === 'ja-JP' || v.lang.startsWith('ja'));
}

if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
  japaneseVoice = loadJapaneseVoice();
  window.speechSynthesis.onvoiceschanged = () => {
    japaneseVoice = loadJapaneseVoice();
  };
}

// 格式化释义：多个意思分行显示
function formatMeaning(meaning: string | undefined): string[] {
  if (!meaning) return [];
  return meaning.split(/[,;，；]/).map(s => s.trim()).filter(s => s);
}

export default function VocabularyListPage() {
  const { user } = useAuth();
  const [words, setWords] = useState<VocabularyWord[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [jlptLevel, setJlptLevel] = useState('all');
  const [category, setCategory] = useState('all');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [categories, setCategories] = useState<string[]>([]);
  const [favoriteIds, setFavoriteIds] = useState<Set<number>>(new Set());
  const [selectedWord, setSelectedWord] = useState<VocabularyWord | null>(null);
  const [showTTSWarning, setShowTTSWarning] = useState(false);

  const pageSize = 24;

  // 检查日语语音是否可用
  useEffect(() => {
    const checkVoice = () => {
      const available = hasJapaneseVoice();
      setShowTTSWarning(!available);
    };
    checkVoice();
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      window.speechSynthesis.onvoiceschanged = () => {
        japaneseVoice = loadJapaneseVoice();
        checkVoice();
      };
    }
    const timer = setTimeout(checkVoice, 1000);
    return () => clearTimeout(timer);
  }, []);

  const loadCategories = async () => {
    try {
      const data = await api.getCategories();
      setCategories(data.categories || []);
    } catch (error) {
      // ignore
    }
  };

  const loadFavoriteIds = async () => {
    if (!user) return;
    try {
      const data = await api.getFavoriteIds();
      setFavoriteIds(new Set(data.ids || []));
    } catch (error) {
      // ignore
    }
  };

  const loadVocabulary = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.getVocabulary({
        jlpt_level: jlptLevel !== 'all' ? jlptLevel : undefined,
        category: category !== 'all' ? category : undefined,
        search: search.trim() || undefined,
        page,
        limit: pageSize,
      });
      setWords(data.words || []);
      setTotalPages(data.pagination?.totalPages || 1);
      setTotal(data.pagination?.total || 0);
    } catch (error) {
      toast.error('加载词汇失败');
    } finally {
      setLoading(false);
    }
  }, [jlptLevel, category, search, page]);

  useEffect(() => {
    loadCategories();
    loadFavoriteIds();
  }, [user]);

  useEffect(() => {
    loadVocabulary();
  }, [loadVocabulary]);

  // Debounced search
  useEffect(() => {
    const timer = setTimeout(() => {
      if (page !== 1) setPage(1);
      else loadVocabulary();
    }, 300);
    return () => clearTimeout(timer);
  }, [search]);

  const handleToggleFavorite = async (wordId: number) => {
    if (!user) {
      toast.error('请先登录');
      return;
    }

    const isFav = favoriteIds.has(wordId);
    setFavoriteIds(prev => {
      const next = new Set(prev);
      if (isFav) next.delete(wordId);
      else next.add(wordId);
      return next;
    });

    try {
      if (isFav) {
        await api.removeFavorite(wordId);
        toast.success('已取消收藏');
      } else {
        await api.addFavorite(wordId);
        toast.success('已收藏');
      }
    } catch (error) {
      // Revert on error
      setFavoriteIds(prev => {
        const next = new Set(prev);
        if (isFav) next.add(wordId);
        else next.delete(wordId);
        return next;
      });
      toast.error('操作失败');
    }
  };

  const handlePageChange = (newPage: number) => {
    setPage(newPage);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // Speak Japanese word using browser TTS
  const speak = (text: string) => {
    if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
      toast.error('您的浏览器不支持语音播放');
      return;
    }
    // 检查日语语音
    if (!japaneseVoice) {
      japaneseVoice = loadJapaneseVoice();
    }
    if (!japaneseVoice && !ttsWarned) {
      ttsWarned = true;
      toast.warning('未检测到日语语音包，请安装日语语音包后使用发音功能', {
        duration: 8000,
        description: 'Chrome/Edge: 设置→语言→添加日语 | Windows: 设置→时间和语言→语言→添加日语',
      });
    }
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'ja-JP';
    utterance.rate = 0.8;
    utterance.volume = 1;
    if (japaneseVoice) {
      utterance.voice = japaneseVoice;
    }
    utterance.onerror = (e) => {
      console.error('TTS error:', e);
    };
    setTimeout(() => {
      try {
        window.speechSynthesis.speak(utterance);
      } catch (err) {
        console.error('TTS speak error:', err);
      }
    }, 100);
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6 page-enter">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">词汇浏览</h1>
          <p className="text-gray-500 mt-1">共 {total} 个词汇 · 点击单词查看详情</p>
        </div>
        <Button asChild variant="outline">
          <Link to="/vocabulary">
            <BookOpen className="mr-2 h-4 w-4" />
            闪卡学习
          </Link>
        </Button>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            placeholder="搜索日语、假名、罗马音或释义..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10"
          />
        </div>
        <Select value={jlptLevel} onValueChange={(v) => { setJlptLevel(v); setPage(1); }}>
          <SelectTrigger className="w-full sm:w-40">
            <SelectValue placeholder="JLPT等级" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">全部等级</SelectItem>
            <SelectItem value="N5">N5 - 基础入门</SelectItem>
            {user?.is_premium && (
              <>
                <SelectItem value="N4">N4 - 基础</SelectItem>
                <SelectItem value="N3">N3 - 中级</SelectItem>
                <SelectItem value="N2">N2 - 中高级</SelectItem>
                <SelectItem value="N1">N1 - 高级</SelectItem>
              </>
            )}
          </SelectContent>
        </Select>
        <Select value={category} onValueChange={(v) => { setCategory(v); setPage(1); }}>
          <SelectTrigger className="w-full sm:w-32">
            <SelectValue placeholder="词性" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">全部词性</SelectItem>
            {categories.map(cat => (
              <SelectItem key={cat} value={cat}>{cat}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Premium Notice */}
      {!user?.is_premium && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 text-sm text-amber-800">
          <Lock className="inline h-4 w-4 mr-1" />
          免费用户可浏览 N5 等级词汇（共662词）。
          <Link to="/pricing" className="underline font-semibold ml-1">升级会员</Link>
          解锁全部 8000+ 词汇。
        </div>
      )}

      {/* TTS Voice Pack Warning */}
      {showTTSWarning && (
        <div className="bg-amber-50 border border-amber-300 rounded-lg p-4 text-sm">
          <div className="flex items-start gap-2">
            <AlertCircle className="h-5 w-5 text-amber-600 shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="font-semibold text-amber-800 mb-1">未检测到日语语音包</p>
              <p className="text-amber-700 mb-2">发音功能需要日语语音包支持。请按以下步骤安装：</p>
              <ul className="text-amber-700 space-y-1 ml-4 list-disc">
                <li><strong>Chrome / Edge 浏览器</strong>：设置 → 语言 → 添加"日语" → 重启浏览器</li>
                <li><strong>Windows 系统</strong>：设置 → 时间和语言 → 语言 → 添加日语 → 下载语音包</li>
                <li><strong>macOS 系统</strong>：系统偏好设置 → 辅助功能 → 语音 → 系统语音 → 选择"Kyoko"</li>
              </ul>
              <p className="text-amber-600 mt-2 text-xs">安装完成后刷新页面即可使用发音功能</p>
              <button
                onClick={() => setShowTTSWarning(false)}
                className="text-amber-600 hover:text-amber-800 text-xs underline mt-1"
              >
                关闭提示
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Vocabulary Grid */}
      {loading ? (
        <div className="flex items-center justify-center min-h-[40vh]">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        </div>
      ) : words.length === 0 ? (
        <div className="text-center py-12">
          <BookOpen className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500">未找到匹配的词汇</p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {words.map((word) => (
              <Card
                key={word.id}
                className="card-hover-effect group relative cursor-pointer"
                onClick={() => setSelectedWord(word)}
              >
                <CardContent className="pt-4 pb-3 px-4">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex gap-2">
                      <Badge variant="secondary" className="text-xs">{word.jlpt_level}</Badge>
                      <Badge variant="outline" className="text-xs">{word.category}</Badge>
                    </div>
                    {user && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleToggleFavorite(word.id);
                        }}
                        className="opacity-60 group-hover:opacity-100 transition-opacity"
                      >
                        <Star
                          className={`h-4 w-4 ${
                            favoriteIds.has(word.id)
                              ? 'fill-yellow-400 text-yellow-400'
                              : 'text-gray-400'
                          }`}
                        />
                      </button>
                    )}
                  </div>

                  <div className="mb-2 flex items-center gap-2">
                    <span className="text-2xl font-bold text-gray-900">{word.japanese}</span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        speak(word.japanese);
                      }}
                      className="opacity-0 group-hover:opacity-100 transition-opacity text-blue-500 hover:text-blue-600"
                      title="点击发音"
                    >
                      <Volume2 className="h-4 w-4" />
                    </button>
                  </div>
                  <div className="text-sm text-gray-500 mb-1">{word.hiragana}</div>
                  <div className="text-xs text-blue-500 mb-2">{word.romaji}</div>
                  <div className="text-sm font-medium text-gray-700">
                    {formatMeaning(word.meaning_zh || word.meaning_en).map((part, i) => (
                      <span key={i} className="block py-0.5">{part}</span>
                    ))}
                  </div>

                  {word.example_sentence && (
                    <div className="mt-3 pt-3 border-t border-gray-100">
                      <p className="text-xs text-gray-600 line-clamp-2">{word.example_sentence}</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2 pt-4">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePageChange(page - 1)}
                disabled={page === 1}
              >
                <ChevronLeft className="h-4 w-4" />
                上一页
              </Button>
              <span className="text-sm text-gray-600 px-4">
                {page} / {totalPages}
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePageChange(page + 1)}
                disabled={page === totalPages}
              >
                下一页
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          )}
        </>
      )}

      {/* Word Detail Dialog */}
      <Dialog open={!!selectedWord} onOpenChange={(open) => !open && setSelectedWord(null)}>
        <DialogContent className="sm:max-w-lg">
          {selectedWord && (
            <>
              <DialogHeader>
                <DialogTitle className="sr-only">单词详情</DialogTitle>
              </DialogHeader>

              {/* Word Header */}
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-3 mb-2">
                    <span className="text-4xl font-bold text-gray-900">{selectedWord.japanese}</span>
                    <button
                      onClick={() => speak(selectedWord.japanese)}
                      className="text-blue-500 hover:text-blue-600 transition-colors"
                      title="点击发音"
                    >
                      <Volume2 className="h-6 w-6" />
                    </button>
                  </div>
                  {selectedWord.hiragana && (
                    <p className="text-lg text-gray-500">{selectedWord.hiragana}</p>
                  )}
                  <p className="text-sm text-blue-500 mt-1">{selectedWord.romaji}</p>
                </div>
                <div className="flex flex-col gap-2 items-end">
                  <div className="flex gap-2">
                    <Badge variant="secondary">{selectedWord.jlpt_level}</Badge>
                    <Badge variant="outline">{selectedWord.category}</Badge>
                  </div>
                  {user && (
                    <button
                      onClick={() => handleToggleFavorite(selectedWord.id)}
                      className="text-sm flex items-center gap-1 text-gray-500 hover:text-yellow-500 transition-colors"
                    >
                      <Star
                        className={`h-4 w-4 ${
                          favoriteIds.has(selectedWord.id)
                            ? 'fill-yellow-400 text-yellow-400'
                            : ''
                        }`}
                      />
                      {favoriteIds.has(selectedWord.id) ? '已收藏' : '收藏'}
                    </button>
                  )}
                </div>
              </div>

              {/* Meaning Section */}
              <div className="space-y-3">
                {selectedWord.meaning_zh && (
                  <div className="bg-blue-50 rounded-lg p-3">
                    <div className="flex items-center gap-2 text-xs text-blue-600 font-semibold mb-1">
                      <Languages className="h-3.5 w-3.5" />
                      中文释义
                    </div>
                    <div className="text-gray-800 space-y-1">
                      {formatMeaning(selectedWord.meaning_zh).map((part, i) => (
                        <div key={i} className="leading-relaxed">{part}</div>
                      ))}
                    </div>
                  </div>
                )}

                {selectedWord.meaning_en && (
                  <div className="bg-gray-50 rounded-lg p-3">
                    <div className="flex items-center gap-2 text-xs text-gray-500 font-semibold mb-1">
                      <BookMarked className="h-3.5 w-3.5" />
                      English
                    </div>
                    <div className="text-gray-600 text-sm space-y-1">
                      {formatMeaning(selectedWord.meaning_en).map((part, i) => (
                        <div key={i} className="leading-relaxed">{part}</div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Example Sentence */}
              {selectedWord.example_sentence && (
                <div className="bg-amber-50 rounded-lg p-4">
                  <div className="flex items-center gap-2 text-xs text-amber-700 font-semibold mb-2">
                    <Lightbulb className="h-3.5 w-3.5" />
                    例句
                  </div>
                  <div className="flex items-start gap-2 mb-2">
                    <p className="text-gray-800 text-lg leading-relaxed flex-1">
                      {selectedWord.example_sentence}
                    </p>
                    <button
                      onClick={() => speak(selectedWord.example_sentence!)}
                      className="text-blue-500 hover:text-blue-600 transition-colors shrink-0 mt-1"
                      title="朗读例句"
                    >
                      <Volume2 className="h-4 w-4" />
                    </button>
                  </div>
                  {selectedWord.example_translation && (
                    <p className="text-gray-500 text-sm">{selectedWord.example_translation}</p>
                  )}
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex gap-2 pt-2">
                <Button asChild className="flex-1">
                  <Link to="/vocabulary">
                    <BookOpen className="mr-2 h-4 w-4" />
                    闪卡学习
                  </Link>
                </Button>
                <Button
                  variant="outline"
                  onClick={() => setSelectedWord(null)}
                  className="flex-1"
                >
                  关闭
                </Button>
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
