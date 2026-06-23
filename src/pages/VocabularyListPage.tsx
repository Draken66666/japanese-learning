import { useState, useEffect, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Search, Star, BookOpen, ChevronLeft, ChevronRight, Lock } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { api } from '@/services/api';
import { toast } from 'sonner';
import type { VocabularyWord } from '@/types';
import { Link } from 'react-router-dom';

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

  const pageSize = 24;

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

  return (
    <div className="max-w-6xl mx-auto space-y-6 page-enter">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">词汇浏览</h1>
          <p className="text-gray-500 mt-1">共 {total} 个词汇</p>
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
              <Card key={word.id} className="card-hover-effect group relative">
                <CardContent className="pt-4 pb-3 px-4">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex gap-2">
                      <Badge variant="secondary" className="text-xs">{word.jlpt_level}</Badge>
                      <Badge variant="outline" className="text-xs">{word.category}</Badge>
                    </div>
                    {user && (
                      <button
                        onClick={() => handleToggleFavorite(word.id)}
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

                  <div className="mb-2">
                    <span className="text-2xl font-bold text-gray-900">{word.japanese}</span>
                  </div>
                  <div className="text-sm text-gray-500 mb-1">{word.hiragana}</div>
                  <div className="text-xs text-blue-500 mb-2">{word.romaji}</div>
                  <div className="text-sm font-medium text-gray-700">
                    {word.meaning_zh || word.meaning_en}
                  </div>
                  {word.meaning_zh && word.meaning_zh !== word.meaning_en && (
                    <div className="text-xs text-gray-400 mt-1">{word.meaning_en}</div>
                  )}

                  {word.example_sentence && (
                    <div className="mt-3 pt-3 border-t border-gray-100">
                      <p className="text-xs text-gray-600">{word.example_sentence}</p>
                      {word.example_translation && (
                        <p className="text-xs text-gray-400 mt-1">{word.example_translation}</p>
                      )}
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
    </div>
  );
}
