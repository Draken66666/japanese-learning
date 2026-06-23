import dotenv from 'dotenv';
dotenv.config();

import express from 'express';
import cors from 'cors';
import bodyParser from 'body-parser';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { initDb, seedVocabulary } from './db/database.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3001;

// ============================================
// Middleware
// ============================================
app.use(cors({
  origin: process.env.FRONTEND_URL || '*',
  credentials: true,
}));
app.use(bodyParser.json({ limit: '10mb' }));
app.use(bodyParser.urlencoded({ extended: true }));

// Request logging
app.use((req, res, next) => {
  const timestamp = new Date().toISOString().split('T')[1].slice(0, 8);
  console.log(`${timestamp} ${req.method} ${req.path}`);
  next();
});

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', version: '3.0.0', timestamp: new Date().toISOString() });
});

// ============================================
// API Routes
// ============================================
const setupRoutes = async () => {
  const authRoutes = (await import('./routes/auth.js')).default;
  const vocabularyRoutes = (await import('./routes/vocabulary.js')).default;
  const progressRoutes = (await import('./routes/progress.js')).default;
  const paymentsRoutes = (await import('./routes/payments.js')).default;

  app.use('/api/auth', authRoutes);
  app.use('/api/vocabulary', vocabularyRoutes);
  app.use('/api/progress', progressRoutes);
  app.use('/api/payments', paymentsRoutes);
};

// Error handling (must be before static files)
app.use('/api', (err, req, res, next) => {
  console.error('Server error:', err.message);
  res.status(500).json({ error: 'Internal server error' });
});

// ============================================
// Static Frontend (同源部署：前端和后端在同一个服务)
// ============================================
const distPath = join(__dirname, '../dist');
app.use(express.static(distPath));

// SPA fallback: 所有非 API 的 GET 请求返回 index.html（兼容 Express 5）
app.use((req, res, next) => {
  if (req.method === 'GET' && !req.path.startsWith('/api/')) {
    return res.sendFile(join(distPath, 'index.html'));
  }
  next();
});

// ============================================
// Initialize and Start
// ============================================
const startServer = async () => {
  initDb();

  // Seed vocabulary after tables are created
  setTimeout(() => {
    seedVocabulary();
  }, 500);

  await setupRoutes();

  app.listen(PORT, () => {
    console.log(`\n=================================`);
    console.log(`  日语学习网站 v3.0 (全栈一体)`);
    console.log(`  端口: ${PORT}`);
    console.log(`  地址: http://localhost:${PORT}`);
    console.log(`  API:  http://localhost:${PORT}/api`);
    console.log(`=================================\n`);
  });
};

startServer().catch(console.error);
