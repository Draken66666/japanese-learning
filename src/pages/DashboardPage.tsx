import { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import { api } from '@/services/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { 
  BookOpen, 
  CheckCircle, 
  XCircle, 
  TrendingUp,
  Award,
  Target
} from 'lucide-react';
import { toast } from 'sonner';
import type { LearningStats } from '@/types';

export default function DashboardPage() {
  const { user } = useAuth();
  const [stats, setStats] = useState<LearningStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      loadStats();
    }
  }, [user]);

  const loadStats = async () => {
    try {
      const data = await api.getStats();
      setStats(data.stats);
    } catch (error) {
      toast.error('加载统计数据失败');
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">请先登录查看学习统计</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  const masteryPercentage = stats && stats.total_words_learned > 0
    ? Math.round((stats.mastered / stats.total_words_learned) * 100)
    : 0;

  return (
    <div className="max-w-6xl mx-auto space-y-8 page-enter">
      <h1 className="text-3xl font-bold link-hover-effect">学习仪表盘</h1>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="card-hover-effect card-enter">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">已学词汇</CardTitle>
            <BookOpen className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_words_learned || 0}</div>
            <p className="text-xs text-muted-foreground">
              共 {stats?.total_vocabulary || 0} 个词汇
            </p>
          </CardContent>
        </Card>

        <Card className="card-hover-effect card-enter" style={{animationDelay: '0.1s'}}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">已掌握</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats?.mastered || 0}</div>
            <p className="text-xs text-muted-foreground">
              掌握率 {masteryPercentage}%
            </p>
          </CardContent>
        </Card>

        <Card className="card-hover-effect card-enter" style={{animationDelay: '0.2s'}}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">正确率</CardTitle>
            <Target className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{stats?.accuracy || 0}%</div>
            <p className="text-xs text-muted-foreground">
              正确 {stats?.total_correct || 0} / 错误 {stats?.total_incorrect || 0}
            </p>
          </CardContent>
        </Card>

        <Card className="card-hover-effect card-enter" style={{animationDelay: '0.3s'}}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">会员状态</CardTitle>
            <Award className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {user.is_premium ? (
                <span className="text-yellow-600">高级</span>
              ) : (
                <span className="text-gray-600">免费</span>
              )}
            </div>
            {user.is_premium && (
              <p className="text-xs text-muted-foreground">
                有效期至{' '}
                {stats && 'premium_expires_at' in stats && stats.premium_expires_at && typeof stats.premium_expires_at === 'string'
                  ? new Date(stats.premium_expires_at).toLocaleDateString('zh-CN')
                  : '永久'}
              </p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Mastery Progress */}
      <Card className="card-hover-effect">
        <CardHeader>
          <CardTitle>掌握进度</CardTitle>
          <CardDescription>
            你已经学习了 {stats?.total_words_learned || 0} 个词汇，其中 {stats?.mastered || 0} 个已掌握
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>总体进度</span>
              <span>{stats?.total_words_learned || 0} / {stats?.total_vocabulary || 0}</span>
            </div>
            <Progress 
              value={stats && stats.total_vocabulary > 0 
                ? (stats.total_words_learned / stats.total_vocabulary) * 100 
                : 0
              }
              className="progress-animated"
            />
          </div>
        </CardContent>
      </Card>

      {/* Learning Activity */}
      <div className="grid md:grid-cols-2 gap-6">
        <Card className="card-hover-effect">
          <CardHeader>
            <CardTitle>学习统计</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <span className="text-sm">正确次数</span>
              </div>
              <span className="font-bold text-green-600">{stats?.total_correct || 0}</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <XCircle className="h-4 w-4 text-red-600" />
                <span className="text-sm">错误次数</span>
              </div>
              <span className="font-bold text-red-600">{stats?.total_incorrect || 0}</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <TrendingUp className="h-4 w-4 text-blue-600" />
                <span className="text-sm">正确率</span>
              </div>
              <span className="font-bold">{stats?.accuracy || 0}%</span>
            </div>
          </CardContent>
        </Card>

        <Card className="card-hover-effect">
          <CardHeader>
            <CardTitle>快速操作</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <Button className="w-full button-hover-effect button-click-effect" asChild>
              <a href="/vocabulary">继续学习</a>
            </Button>
            {!user.is_premium && (
              <Button variant="outline" className="w-full button-hover-effect" asChild>
                <a href="/pricing">升级高级会员</a>
              </Button>
            )}
            <Button 
              variant="destructive" 
              className="w-full button-hover-effect"
              onClick={async () => {
                if (confirm('确定要重置所有学习进度吗？此操作不可撤销。')) {
                  try {
                    await api.resetProgress();
                    toast.success('学习进度已重置');
                    loadStats();
                  } catch (error) {
                    toast.error('重置失败');
                  }
                }
              }}
            >
              重置学习进度
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
