import { useState, useEffect, useRef, useCallback } from 'react';
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
  BookOpen,
  Volume2,
  Shuffle,
  AlertCircle
} from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { api } from '@/services/api';
import { toast } from 'sonner';
import type { VocabularyWord } from '@/types';

// 检查是否有日语语音引擎
let ttsWarned = false;
function hasJapaneseVoice(): boolean {
  if (typeof window === 'undefined' || !('speechSynthesis' in window)) return false;
  const voices = window.speechSynthesis.getVoices();
  return voices.some(v => v.lang === 'ja-JP' || v.lang.startsWith('ja'));
}

// 标准化罗马音：处理 ō/ō → ou, ā → aa 等变体
function normalizeRomaji(s: string): string {
  return s
    .toLowerCase()
    .trim()
    .replace(/ō/g, 'ou')
    .replace(/ō/g, 'ou')
    .replace(/ū/g, 'uu')
    .replace(/ā/g, 'aa')
    .replace(/ī/g, 'ii')
    .replace(/ē/g, 'ee')
    .replace(/-/g, '')
    .replace(/\s+/g, '')
    // 去掉标点
    .replace(/[、。.!！?？，,]/g, '');
}

// 日语 TTS 发音 — 多重策略确保有声音
let japaneseVoice: SpeechSynthesisVoice | null = null;

// 加载日语语音引擎
function loadJapaneseVoice(): SpeechSynthesisVoice | null {
  if (!('speechSynthesis' in window)) return null;
  const voices = window.speechSynthesis.getVoices();
  // 优先找 ja-JP 语音
  const jaVoice = voices.find(v => v.lang === 'ja-JP' || v.lang.startsWith('ja'));
  return jaVoice || null;
}

// 初始化时加载语音
if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
  japaneseVoice = loadJapaneseVoice();
  window.speechSynthesis.onvoiceschanged = () => {
    japaneseVoice = loadJapaneseVoice();
  };
}

function speakJapanese(text: string) {
  if (!('speechSynthesis' in window)) {
    toast.error('您的浏览器不支持语音播放');
    return;
  }

  // 检查是否有日语语音
  if (!japaneseVoice) {
    japaneseVoice = loadJapaneseVoice();
  }

  // 如果仍然没有日语语音，提示用户下载
  if (!japaneseVoice && !ttsWarned) {
    ttsWarned = true;
    toast.warning(
      '未检测到日语语音包，发音功能可能无法正常工作。请安装日语语音包：',
      {
        duration: 8000,
        description: 'Chrome: 设置 → 语言 → 添加日语 | Edge: 设置 → 语言 → 添加日语 | Windows: 设置 → 时间和语言 → 语言 → 添加日语',
      }
    );
  }

  // 取消之前的朗读
  window.speechSynthesis.cancel();

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = 'ja-JP';
  utterance.rate = 0.8;
  utterance.pitch = 1;
  utterance.volume = 1;

  if (japaneseVoice) {
    utterance.voice = japaneseVoice;
  }

  // 添加事件监听用于调试
  utterance.onstart = () => {};
  utterance.onerror = (e) => {
    console.warn('TTS error:', e);
  };

  // 延迟一点确保 cancel 完成
  setTimeout(() => {
    try {
      window.speechSynthesis.speak(utterance);
    } catch (err) {
      console.error('TTS speak error:', err);
    }
  }, 100);
}

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
  const [autoSpeak, setAutoSpeak] = useState(true);
  const [showTTSWarning, setShowTTSWarning] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const advanceTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  // 检查日语语音是否可用
  useEffect(() => {
    const checkVoice = () => {
      const available = hasJapaneseVoice();
      setShowTTSWarning(!available);
    };
    // 初始检查
    checkVoice();
    // voiceschanged 后重新检查
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      window.speechSynthesis.onvoiceschanged = () => {
        japaneseVoice = loadJapaneseVoice();
        checkVoice();
      };
    }
    // 延迟再次检查（某些浏览器需要时间加载）
    const timer = setTimeout(checkVoice, 1000);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    loadVocabulary();
  }, [jlptFilter]);

  // 清理定时器
  useEffect(() => {
    return () => {
      if (advanceTimer.current) clearTimeout(advanceTimer.current);
    };
  }, []);

  // 自动聚焦输入框
  useEffect(() => {
    if (showRomajiInput && !isFlipped && inputRef.current) {
      inputRef.current.focus();
    }
  }, [showRomajiInput, isFlipped, currentIndex]);

  // 自动发音
  useEffect(() => {
    if (currentWord && autoSpeak) {
      const timer = setTimeout(() => speakJapanese(currentWord.japanese), 300);
      return () => clearTimeout(timer);
    }
  }, [currentIndex, autoSpeak]);

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
      setRomajiInput('');
      setIsCorrect(null);
    } catch (error) {
      toast.error('加载词汇失败');
    } finally {
      setLoading(false);
    }
  };

  const currentWord = words[currentIndex];

  const goNext = useCallback(() => {
    if (currentIndex < words.length - 1) {
      setCurrentIndex(currentIndex + 1);
      setIsFlipped(false);
      setRomajiInput('');
      setIsCorrect(null);
    } else {
      toast.info('已到达最后一题，重新开始');
      setCurrentIndex(0);
      setIsFlipped(false);
      setRomajiInput('');
      setIsCorrect(null);
    }
  }, [currentIndex, words.length]);

  const goPrevious = useCallback(() => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
      setIsFlipped(false);
      setRomajiInput('');
      setIsCorrect(null);
    }
  }, [currentIndex]);

  const handleFlip = useCallback(() => {
    setIsFlipped(!isFlipped);
  }, [isFlipped]);

  const handleShuffle = useCallback(() => {
    setWords(prev => {
      const shuffled = [...prev];
      for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
      }
      return shuffled;
    });
    setCurrentIndex(0);
    setIsFlipped(false);
    setRomajiInput('');
    setIsCorrect(null);
    toast.success('已打乱顺序');
  }, []);

  const handleRomajiSubmit = useCallback(() => {
    if (!currentWord) return;
    
    const userInput = normalizeRomaji(romajiInput);
    const correctAnswer = normalizeRomaji(currentWord.romaji);
    const correct = userInput === correctAnswer || userInput.length > 0 && correctAnswer.includes(userInput) && userInput.length >= correctAnswer.length - 2;
    
    setIsCorrect(correct);
    setIsFlipped(true);
    
    // 发音
    speakJapanese(currentWord.japanese);

    // 更新进度
    if (user) {
      api.updateProgress(currentWord.id, correct);
    }

    // 答对自动跳到下一个
    if (correct) {
      toast.success('✓ 正确！');
      advanceTimer.current = setTimeout(() => {
        goNext();
      }, 1500);
    }
  }, [currentWord, romajiInput, user, goNext]);

  const handleRevealAnswer = useCallback(() => {
    if (!currentWord) return;
    setIsCorrect(false);
    setIsFlipped(true);
    speakJapanese(currentWord.japanese);
    if (user) {
      api.updateProgress(currentWord.id, false);
    }
  }, [currentWord, user]);

  // 键盘快捷键
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // 如果在输入框中，只处理 Enter
      if (e.target instanceof HTMLInputElement) {
        if (e.key === 'Enter') {
          e.preventDefault();
          handleRomajiSubmit();
        }
        return;
      }
      
      switch (e.key) {
        case ' ':
          e.preventDefault();
          if (isFlipped) goNext();
          else handleFlip();
          break;
        case 'ArrowLeft':
          e.preventDefault();
          goPrevious();
          break;
        case 'ArrowRight':
          e.preventDefault();
          if (isFlipped) goNext();
          else handleFlip();
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isFlipped, goNext, goPrevious, handleFlip, handleRomajiSubmit]);

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

  if (words.length === 0 || !currentWord) {
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
      <div className="flex items-center justify-between flex-wrap gap-2">
        <h1 className="text-3xl font-bold link-hover-effect">词汇学习</h1>
        <div className="flex items-center gap-2 flex-wrap">
          <select
            value={jlptFilter}
            onChange={(e) => setJlptFilter(e.target.value)}
            className="px-3 py-2 border rounded-md dropdown-animated bg-white"
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
            {showRomajiInput ? '浏览' : '拼写'}模式
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setAutoSpeak(!autoSpeak)}
            className="button-hover-effect"
          >
            <Volume2 className={`h-4 w-4 ${autoSpeak ? 'text-blue-600' : 'text-gray-400'}`} />
            {autoSpeak ? '发音开' : '发音关'}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={handleShuffle}
            className="button-hover-effect"
          >
            <Shuffle className="h-4 w-4" />
            打乱
          </Button>
        </div>
      </div>

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
              <p className="text-amber-600 mt-2 text-xs">
                安装完成后刷新页面即可使用发音功能
              </p>
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

      {/* Progress */}
      <div className="space-y-2">
        <div className="flex justify-between text-sm text-gray-600">
          <span>进度</span>
          <span className="font-semibold">{currentIndex + 1} / {words.length}</span>
        </div>
        <Progress value={((currentIndex + 1) / words.length) * 100} className="progress-animated" />
      </div>

      {/* Flashcard */}
      <Card className={`min-h-[420px] flex flex-col justify-center card-hover-effect transition-all duration-300 ${isCorrect === true ? 'ring-2 ring-green-500' : isCorrect === false ? 'ring-2 ring-red-500' : ''}`}>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Badge variant="secondary" className="badge-ping">{currentWord.jlpt_level}</Badge>
              <Badge variant="outline">{currentWord.category}</Badge>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => speakJapanese(currentWord.japanese)}
              className="gap-1"
            >
              <Volume2 className="h-5 w-5 text-blue-600" />
              <span className="text-sm">朗读</span>
            </Button>
          </div>
        </CardHeader>
        <CardContent className="flex-1 flex flex-col items-center justify-center space-y-6">
          {!isFlipped ? (
            /* Front of card - Japanese word */
            <div className="text-center space-y-4 w-full">
              <div className="text-6xl font-bold text-primary mb-4">
                {currentWord.japanese}
              </div>
              
              {!showRomajiInput ? (
                <>
                  <div className="text-2xl text-gray-600">
                    {currentWord.hiragana}
                  </div>
                  <div className="flex gap-3 justify-center pt-4">
                    <Button onClick={handleFlip} size="lg" className="button-hover-effect button-click-effect gap-2">
                      查看意思 <ArrowRight className="h-4 w-4" />
                    </Button>
                    <Button onClick={() => speakJapanese(currentWord.japanese)} variant="outline" size="lg" className="gap-2">
                      <Volume2 className="h-5 w-5" /> 朗读
                    </Button>
                  </div>
                </>
              ) : (
                <>
                  <div className="text-2xl text-gray-400">
                    {currentWord.hiragana}
                  </div>
                  <div className="w-full max-w-md space-y-3 mx-auto">
                    <p className="text-sm text-gray-600">输入罗马音（按 Enter 提交）：</p>
                    <Input
                      ref={inputRef}
                      type="text"
                      placeholder="输入罗马音..."
                      value={romajiInput}
                      onChange={(e) => setRomajiInput(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') {
                          e.preventDefault();
                          handleRomajiSubmit();
                        }
                      }}
                      className="text-lg input-focus-effect text-center"
                      autoComplete="off"
                      autoCapitalize="off"
                      spellCheck={false}
                    />
                    <div className="flex gap-2 justify-center">
                      <Button onClick={handleRomajiSubmit} className="button-click-effect gap-1">
                        <Check className="h-4 w-4" /> 提交
                      </Button>
                      <Button onClick={handleRevealAnswer} variant="outline" className="gap-1">
                        <Eye className="h-4 w-4" /> 看答案
                      </Button>
                    </div>
                  </div>
                </>
              )}
            </div>
          ) : (
            /* Back of card - Meaning + Result */
            <div className="text-center space-y-5 w-full">
              {/* 反馈结果 */}
              {isCorrect !== null && (
                <div className={`inline-flex items-center gap-2 px-6 py-3 rounded-full text-xl font-bold ${
                  isCorrect 
                    ? 'bg-green-100 text-green-700' 
                    : 'bg-red-100 text-red-700'
                }`}>
                  {isCorrect ? (
                    <><Check className="h-6 w-6" /> 正确！</>
                  ) : (
                    <><X className="h-6 w-6" /> 错误</>
                  )}
                </div>
              )}

              {/* 单词信息 */}
              <div className="space-y-3 card-enter">
                <div className="text-4xl font-bold text-primary">
                  {currentWord.japanese}
                </div>
                <div className="text-xl text-gray-600">
                  {currentWord.hiragana}
                </div>
                <div className="text-lg text-blue-600 font-mono">
                  {currentWord.romaji}
                </div>
                
                {/* 如果错了，显示你输入的 vs 正确答案 */}
                {isCorrect === false && romajiInput && (
                  <div className="bg-red-50 border border-red-200 rounded-lg px-4 py-2 text-sm">
                    <span className="text-gray-500">你的输入：</span>
                    <span className="text-red-600 font-mono">{romajiInput}</span>
                    <span className="text-gray-400 mx-2">→</span>
                    <span className="text-gray-500">正确答案：</span>
                    <span className="text-green-600 font-mono">{currentWord.romaji}</span>
                  </div>
                )}
                
                <div className="bg-blue-50 rounded-lg px-4 py-3 inline-block">
                  <p className="text-sm text-gray-500 mb-1">中文释义</p>
                  <div className="text-2xl font-semibold space-y-1">
                    {(currentWord.meaning_zh || currentWord.meaning_en || '').split(/[,;，；]/).filter((s: string) => s.trim()).map((part: string, i: number) => (
                      <div key={i} className="leading-relaxed">{part.trim()}</div>
                    ))}
                  </div>
                </div>
                
                {currentWord.meaning_en && currentWord.meaning_z && (
                  <p className="text-lg text-gray-500">{currentWord.meaning_en}</p>
                )}
              </div>
              
              {/* 操作按钮 */}
              <div className="flex gap-3 justify-center pt-2">
                {!isCorrect && showRomajiInput && (
                  <Button 
                    onClick={() => {
                      setIsFlipped(false);
                      setRomajiInput('');
                      setIsCorrect(null);
                      inputRef.current?.focus();
                    }} 
                    variant="outline"
                    className="gap-2"
                  >
                    <RotateCcw className="h-4 w-4" /> 重新输入
                  </Button>
                )}
                <Button onClick={() => speakJapanese(currentWord.japanese)} variant="outline" className="gap-2">
                  <Volume2 className="h-5 w-5 text-blue-600" /> 再读一遍
                </Button>
                <Button onClick={goNext} size="lg" className="gap-2 button-hover-effect button-click-effect">
                  下一个 <ArrowRight className="h-4 w-4" />
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Navigation */}
      <div className="flex items-center justify-between">
        <Button
          onClick={goPrevious}
          disabled={currentIndex === 0}
          variant="outline"
          className="nav-button"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          上一个
        </Button>
        
        <div className="text-sm text-gray-400">
          空格 = 翻转/下一个 · ← → = 切换
        </div>
        
        <Button
          onClick={goNext}
          variant="outline"
          className="nav-button"
        >
          下一个
          <ArrowRight className="ml-2 h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
