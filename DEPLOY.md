# 日语学习网站部署指南（v4.0 静态版）

## 架构说明

本项目已从全栈应用改为**纯静态网站**：
- ✅ 无后端服务器，无需数据库
- ✅ 所有数据（8333词）打包到前端
- ✅ 用户数据存储在浏览器 localStorage
- ✅ 可部署到任意免费静态托管平台
- ✅ 全球 CDN 加速，国内可访问

---

## 部署方案（推荐顺序）

### 方案 1：Vercel（推荐，免费+国内可访问）

1. 打开 https://vercel.com ，用 GitHub 登录
2. 点击 "New Project"
3. 选择 `japanese-learning` 仓库
4. Vercel 自动检测 Vite 项目，直接点 "Deploy"
5. 1-2 分钟后完成，获得 `xxx.vercel.app` 域名

**绑定自定义域名：**
1. 在 Vercel 项目设置 → Domains
2. 添加你的域名
3. 按提示到域名服务商添加 CNAME 记录
4. Vercel 自动配置 HTTPS

---

### 方案 2：Netlify（免费）

1. 打开 https://netlify.com ，用 GitHub 登录
2. 点击 "Add new site" → "Import an existing project"
3. 选择 `japanese-learning` 仓库
4. 构建配置已写在 `netlify.toml`，直接部署
5. 获得 `xxx.netlify.app` 域名

---

### 方案 3：Cloudflare Pages（免费，国内速度好）

1. 打开 https://pages.cloudflare.com ，登录 Cloudflare
2. 点击 "Create a project" → "Connect to Git"
3. 选择 `japanese-learning` 仓库
4. 构建命令：`npm run build`
5. 输出目录：`dist`
6. 获得 `xxx.pages.dev` 域名

---

### 方案 4：GitHub Pages（免费，但国内可能慢）

1. 在 GitHub 仓库 Settings → Pages
2. Source: GitHub Actions
3. 创建 `.github/workflows/deploy.yml`（略）
4. 获得 `xxx.github.io` 域名

---

## 域名绑定

以上所有平台都支持绑定自定义域名：

1. **买域名**：腾讯云 / 阿里云购买 `.com` 或 `.cn` 域名（¥30-60/年）
2. **DNS 解析**：在域名管理面板添加 CNAME 记录，指向平台分配的地址
3. **HTTPS**：平台自动配置，无需额外操作

**免备案说明**：使用海外托管平台（Vercel/Netlify/Cloudflare）+ 你的域名，不需要 ICP 备案。

---

## 激活码系统

静态版使用激活码代替在线支付：

- **激活码**：`JPLEARN2026`
- 用户在定价页输入激活码即可解锁全部词汇
- 修改激活码：编辑 `src/services/api.ts` 中的 `PREMIUM_ACTIVATION_CODE`

**收款流程**：
1. 用户在网站看到定价页，联系你付款
2. 你通过微信/支付宝收款 ¥49.9
3. 把激活码发给用户
4. 用户输入激活码解锁

---

## 搜索引擎收录

部署完成后，提交网站到国内搜索引擎：

1. **百度站长平台**：https://ziyuan.baidu.com
   - 添加网站 → 验证域名 → 提交 sitemap
   - sitemap 地址：`https://你的域名/sitemap.xml`

2. **360 站长平台**：https://zhanzhang.so.com
   - 添加网站 → 验证 → 提交 sitemap

3. **搜狗站长平台**：https://zhanzhang.sogou.com
   - 添加网站 → 验证 → 提交 sitemap

4. **神马站长平台**：https://zhanzhang.sm.cn
   - 添加网站 → 验证 → 提交 sitemap

---

## 本地开发

```bash
# 安装依赖
npm install

# 开发服务器
npm run dev

# 构建
npm run build

# 预览构建结果
npm run preview
```

---

## 数据存储说明

所有用户数据存储在浏览器 localStorage 中：
- `jl_users` - 注册用户列表
- `jl_current_user` - 当前登录用户
- `jl_token` - 登录令牌
- `jl_favorites` - 收藏的词汇 ID
- `jl_progress` - 学习进度

**注意**：清除浏览器数据会丢失所有本地数据。同一浏览器不同标签页共享数据。
