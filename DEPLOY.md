# 日语学习网站 - 部署指南（国内版）

> v3.0 全栈一体架构 — 前端+后端合并为单个 Node.js 服务

---

## 架构说明

```
┌─────────────────────────────────┐
│       单个 Node.js 服务          │
│  ┌───────────┐ ┌─────────────┐  │
│  │ 静态文件   │ │  API 路由    │  │
│  │ (dist/)   │ │ (/api/*)    │  │
│  └───────────┘ └─────────────┘  │
│         SQLite 数据库            │
└─────────────────────────────────┘
```

- 前端和后端在同一个 Express 服务中
- 不需要 CORS 配置，不存在跨域问题
- 不需要单独的前端托管
- SQLite 数据库文件随服务一起运行

---

## 一、本地运行

```bash
# 1. 安装依赖
npm install

# 2. 构建前端
npm run build

# 3. 启动全栈服务
npm start

# 打开 http://localhost:3001
```

开发模式（前后端分离热更新）：
```bash
# 终端1：启动后端
npm run dev:server

# 终端2：启动前端（自动代理 API 到 3001）
npm run dev
# 打开 http://localhost:5173
```

---

## 二、部署方案对比（国内可用）

| 方案 | 费用 | 速度 | 持久化 | 推荐度 |
|------|------|------|--------|--------|
| Zeabur | 免费额度 | 快（亚洲节点） | ✅ | ⭐⭐⭐⭐⭐ |
| 腾讯云开发 CloudBase | 免费额度 | 极快 | ✅ | ⭐⭐⭐⭐ |
| Render.com | 免费 | 较慢 | ❌* | ⭐⭐ |
| 国内 VPS | ¥几元/月 | 极快 | ✅ | ⭐⭐⭐⭐ |

> *Render 免费版使用临时文件系统，重启后 SQLite 数据丢失（词汇每次自动恢复，用户数据会丢失）

### 推荐方案：Zeabur

Zeabur 有香港/亚洲节点，国内访问速度快，支持持久化存储，免费额度足够小网站使用。

---

## 三、Zeabur 部署（推荐）

### 步骤

1. **注册 Zeabur**
   - 打开 https://zeabur.com
   - 用 GitHub 账号登录

2. **推送代码到 GitHub**
   ```bash
   git init
   git add .
   git commit -m "日语学习网站 v3.0"
   git push origin main
   ```

3. **在 Zeabur 创建项目**
   - New Project → 选择 GitHub 仓库
   - Zeabur 自动检测 Node.js 项目
   - Build Command: `npm run build`
   - Start Command: `npm start`

4. **添加持久化存储（重要！）**
   - 在 Zeabur 控制台 → 服务设置 → Volumes
   - 添加 Volume，挂载路径：`/opt/render/project/src/server`（或项目实际路径）
   - 这样 SQLite 数据库文件不会丢失

5. **配置环境变量**
   - Settings → Environment Variables
   - 添加以下变量：

   ```
   JWT_SECRET=你的随机密钥（用 openssl rand -hex 32 生成）
   ADMIN_KEY=你的管理员密钥
   PAYMENT_MODE=qrcode
   PAYMENT_AUTO_ACTIVATE=true
   WECHAT_PAY_QR_URL=你的微信收款码图片URL
   ALIPAY_QR_URL=你的支付宝收款码图片URL
   ```

6. **绑定域名**
   - Zeabur 提供免费子域名：`xxx.zeabur.app`
   - 也可绑定自有域名（建议备案）

7. **部署完成**
   - 访问 Zeabur 分配的域名即可使用

---

## 四、国内 VPS 部署（最稳定）

适合有一定技术基础的用户，国内访问最快最稳定。

### 推荐 VPS
- 腾讯云轻量应用服务器：¥38/月起（2核2G）
- 阿里云 ECS 突发性能型：¥24/月起（2核2G）
- 京东云轻量主机：¥36/月起（2核2G）

### 部署步骤

1. **购买 VPS**，选择 Ubuntu 22.04 系统

2. **安装 Node.js**
   ```bash
   curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
   sudo apt-get install -y nodejs
   ```

3. **安装 PM2**（进程管理，保证服务不中断）
   ```bash
   sudo npm install -g pm2
   ```

4. **上传项目**
   ```bash
   # 方法1：Git 克隆
   git clone https://github.com/你的用户名/japanese-learning.git
   cd japanese-learning
   npm install
   npm run build

   # 方法2：SCP 上传
   scp -r ./japanese-learning root@你的IP:/opt/
   ```

5. **启动服务**
   ```bash
   PORT=3001 pm2 start server/index.js --name japanese-learning
   pm2 save
   pm2 startup  # 设置开机自启
   ```

6. **配置 Nginx 反向代理**
   ```nginx
   server {
       listen 80;
       server_name 你的域名或IP;

       location / {
           proxy_pass http://127.0.0.1:3001;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

7. **配置 SSL（可选，需域名）**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d 你的域名
   ```

---

## 五、配置支付

### 获取收款二维码

1. **微信收款码**
   - 打开微信 → 我 → 服务 → 收付款 → 二维码收款
   - 保存收款码图片
   - 上传到图床（推荐：https://imgse.com 或 https://sm.ms）
   - 获取图片 URL

2. **支付宝收款码**
   - 打开支付宝 → 首页 -> 收钱码
   - 保存收款码图片
   - 同样上传到图床获取 URL

3. **设置环境变量**
   ```
   WECHAT_PAY_QR_URL=https://图片URL.jpg
   ALIPAY_QR_URL=https://图片URL.jpg
   ```

### 支付流程
1. 用户点击「微信支付」或「支付宝」按钮
2. 弹出收款二维码
3. 用户扫码支付 ¥49.9
4. 用户点击「我已支付，确认激活」
5. 系统自动激活会员（PAYMENT_AUTO_ACTIVATE=true）

---

## 六、搜索引擎收录

### 百度收录
1. 打开 https://ziyuan.baidu.com
2. 添加网站，验证域名所有权
3. 提交 sitemap：`https://你的域名/sitemap.xml`
4. 在 `index.html` 中填写 `<meta name="baidu-site-verification" content="验证码" />`

### 360 搜索收录
1. 打开 https://zhanzhang.so.com
2. 添加网站，验证所有权
3. 填写 `<meta name="360-site-verification" content="验证码" />`

### 搜狗收录
1. 打开 https://zhanzhang.sogou.com
2. 添加网站，验证所有权
3. 填写 `<meta name="sogou_site_verification" content="验证码" />`

### 神马搜索（UC浏览器）
1. 打开 https://zhanzhang.sm.cn
2. 添加网站，验证所有权
4. 填写 `<meta name="shenma-site-verification" content="验证码" />`

---

## 七、环境变量说明

| 变量名 | 必填 | 默认值 | 说明 |
|--------|------|--------|------|
| PORT | 否 | 3001 | 服务端口 |
| JWT_SECRET | **是** | - | JWT 签名密钥 |
| ADMIN_KEY | **是** | - | 管理员审核密钥 |
| PAYMENT_MODE | 否 | qrcode | 支付模式 |
| PAYMENT_AUTO_ACTIVATE | 否 | true | 自动激活会员 |
| WECHAT_PAY_QR_URL | 否 | - | 微信收款码 URL |
| ALIPAY_QR_URL | 否 | - | 支付宝收款码 URL |

生成密钥：
```bash
openssl rand -hex 32
```

---

## 八、运维管理

### 查看日志
```bash
# PM2
pm2 logs japanese-learning

# Zeabur
在控制台 → Logs 页面查看
```

### 数据库备份
```bash
# 复制 SQLite 文件
cp server/japanese_learning.db backup_$(date +%Y%m%d).db
```

### 更新部署
```bash
git pull
npm install
npm run build
pm2 restart japanese-learning
```

---

## 九、成本估算

| 方案 | 月费用 | 说明 |
|------|--------|------|
| Zeabur 免费额度 | ¥0 | 适合初期小流量 |
| 腾讯云轻量服务器 | ¥38 | 2核2G，稳定可靠 |
| 域名（可选） | ¥30-60/年 | .com 域名 |
| SSL 证书 | ¥0 | Let's Encrypt 免费 |

**最低成本：¥0**（使用 Zeabur 免费额度）
**推荐成本：¥38/月**（国内 VPS，速度最快）
