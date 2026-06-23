import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Input } from '@/components/ui/input';
import { 
  ArrowLeft, 
  ArrowRight, 
  RotateCcw, 
  Check, 
  X, 
  Eye, 
  EyeOff,
  BookOpen
} from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { api } from '@/services/api';
import { toast } from 'sonner';
import type { VocabularyWord } from '@/types';

export default function VocabularyPage() {
  const { user } = useAuth();
  const [words, setWords] = useState<VocabularyWord[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [loading, setLoading] = useState(true);
  const [jlptFilter, setJlptFilter] = useState('');
  const [romajiInput, setRomajiInput] = useState('');
  const [showRomajiInput, setShowRomajiInput] = useState(false);
  const [isCorrect, setIsCorrect] = useState<boolean | null>(null);

  useEffect(() => {
    loadVocabulary();
  }, [jlptFilter]);

  const loadVocabulary = async () => {
    setLoading(true);
    try {
      const data = await api.getVocabulary({
        jlpt_level: jlptFilter || undefined,
        limit: 50,
      });
      setWords(data.words);
      setCurrentIndex(0);
      setIsFlipped(false);
    } catch (error) {
      toast.error('加载词汇失败');
    } finally {
      setLoading(false);
    }
  };

  const currentWord = words[currentIndex];

  const handleNext = () => {
    if (currentIndex < words.length - 1) {
      setCurrentIndex(currentIndex + 1);
      setIsFlipped(false);
      setRomajiInput('');
      setIsCorrect(null);
    }
  };

  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
      setIsFlipped(false);
      setRomajiInput('');
      setIsCorrect(null);
    }
  };

  const handleFlip = () => {
    setIsFlipped(!isFlipped);
  };

  const handleRomajiSubmit = () => {
    if (!currentWord) return;
    
    const correct = romajiInput.toLowerCase().trim() === currentWord.romaji.toLowerCase();
    setIsCorrect(correct);
    setIsFlipped(true);
    
    // Update progress if user is logged in
    if (user) {
      api.updateProgress(currentWord.id, correct);
    }
  };

  const handleMarkCorrect = async () => {
    if (!currentWord || !user) return;
    
    try {
      await api.updateProgress(currentWord.id, true);
      toast.success('已标记为正确');
      handleNext();
    } catch (error) {
      toast.error('更新失败');
    }
  };

  const handleMarkIncorrect = async () => {
    if (!currentWord || !user) return;
    
    try {
      await api.updateProgress(currentWord.id, false);
      toast.error('已标记为错误');
      handleNext();
    } catch (error) {
      toast.error('更新失败');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-gray-600">加载中...</p>
        </div>
      </div>
    );
  }

  if (words.length === 0) {
    return (
      <div className="text-center py-12">
        <BookOpen className="h-16 w-16 text-gray-400 mx-auto mb-4" />
        <h2 className="text-2xl font-bold mb-2">暂无词汇</h2>
        <p className="text-gray-600">
          {jlptFilter ? '该等级下暂无词汇' : '请稍后再试'}
        </p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6 page-enter">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold link-hover-effect">词汇学习</h1>
        <div className="flex items-center gap-2">
          <select
            value={jlptFilter}
            onChange={(e) => setJlptFilter(e.target.value)}
            className="px-3 py-2 border rounded-md dropdown-animated"
          >
            <option value="">全部等级</option>
            <option value="N5">N5 - 基础入门</option>
            {user?.is_premium && (
              <>
                <option value="N4">N4 - 基础</option>
                <option value="N3">N3 - 中级</option>
                <option value="N2">N2 - 中高级</option>
                <option value="N1">N1 - 高级</option>
              </>
            )}
          </select>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowRomajiInput(!showRomajiInput)}
            className="button-hover-effect"
          >
            {showRomajiInput ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            {showRomajiInput ? '隐藏' : '显示'}输入模式
          </Button>
        </div>
      </div>

      {/* Progress */}
      <div className="space-y-2">
        <div className="flex justify-between text-sm text-gray-600">
          <span>进度</span>
          <span className="font-semibold">{currentIndex + 1} / {words.length}</span>
        </div>
        <Progress value={((currentIndex + 1) / words.length) * 100} className="progress-animated" />
      </div>

      {/* Flashcard */}
      <Card className={`min-h-[400px] flex flex-col justify-center card-hover-effect ${isFlipped ? 'flipped' : ''}`}>
        <CardHeader>
          <div className="flex items-center justify-between">
            <Badge variant="secondary" className="badge-ping">{currentWord.jlpt_level}</Badge>
            <Badge variant="outline">{currentWord.category}</Badge>
          </div>
        </CardHeader>
        <CardContent className="flex-1 flex flex-col items-center justify-center space-y-6 flashcard">
          <div className="flashcard-inner w-full">
            {!isFlipped ? (
              /* Front of card - Japanese word */
              <div className="text-center space-y-4 flashcard-front">
                <div className="text-6xl font-bold text-primary mb-4 float-animation">
                  {currentWord.japanese}
                </div>
                
                {!showRomajiInput ? (
                  <>
                    <div className="text-2xl text-gray-600">
                      {currentWord.hiragana}
                    </div>
                    <Button onClick={handleFlip} size="lg" className="mt-8 button-hover-effect button-click-effect">
                      查看意思 <ArrowRight className="ml-2 h-4 w-4" />
                    </Button>
                  </>
                ) : (
                  <>
                    <div className="text-2xl text-gray-400">
                      {currentWord.hiragana}
                    </div>
                    <div className="w-full max-w-md space-y-4">
                      <p className="text-sm text-gray-600">输入罗马音：</p>
                      <div className="flex gap-2">
                        <Input
                          type="text"
                          placeholder="输入罗马音..."
                          value={romajiInput}
                          onChange={(e) => setRomajiInput(e.target.value)}
                          onKeyPress={(e) => {
                            if (e.key === 'Enter') handleRomajiSubmit();
                          }}
                          className="text-lg input-focus-effect"
                        />
                        <Button onClick={handleRomajiSubmit} className="button-click-effect">
                          确认
                        </Button>
                      </div>
                    </div>
                  </>
                )}
              </div>
            ) : (
              /* Back of card - Meaning */
              <div className="text-center space-y-6 flashcard-back">
                {isCorrect !== null && (
                  <div className={`text-2xl font-bold ${isCorrect ? 'answer-correct' : 'answer-incorrect'}`}>
                    {isCorrect ? '✓ 正确！' : '✗ 错误'}
                  </div>
                )}
                
                <div className="space-y-4 card-enter">
                  <div>
                    <p className="text-sm text-gray-600 mb-1">假名</p>
                    <p className="text-3xl">{currentWord.hiragana}</p>
                  </div>
                  
                  <div>
                    <p className="text-sm text-gray-600 mb-1">罗马音</p>
                    <p className="text-2xl text-blue-600">{currentWord.romaji}</p>
                  </div>
                  
                  <div className="space-y-2">
                    <p className="text-sm text-gray-600">意思</p>
                    <p className="text-2xl font-semibold">{currentWord.meaning_zh}</p>
                    <p className="text-lg text-gray-600">{currentWord.meaning_en}</p>
                  </div>
                </div>
                
                {user && (
                  <div className="flex gap-4 justify-center pt-4">
                    <Button onClick={handleMarkCorrect} variant="default" className="gap-2 button-hover-effect button-click-effect">
                      <Check className="h-4 w-4" />
                      认识
                    </Button>
                    <Button onClick={handleMarkIncorrect} variant="destructive" className="gap-2 button-hover-effect button-click-effect">
                      <X className="h-4 w-4" />
                      不认识
                    </Button>
                  </div>
                )}
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Navigation */}
      <div className="flex items-center justify-between">
        <Button
          onClick={handlePrevious}
          disabled={currentIndex === 0}
          variant="outline"
          className="nav-button"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          上一个
        </Button>
        
        <Button onClick={handleFlip} variant="ghost" className="gap-2 button-hover-effect">
          <RotateCcw className="h-4 w-4" />
          翻转
        </Button>
        
        <Button
          onClick={handleNext}
          disabled={currentIndex === words.length - 1}
          variant="outline"
          className="nav-button"
        >
          下一个
          <ArrowRight className="ml-2 h-4 w-4" />
        </Button>
      </div>

      {/* Keyboard shortcuts hint */}
      <div className="text-center text-sm text-gray-500">
        提示：按空格键翻转卡片，左右箭头键切换单词
      </div>
    </div>
  );
}
