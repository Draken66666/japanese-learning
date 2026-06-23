# 日语学习网站 - Japanese Learning Website

## 项目概述

一个功能完整的日语学习网站，帮助用户通过科学的方法学习日语词汇。

## 核心功能

### 1. 词汇学习模块
- ✅ 支持罗马音（Romaji）输入模式进行单词记忆练习
- ✅ 提供单词卡片式学习界面，每次专注显示单个词汇
- ✅ 包含假名、汉字与罗马音的对照展示
- ✅ 翻转卡片查看词义
- ✅ 标记"认识"或"不认识"来追踪学习进度

### 2. 页面设计
- ✅ 整洁简约的 UI 风格，减少视觉干扰
- ✅ 响应式布局，兼容桌面端与移动端
- ✅ 清晰的学习进度指示与导航结构
- ✅ 使用 Tailwind CSS 和 shadcn/ui 组件库

### 3. 用户账户与付费系统
- ✅ 支持用户注册与登录功能
- ✅ 免费用户访问基础词汇内容（JLPT N5）
- ✅ 付费解锁完整词库（JLPT N4-N1）、高级练习模式及学习统计功能
- ✅ 集成在线支付流程（模拟），支付成功后自动激活账户权限

### 4. 其他功能
- ✅ 词汇分类管理（按 JLPT 等级或主题分类）
- ✅ 学习记录与错题回顾机制
- ✅ 简洁的用户仪表盘展示学习进度与解锁状态

## 技术栈

### 前端
- React 18 + TypeScript
- Vite (构建工具)
- Tailwind CSS + shadcn/ui
- React Router (路由)
- Sonner (Toast 提示)

### 后端
- Express.js
- SQLite (数据库)
- JWT (身份认证)
- bcryptjs (密码加密)

## 项目结构

```
japanese-learning/
├── server/                 # 后端代码
│   ├── index.js           # 服务器入口
│   ├── db/                # 数据库
│   │   └── database.js    # 数据库初始化和种子数据
│   ├── routes/            # API 路由
│   │   ├── auth.js        # 认证路由
│   │   ├── vocabulary.js  # 词汇路由
│   │   ├── progress.js    # 学习进度路由
│   │   └── payments.js    # 支付路由
│   └── utils/             # 工具函数
│       └── auth.js        # 认证工具
├── src/                   # 前端代码
│   ├── components/        # React 组件
│   │   └── Layout.tsx     # 布局组件
│   ├── context/           # React 上下文
│   │   └── AuthContext.tsx # 认证上下文
│   ├── pages/             # 页面组件
│   │   ├── HomePage.tsx         # 首页
│   │   ├── LoginPage.tsx        # 登录页
│   │   ├── RegisterPage.tsx     # 注册页
│   │   ├── VocabularyPage.tsx  # 词汇学习页
│   │   ├── DashboardPage.tsx    # 仪表盘页
│   │   └── PricingPage.tsx      # 订阅页
│   ├── services/          # 服务层
│   │   └── api.ts         # API 服务
│   ├── types/             # TypeScript 类型
│   │   └── index.ts
│   ├── App.tsx            # 主应用组件
│   ├── main.tsx           # 入口文件
│   └── index.css          # 全局样式
└── dist/                  # 构建输出
```

## 如何运行

### 后端服务器
```bash
cd japanese-learning
node server/index.js
```
运行在 http://localhost:3001

### 前端开发服务器
```bash
cd japanese-learning
npm run dev
```
运行在 http://localhost:5173

## API 端点

### 认证
- POST `/api/auth/register` - 注册
- POST `/api/auth/login` - 登录
- GET `/api/auth/me` - 获取当前用户

### 词汇
- GET `/api/vocabulary` - 获取词汇列表
- GET `/api/vocabulary/:id` - 获取单个词汇
- GET `/api/vocabulary/meta/categories` - 获取分类
- GET `/api/vocabulary/meta/jlpt-levels` - 获取 JLPT 等级

### 学习进度
- GET `/api/progress` - 获取学习进度
- POST `/api/progress/update` - 更新学习进度
- GET `/api/progress/review` - 获取复习词汇
- GET `/api/progress/stats` - 获取学习统计
- DELETE `/api/progress/reset` - 重置学习进度

### 支付
- POST `/api/payments/process` - 处理支付
- GET `/api/payments/history` - 获取支付历史
- GET `/api/payments/status` - 检查会员状态

## 使用说明

1. **注册账号**: 访问 http://localhost:5173/register 创建新账号
2. **登录**: 使用注册的邮箱和密码登录
3. **开始学习**: 进入"词汇学习"页面，选择 JLPT 等级开始学习
4. **闪卡学习**: 
   - 查看日语词汇（汉字和假名）
   - 输入罗马音进行测试（可选）
   - 翻转卡片查看词义
   - 标记是否认识该词汇
5. **查看进度**: 在"学习统计"页面查看学习进度和掌握情况
6. **升级会员**: 在"订阅升级"页面升级到高级会员，解锁全部词汇

## 默认账号

注册新账号后即可使用。免费账号可以访问 JLPT N5 等级的词汇（约30个基础词汇）。

## 数据库

SQLite 数据库文件位于: `server/db/japanese_learning.db`

包含以下表:
- `users` - 用户表
- `vocabulary` - 词汇表
- `learning_progress` - 学习进度表
- `payments` - 支付记录表
- `user_settings` - 用户设置表

## 未来改进

- [ ] 添加语音发音功能
- [ ] 添加更多词汇和例句
- [ ] 实现真正的支付集成（Stripe、支付宝等）
- [ ] 添加社交功能（学习社区）
- [ ] 添加更多练习模式（填空、选择题等）
- [ ] 实现间隔重复算法（SRS）
- [ ] 添加移动应用版本

## 开发者

由 WorkBuddy AI 助手创建于 2026年6月
