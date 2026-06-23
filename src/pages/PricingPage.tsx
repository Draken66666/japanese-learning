import { useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Check, Crown, Sparkles, KeyRound, Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import { api } from '@/services/api';

export default function PricingPage() {
  const { user, refreshUser } = useAuth();
  const [activationCode, setActivationCode] = useState('');
  const [activating, setActivating] = useState(false);
  const navigate = useNavigate();

  const handleActivate = async () => {
    if (!user) {
      toast.error('请先登录');
      navigate('/login');
      return;
    }

    if (!activationCode.trim()) {
      toast.error('请输入激活码');
      return;
    }

    setActivating(true);
    try {
      const result = await api.activateWithCode(activationCode);
      if (result.success) {
        toast.success(result.message);
        await refreshUser();
        setActivationCode('');
        navigate('/dashboard');
      } else {
        toast.error(result.message);
      }
    } catch (error) {
      toast.error('操作失败，请稍后重试');
    } finally {
      setActivating(false);
    }
  };

  const plan = {
    name: '永久会员',
    price: 49.9,
    duration: '一次性买断',
    features: [
      '解锁全部 JLPT 等级词汇 (N5-N1)',
      '8000+ 词汇全部开放',
      '词汇搜索与筛选功能',
      '词汇收藏功能',
      '详细学习统计与进度追踪',
      '错误回顾与智能复习',
      '终身免费更新',
      '无订阅压力，一次付费永久使用',
    ],
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8 page-enter">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">选择你的学习计划</h1>
        <p className="text-xl text-gray-600">
          一次性买断，终身使用，无订阅压力
        </p>
      </div>

      {user?.is_premium && (
        <Card className="bg-yellow-50 border-yellow-200">
          <CardContent className="pt-6">
            <div className="flex items-center justify-center gap-2 text-yellow-800">
              <Crown className="h-5 w-5" />
              <p className="font-semibold">您已是永久会员！终身享受所有功能。</p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Pricing Card */}
      <div className="max-w-md mx-auto">
        <Card className="relative border-primary shadow-lg">
          <Badge className="absolute -top-3 left-1/2 -translate-x-1/2">
            <Sparkles className="h-3 w-3 mr-1" />
            推荐
          </Badge>

          <CardHeader className="text-center">
            <CardTitle className="text-2xl">{plan.name}</CardTitle>
            <CardDescription>{plan.duration}</CardDescription>
            <div className="pt-4">
              <span className="text-5xl font-bold">¥{plan.price}</span>
              <span className="text-gray-500"> 一次性</span>
            </div>
          </CardHeader>

          <CardContent>
            <ul className="space-y-3">
              {plan.features.map((feature, index) => (
                <li key={index} className="flex items-start gap-2">
                  <Check className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
                  <span className="text-sm">{feature}</span>
                </li>
              ))}
            </ul>
          </CardContent>

          {!user?.is_premium && (
            <CardFooter className="flex-col gap-4">
              {/* 购买说明 */}
              <div className="w-full bg-blue-50 border border-blue-100 rounded-lg p-4 text-sm text-blue-700 space-y-2">
                <p className="font-semibold flex items-center gap-1">
                  <KeyRound className="h-4 w-4" />
                  如何获取激活码：
                </p>
                <p>1. 微信扫码支付 ¥{plan.price}（添加客服微信）</p>
                <p>2. 支付后获取激活码</p>
                <p>3. 在下方输入激活码解锁全部词汇</p>
              </div>

              {/* 激活码输入 */}
              <div className="w-full space-y-2">
                <Label htmlFor="code">输入激活码</Label>
                <div className="flex gap-2">
                  <Input
                    id="code"
                    placeholder="请输入激活码..."
                    value={activationCode}
                    onChange={(e) => setActivationCode(e.target.value)}
                    className="flex-1"
                  />
                  <Button
                    onClick={handleActivate}
                    disabled={activating}
                    className="button-hover-effect button-click-effect"
                  >
                    {activating ? (
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    ) : (
                      <KeyRound className="mr-2 h-4 w-4" />
                    )}
                    激活
                  </Button>
                </div>
              </div>

              <p className="text-xs text-gray-400 text-center">
                支付后请联系客服获取激活码，输入后立即解锁
              </p>
            </CardFooter>
          )}
        </Card>
      </div>

      {/* Free vs Premium comparison */}
      <div className="max-w-3xl mx-auto pt-8">
        <div className="grid md:grid-cols-2 gap-4">
          <Card className="border-gray-200">
            <CardHeader>
              <CardTitle className="text-lg text-gray-700">免费版</CardTitle>
              <CardDescription>¥0 / 永久</CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-center gap-2"><Check className="h-4 w-4 text-green-600" /> N5 词汇 (662词)</li>
                <li className="flex items-center gap-2"><Check className="h-4 w-4 text-green-600" /> 闪卡学习模式</li>
                <li className="flex items-center gap-2"><Check className="h-4 w-4 text-green-600" /> 基础学习统计</li>
                <li className="flex items-center gap-2 text-gray-400">✗ N4-N1 词汇</li>
                <li className="flex items-center gap-2 text-gray-400">✗ 词汇搜索与收藏</li>
                <li className="flex items-center gap-2 text-gray-400">✗ 高级复习功能</li>
              </ul>
            </CardContent>
          </Card>

          <Card className="border-primary">
            <CardHeader>
              <CardTitle className="text-lg text-primary">永久会员</CardTitle>
              <CardDescription>¥{plan.price} / 一次性买断</CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm">
                <li className="flex items-center gap-2"><Check className="h-4 w-4 text-green-600" /> 全部 JLPT 词汇 (8000+词)</li>
                <li className="flex items-center gap-2"><Check className="h-4 w-4 text-green-600" /> 闪卡学习模式</li>
                <li className="flex items-center gap-2"><Check className="h-4 w-4 text-green-600" /> 详细学习统计</li>
                <li className="flex items-center gap-2"><Check className="h-4 w-4 text-green-600" /> 词汇搜索与收藏</li>
                <li className="flex items-center gap-2"><Check className="h-4 w-4 text-green-600" /> 智能复习功能</li>
                <li className="flex items-center gap-2"><Check className="h-4 w-4 text-green-600" /> 终身免费更新</li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* FAQ */}
      <div className="max-w-2xl mx-auto space-y-4 pt-8">
        <h2 className="text-2xl font-bold text-center mb-6">常见问题</h2>
        <Card>
          <CardHeader><CardTitle className="text-base">一次性买断包含什么？</CardTitle></CardHeader>
          <CardContent>
            <p className="text-gray-600 text-sm">解锁全部JLPT等级词汇（N5-N1，共8000+词），以及所有高级功能。无需月付或年付，一次付费终身使用。</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle className="text-base">如何购买？</CardTitle></CardHeader>
          <CardContent>
            <p className="text-gray-600 text-sm">通过微信或支付宝扫码支付 ¥{plan.price}，支付后联系客服获取激活码。在定价页输入激活码即可立即解锁全部内容。</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle className="text-base">激活码怎么用？</CardTitle></CardHeader>
          <CardContent>
            <p className="text-gray-600 text-sm">注册登录后，在定价页输入激活码，点击"激活"按钮即可。激活后永久有效，无需重复输入。</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle className="text-base">可以退款吗？</CardTitle></CardHeader>
          <CardContent>
            <p className="text-gray-600 text-sm">购买后7天内，如果您对产品不满意，可以申请全额退款。请联系客服处理退款事宜。</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
