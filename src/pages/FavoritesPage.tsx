import { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Star, BookOpen, Trash2 } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { api } from '@/services/api';
import { toast } from 'sonner';
import { Link } from 'react-router-dom';
import type { VocabularyWord } from '@/types';

export default function FavoritesPage() {
  const { user } = useAuth();
  const [favorites, setFavorites] = useState<VocabularyWord[]>([]);
  const [loading, setLoading] = useState(true);

  const loadFavorites = async () => {
    setLoading(true);
    try {
      const data = await api.getFavorites();
      setFavorites(data.words || []);
    } catch (error) {
      toast.error('加载收藏失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user) {
      loadFavorites();
    } else {
      setLoading(false);
    }
  }, [user]);

  const handleRemove = async (wordId: number) => {
    try {
      await api.removeFavorite(wordId);
      setFavorites(prev => prev.filter(w => w.id !== wordId));
      toast.success('已取消收藏');
    } catch (error) {
      toast.error('操作失败');
    }
  };

  if (!user) {
    return (
      <div className="text-center py-12">
        <Star className="h-16 w-16 text-gray-300 mx-auto mb-4" />
        <h2 className="text-xl font-bold mb-2">请先登录</h2>
        <p className="text-gray-500 mb-4">登录后即可收藏词汇</p>
        <Button asChild>
          <Link to="/login">去登录</Link>
        </Button>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[40vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6 page-enter">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">我的收藏</h1>
          <p className="text-gray-500 mt-1">共 {favorites.length} 个词汇</p>
        </div>
        <Button asChild variant="outline">
          <Link to="/vocab-list">
            <BookOpen className="mr-2 h-4 w-4" />
            浏览全部词汇
          </Link>
        </Button>
      </div>

      {favorites.length === 0 ? (
        <div className="text-center py-12">
          <Star className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <h2 className="text-xl font-bold mb-2">还没有收藏词汇</h2>
          <p className="text-gray-500 mb-4">浏览词汇时点击星标即可收藏</p>
          <Button asChild>
            <Link to="/vocab-list">去浏览词汇</Link>
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {favorites.map((word) => (
            <Card key={word.id} className="card-hover-effect group relative">
              <CardContent className="pt-4 pb-3 px-4">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex gap-2">
                    <Badge variant="secondary" className="text-xs">{word.jlpt_level}</Badge>
                    <Badge variant="outline" className="text-xs">{word.category}</Badge>
                  </div>
                  <button
                    onClick={() => handleRemove(word.id)}
                    className="opacity-60 group-hover:opacity-100 transition-opacity"
                  >
                    <Trash2 className="h-4 w-4 text-gray-400 hover:text-red-500" />
                  </button>
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
      )}
    </div>
  );
}
