import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { CheckCircle, Loader2 } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';

export default function PaymentSuccessPage() {
  const navigate = useNavigate();
  const { refreshUser } = useAuth();
  const [status, setStatus] = useState<'loading' | 'success'>('loading');

  useEffect(() => {
    const timer = setTimeout(async () => {
      await refreshUser();
      setStatus('success');
    }, 1500);
    return () => clearTimeout(timer);
  }, [refreshUser]);

  return (
    <div className="max-w-md mx-auto py-12">
      {status === 'loading' && (
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-primary mx-auto mb-4" />
          <p className="text-gray-600">正在确认...</p>
        </div>
      )}

      {status === 'success' && (
        <Card className="border-green-200 bg-green-50">
          <CardContent className="pt-6 text-center space-y-4">
            <CheckCircle className="h-16 w-16 text-green-600 mx-auto" />
            <h1 className="text-2xl font-bold text-green-800">激活成功！</h1>
            <p className="text-gray-600">
              恭喜您成为永久会员！现在可以访问全部 8000+ 词汇了。
            </p>
            <div className="flex flex-col gap-2 pt-4">
              <Button onClick={() => navigate('/vocabulary')}>
                开始学习
              </Button>
              <Button variant="outline" onClick={() => navigate('/dashboard')}>
                查看学习统计
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
