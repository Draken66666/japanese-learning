import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { BookOpen, Search, Star, TrendingUp, ChevronRight, Sparkles, Lock } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { api } from '@/services/api';

export default function HomePage() {
  const { user } = useAuth();
  const [vocabStats, setVocabStats] = useState<any>(null);

  useEffect(() => {
    api.getVocabStats().then(data => setVocabStats(data.stats)).catch(() => {});
  }, []);

  const features = [
    {
      icon: <BookOpen className="h-8 w-8 text-blue-600" />,
      title: '闪卡学习',
      description: '通过闪卡式学习界面，掌握日语词汇的假名、汉字和罗马音',
    },
    {
      icon: <Search className="h-8 w-8 text-green-600" />,
      title: '搜索浏览',
      description: '搜索8000+词汇，按JLPT等级和词性筛选，快速找到需要的单词',
    },
    {
      icon: <Star className="h-8 w-8 text-yellow-600" />,
      title: '收藏复习',
      description: '收藏生词，随时回顾，配合智能复习系统高效记忆',
    },
    {
      icon: <TrendingUp className="h-8 w-8 text-purple-600" />,
      title: '进度追踪',
      description: '追踪学习进度，查看掌握情况和正确率，科学提升日语水平',
    },
  ];

  const jlptLevels = [
    { level: 'N5', description: '基础入门', count: vocabStats?.byLevel?.N5 || 662, color: 'bg-green-100 text-green-800', free: true },
    { level: 'N4', description: '基础', count: vocabStats?.byLevel?.N4 || 632, color: 'bg-blue-100 text-blue-800', premium: true },
    { level: 'N3', description: '中级', count: vocabStats?.byLevel?.N3 || 1784, color: 'bg-yellow-100 text-yellow-800', premium: true },
    { level: 'N2', description: '中高级', count: vocabStats?.byLevel?.N2 || 1792, color: 'bg-orange-100 text-orange-800', premium: true },
    { level: 'N1', description: '高级', count: vocabStats?.byLevel?.N1 || 3463, color: 'bg-red-100 text-red-800', premium: true },
  ];

  const totalVocab = vocabStats?.total || 8333;

  return (
    <div className="space-y-16 page-enter">
      {/* Hero Section */}
      <section className="text-center py-8 sm:py-12">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-4xl sm:text-5xl font-bold tracking-tight mb-4">
            轻松学习
            <span className="text-primary"> 日语</span>
          </h1>
          <p className="text-lg sm:text-xl text-gray-600 mb-8">
            {totalVocab.toLocaleString()}+ JLPT 词汇 · 闪卡学习 · 智能复习 · 一次性买断
          </p>
          <div className="flex flex-wrap gap-4 justify-center">
            {user ? (
              <Button size="lg" asChild className="button-hover-effect button-click-effect">
                <Link to="/vocabulary">
                  开始学习 <ChevronRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
            ) : (
              <>
                <Button size="lg" asChild className="button-hover-effect button-click-effect">
                  <Link to="/register">
                    免费注册 <ChevronRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
                <Button size="lg" variant="outline" asChild className="button-hover-effect">
                  <Link to="/vocab-list">浏览词汇</Link>
                </Button>
              </>
            )}
          </div>
        </div>
      </section>

      {/* Stats Banner */}
      <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="text-center">
          <CardContent className="pt-6">
            <div className="text-3xl font-bold text-primary">{totalVocab.toLocaleString()}+</div>
            <p className="text-sm text-gray-500 mt-1">JLPT词汇</p>
          </CardContent>
        </Card>
        <Card className="text-center">
          <CardContent className="pt-6">
            <div className="text-3xl font-bold text-green-600">5</div>
            <p className="text-sm text-gray-500 mt-1">JLPT等级</p>
          </CardContent>
        </Card>
        <Card className="text-center">
          <CardContent className="pt-6">
            <div className="text-3xl font-bold text-blue-600">8</div>
            <p className="text-sm text-gray-500 mt-1">词性分类</p>
          </CardContent>
        </Card>
        <Card className="text-center">
          <CardContent className="pt-6">
            <div className="text-3xl font-bold text-purple-600">¥49.9</div>
            <p className="text-sm text-gray-500 mt-1">永久买断</p>
          </CardContent>
        </Card>
      </section>

      {/* Features Section */}
      <section>
        <h2 className="text-2xl sm:text-3xl font-bold text-center mb-8 sm:mb-12">核心功能</h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <Card key={index} className="card-hover-effect">
              <CardHeader>
                <div className="mb-4">{feature.icon}</div>
                <CardTitle>{feature.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-base">
                  {feature.description}
                </CardDescription>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* JLPT Levels Section */}
      <section className="bg-white rounded-2xl p-6 sm:p-8">
        <h2 className="text-2xl sm:text-3xl font-bold text-center mb-4">JLPT等级分类</h2>
        <p className="text-center text-gray-600 mb-8">选择适合你水平的等级开始学习</p>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
          {jlptLevels.map((item, index) => (
            <div
              key={item.level}
              className={`px-4 py-6 rounded-xl text-center card-enter ${item.color}`}
              style={{animationDelay: `${index * 0.1}s`}}
            >
              <div className="text-2xl font-bold mb-1">{item.level}</div>
              <div className="text-sm opacity-80 mb-2">{item.description}</div>
              <div className="text-lg font-semibold">{item.count.toLocaleString()} 词</div>
              {item.premium ? (
                <div className="mt-2 inline-flex items-center gap-1 text-xs bg-white/50 px-2 py-0.5 rounded-full">
                  <Lock className="h-3 w-3" />
                  会员
                </div>
              ) : (
                <div className="mt-2 inline-flex items-center gap-1 text-xs bg-white/50 px-2 py-0.5 rounded-full">
                  免费
                </div>
              )}
            </div>
          ))}
        </div>
        <p className="text-center text-sm text-gray-500 mt-4">
          * N5 等级免费开放（662词），N4-N1 需要升级会员
        </p>
      </section>

      {/* CTA Section */}
      {!user?.is_premium && (
        <section className="text-center bg-primary text-primary-foreground rounded-2xl p-8 sm:p-12 card-hover-effect">
          <h2 className="text-2xl sm:text-3xl font-bold mb-4">
            {user ? '解锁全部 8000+ 词汇' : '准备好开始学习了吗？'}
          </h2>
          <p className="text-lg sm:text-xl mb-8 opacity-90">
            {user ? '一次性买断 ¥49.9，终身使用' : '免费注册，立即开始日语学习之旅'}
          </p>
          <Button size="lg" variant="secondary" asChild className="button-hover-effect button-click-effect">
            {user ? (
              <Link to="/pricing">
                <Sparkles className="mr-2 h-4 w-4" />
                升级永久会员
              </Link>
            ) : (
              <Link to="/register">立即注册 - 免费</Link>
            )}
          </Button>
        </section>
      )}
    </div>
  );
}
