import { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription
} from '@/components/ui/dialog';
import { Check, Crown, Sparkles, QrCode, Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import { api } from '@/services/api';

export default function PricingPage() {
  const { user, refreshUser } = useAuth();
  const [processing, setProcessing] = useState<string | null>(null);
  const [paymentDialog, setPaymentDialog] = useState(false);
  const [paymentMethod, setPaymentMethod] = useState<'wechat' | 'alipay'>('wechat');
  const [orderInfo, setOrderInfo] = useState<any>(null);
  const [confirming, setConfirming] = useState(false);
  const [paymentConfig, setPaymentConfig] = useState<any>(null);
  const navigate = useNavigate();

  useEffect(() => {
    api.getPaymentConfig().then(data => setPaymentConfig(data)).catch(() => {});
  }, []);

  const handlePurchase = async (method: 'wechat' | 'alipay') => {
    if (!user) {
      toast.error('请先登录');
      navigate('/login');
      return;
    }

    if (user.is_premium) {
      toast.success('您已是永久会员！');
      return;
    }

    setPaymentMethod(method);
    setProcessing(method);

    try {
      const data = await api.createPaymentOrder(method);

      if (data.error === 'ALREADY_PREMIUM') {
        toast.success('您已是永久会员！');
        return;
      }

      if (data.success) {
        setOrderInfo(data);
        setPaymentDialog(true);
      } else {
        toast.error(data.message || '创建订单失败');
      }
    } catch (error) {
      toast.error('支付处理失败，请稍后重试');
    } finally {
      setProcessing(null);
    }
  };

  const handleConfirmPayment = async () => {
    if (!orderInfo) return;

    setConfirming(true);
    try {
      const data = await api.confirmPayment(orderInfo.orderId, paymentMethod);

      if (data.success && data.is_premium) {
        toast.success('支付成功！已为您激活永久会员！');
        setPaymentDialog(false);
        await refreshUser?.();
        navigate('/dashboard');
      } else if (data.success && data.status === 'pending_verification') {
        toast.success(data.message || '支付确认已提交，请等待审核');
        setPaymentDialog(false);
      } else {
        toast.error(data.message || '支付确认失败');
      }
    } catch (error) {
      toast.error('操作失败，请稍后重试');
    } finally {
      setConfirming(false);
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
            <CardFooter className="flex-col gap-3">
              <div className="w-full text-center text-sm text-gray-500 mb-2">选择支付方式</div>
              <div className="grid grid-cols-2 gap-3 w-full">
                <Button
                  className="w-full bg-green-600 hover:bg-green-700"
                  onClick={() => handlePurchase('wechat')}
                  disabled={processing !== null}
                >
                  {processing === 'wechat' ? (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  ) : (
                    <span className="mr-2">💚</span>
                  )}
                  微信支付
                </Button>
                <Button
                  className="w-full bg-blue-500 hover:bg-blue-600"
                  onClick={() => handlePurchase('alipay')}
                  disabled={processing !== null}
                >
                  {processing === 'alipay' ? (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  ) : (
                    <span className="mr-2">💙</span>
                  )}
                  支付宝
                </Button>
              </div>
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
          <CardHeader><CardTitle className="text-base">支付安全吗？</CardTitle></CardHeader>
          <CardContent>
            <p className="text-gray-600 text-sm">我们使用微信支付和支付宝进行收款，支付过程在官方平台完成，确保您的资金安全。</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle className="text-base">如何激活会员？</CardTitle></CardHeader>
          <CardContent>
            <p className="text-gray-600 text-sm">选择微信或支付宝扫码支付后，点击"我已支付"按钮即可。系统会在确认后自动为您激活永久会员。</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle className="text-base">可以退款吗？</CardTitle></CardHeader>
          <CardContent>
            <p className="text-gray-600 text-sm">购买后7天内，如果您对产品不满意，可以申请全额退款。请联系客服处理退款事宜。</p>
          </CardContent>
        </Card>
      </div>

      {/* Payment Dialog */}
      <Dialog open={paymentDialog} onOpenChange={setPaymentDialog}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="text-center">扫码支付 ¥{plan.price}</DialogTitle>
            <DialogDescription className="text-center">
              {paymentMethod === 'wechat' ? '请使用微信扫描二维码' : '请使用支付宝扫描二维码'}
            </DialogDescription>
          </DialogHeader>

          <div className="flex flex-col items-center space-y-4 py-4">
            {/* QR Code */}
            <div className="w-64 h-64 border-2 border-gray-200 rounded-lg flex items-center justify-center bg-gray-50">
              {orderInfo?.qrCodeUrl ? (
                <img
                  src={orderInfo.qrCodeUrl}
                  alt="支付二维码"
                  className="w-full h-full object-contain p-2"
                />
              ) : (
                <div className="text-center p-4">
                  <QrCode className="h-16 w-16 text-gray-300 mx-auto mb-2" />
                  <p className="text-sm text-gray-500">
                    {paymentConfig?.mode === 'qrcode'
                      ? '管理员尚未配置收款二维码，请联系管理员。'
                      : '二维码生成中...'}
                  </p>
                  {orderInfo?.orderId && (
                    <p className="text-xs text-gray-400 mt-2">订单号: {orderInfo.orderId}</p>
                  )}
                </div>
              )}
            </div>

            {/* Order Info */}
            <div className="text-center space-y-1 w-full">
              <p className="text-lg font-semibold text-primary">{plan.name}</p>
              <p className="text-2xl font-bold">¥{plan.price}</p>
              {orderInfo?.orderId && (
                <p className="text-xs text-gray-400">订单号: {orderInfo.orderId}</p>
              )}
            </div>

            {/* Payment Instructions */}
            <div className="bg-blue-50 border border-blue-100 rounded-lg p-3 w-full text-sm text-blue-700">
              <p>1. 使用{paymentMethod === 'wechat' ? '微信' : '支付宝'}扫描上方二维码</p>
              <p>2. 支付金额：<strong>¥{plan.price}</strong></p>
              <p>3. 支付完成后，点击下方按钮确认</p>
            </div>

            {/* Confirm Button */}
            <Button
              className="w-full"
              size="lg"
              onClick={handleConfirmPayment}
              disabled={confirming}
            >
              {confirming ? (
                <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> 确认中...</>
              ) : (
                <><Check className="mr-2 h-4 w-4" /> 我已支付，确认激活</>
              )}
            </Button>

            <Button
              variant="ghost"
              size="sm"
              onClick={() => setPaymentDialog(false)}
              className="text-gray-400"
            >
              取消
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
