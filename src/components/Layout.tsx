import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Menu, X, User, BookOpen, BarChart3, CreditCard, Star, List } from 'lucide-react';

export default function Layout({ children }: { children: React.ReactNode }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();
  const { user, logout } = useAuth();

  const navigation = [
    { name: '首页', href: '/', icon: null },
    { name: '闪卡学习', href: '/vocabulary', icon: BookOpen },
    { name: '词汇浏览', href: '/vocab-list', icon: List },
    { name: '我的收藏', href: '/favorites', icon: Star, requireAuth: true },
    { name: '学习统计', href: '/dashboard', icon: BarChart3, requireAuth: true },
    { name: '订阅升级', href: '/pricing', icon: CreditCard },
  ];

  const isActive = (path: string) => location.pathname === path;

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Navigation */}
      <nav className="border-b bg-white/95 backdrop-blur sticky top-0 z-50">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 justify-between">
            <div className="flex items-center">
              <Link to="/" className="flex items-center gap-2">
                <span className="text-2xl">🇯🇵</span>
                <span className="font-bold text-xl hidden sm:inline">日语学习</span>
              </Link>
            </div>

            {/* Desktop navigation */}
            <div className="hidden lg:flex lg:items-center lg:space-x-1">
              {navigation.map((item) => {
                if (item.requireAuth && !user) return null;
                const Icon = item.icon;
                return (
                  <Link
                    key={item.href}
                    to={item.href}
                    className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                      isActive(item.href)
                        ? 'bg-primary text-primary-foreground'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    <span className="flex items-center gap-1">
                      {Icon && <Icon className="h-4 w-4" />}
                      {item.name}
                    </span>
                  </Link>
                );
              })}
            </div>

            {/* User menu */}
            <div className="flex items-center gap-4">
              {user ? (
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="sm" className="gap-2 max-w-[200px]">
                      <User className="h-4 w-4 flex-shrink-0" />
                      <span className="truncate">{user.name || user.email}</span>
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem disabled>
                      {user.is_premium ? '⭐ 永久会员' : '免费用户'}
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={logout}>
                      退出登录
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              ) : (
                <div className="hidden sm:flex gap-2">
                  <Button variant="ghost" size="sm" asChild>
                    <Link to="/login">登录</Link>
                  </Button>
                  <Button size="sm" asChild>
                    <Link to="/register">注册</Link>
                  </Button>
                </div>
              )}

              {/* Mobile menu button */}
              <Button
                variant="ghost"
                size="sm"
                className="lg:hidden"
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              >
                {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
              </Button>
            </div>
          </div>
        </div>

        {/* Mobile menu */}
        {mobileMenuOpen && (
          <div className="lg:hidden border-t">
            <div className="space-y-1 px-4 pb-3 pt-2">
              {navigation.map((item) => {
                if (item.requireAuth && !user) return null;
                const Icon = item.icon;
                return (
                  <Link
                    key={item.href}
                    to={item.href}
                    onClick={() => setMobileMenuOpen(false)}
                    className={`flex items-center gap-2 px-3 py-2 rounded-md text-base font-medium ${
                      isActive(item.href)
                        ? 'bg-primary text-primary-foreground'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    {Icon && <Icon className="h-4 w-4" />}
                    {item.name}
                  </Link>
                );
              })}
              {!user && (
                <div className="flex gap-2 pt-2">
                  <Button variant="ghost" asChild className="flex-1">
                    <Link to="/login" onClick={() => setMobileMenuOpen(false)}>登录</Link>
                  </Button>
                  <Button asChild className="flex-1">
                    <Link to="/register" onClick={() => setMobileMenuOpen(false)}>注册</Link>
                  </Button>
                </div>
              )}
            </div>
          </div>
        )}
      </nav>

      {/* Main content */}
      <main className="flex-1 mx-auto max-w-7xl w-full px-4 py-6 sm:px-6 lg:px-8">
        {children}
      </main>

      {/* Footer */}
      <footer className="border-t bg-white py-6 mt-auto">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <p className="text-center text-sm text-gray-500">
            © 2026 日语学习 · JLPT N5-N1 词汇学习平台 · 8000+词汇
          </p>
        </div>
      </footer>
    </div>
  );
}
