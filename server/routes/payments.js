import express from 'express';
import { db } from '../db/database.js';
import { authMiddleware } from '../utils/auth.js';
import paymentConfig from '../config/payment.js';
import crypto from 'crypto';

const router = express.Router();

// Generate unique order ID
const generateOrderId = () => {
  const timestamp = Date.now().toString(36);
  const random = crypto.randomBytes(4).toString('hex');
  return `JL${timestamp}${random}`.toUpperCase();
};

// ============================================
// Get payment configuration (public)
// ============================================
router.get('/config', (req, res) => {
  res.json({
    mode: paymentConfig.mode,
    product: paymentConfig.product,
    qrcode: {
      wechatEnabled: !!paymentConfig.qrcode.wechatPayUrl,
      alipayEnabled: !!paymentConfig.qrcode.alipayUrl,
    },
  });
});

// ============================================
// Create payment order
// ============================================
router.post('/create-order', authMiddleware, (req, res) => {
  const userId = req.userId;
  const { method } = req.body; // 'wechat' or 'alipay'

  if (!method || !['wechat', 'alipay'].includes(method)) {
    return res.status(400).json({ error: 'Invalid payment method. Use "wechat" or "alipay".' });
  }

  // Check if user is already premium
  db.get('SELECT is_premium, email FROM users WHERE id = ?', [userId], (err, user) => {
    if (err || !user) {
      return res.status(404).json({ error: 'User not found' });
    }

    if (user.is_premium) {
      return res.json({ error: 'ALREADY_PREMIUM', message: '您已是永久会员' });
    }

    const orderId = generateOrderId();
    const amount = paymentConfig.product.price;

    // Create payment record
    db.run(
      `INSERT INTO payments (user_id, amount, currency, payment_method, transaction_id, status)
       VALUES (?, ?, 'CNY', ?, ?, 'pending')`,
      [userId, amount, method, orderId],
      function(err) {
        if (err) {
          console.error('Payment order creation error:', err);
          return res.status(500).json({ error: 'Failed to create order' });
        }

        const paymentId = this.lastID;

        // Generate payment URL based on mode
        let paymentUrl = '';
        let qrCodeUrl = '';

        if (paymentConfig.mode === 'qrcode') {
          // QR code mode - return the collection QR code URL
          if (method === 'wechat') {
            qrCodeUrl = paymentConfig.qrcode.wechatPayUrl;
          } else {
            qrCodeUrl = paymentConfig.qrcode.alipayUrl;
          }
        }

        res.json({
          success: true,
          orderId,
          paymentId,
          amount,
          method,
          productName: paymentConfig.product.name,
          productDescription: paymentConfig.product.description,
          qrCodeUrl,
          mode: paymentConfig.mode,
          instructions: method === 'wechat'
            ? '请使用微信扫描二维码完成支付，支付完成后点击"我已支付"按钮'
            : '请使用支付宝扫描二维码完成支付，支付完成后点击"我已支付"按钮',
        });
      }
    );
  });
});

// ============================================
// Confirm payment (user confirms they've paid)
// ============================================
router.post('/confirm-payment', authMiddleware, (req, res) => {
  const userId = req.userId;
  const { orderId, method } = req.body;

  if (!orderId) {
    return res.status(400).json({ error: 'Order ID required' });
  }

  // Find the payment record
  db.get(
    'SELECT * FROM payments WHERE transaction_id = ? AND user_id = ?',
    [orderId, userId],
    (err, payment) => {
      if (err || !payment) {
        return res.status(404).json({ error: 'Order not found' });
      }

      if (payment.status === 'completed') {
        return res.json({ success: true, message: 'Payment already confirmed', is_premium: true });
      }

      if (paymentConfig.qrcode.autoActivate) {
        // Auto-activate (less secure, but simpler for small operations)
        activatePremium(userId, orderId, payment.payment_method || method, (success) => {
          if (success) {
            res.json({ success: true, message: 'Payment confirmed, premium activated!', is_premium: true });
          } else {
            res.status(500).json({ error: 'Failed to activate premium' });
          }
        });
      } else {
        // Mark as pending verification
        db.run(
          'UPDATE payments SET status = ? WHERE transaction_id = ?',
          ['pending_verification', orderId],
          (err) => {
            if (err) {
              return res.status(500).json({ error: 'Database error' });
            }
            res.json({
              success: true,
              message: '支付确认已提交，请等待管理员审核激活（通常在24小时内完成）',
              status: 'pending_verification',
            });
          }
        );
      }
    }
  );
});

// ============================================
// Admin: Verify and activate premium
// ============================================
router.post('/admin/verify', (req, res) => {
  const { orderId, adminKey } = req.body;

  // Simple admin authentication
  const configuredAdminKey = process.env.ADMIN_KEY || 'japanese-learning-admin-2026';
  if (adminKey !== configuredAdminKey) {
    return res.status(403).json({ error: 'Unauthorized' });
  }

  if (!orderId) {
    return res.status(400).json({ error: 'Order ID required' });
  }

  db.get('SELECT * FROM payments WHERE transaction_id = ?', [orderId], (err, payment) => {
    if (err || !payment) {
      return res.status(404).json({ error: 'Order not found' });
    }

    activatePremium(payment.user_id, orderId, payment.payment_method, (success) => {
      if (success) {
        res.json({ success: true, message: 'Premium activated successfully' });
      } else {
        res.status(500).json({ error: 'Activation failed' });
      }
    });
  });
});

// ============================================
// Helper: Activate premium for a user
// ============================================
function activatePremium(userId, orderId, method, callback) {
  // Update payment status
  db.run(
    'UPDATE payments SET status = ? WHERE transaction_id = ?',
    ['completed', orderId],
    (err) => {
      if (err) {
        console.error('Payment status update error:', err);
        callback(false);
        return;
      }

      // Activate lifetime premium
      db.run(
        'UPDATE users SET is_premium = 1, premium_expires_at = NULL WHERE id = ?',
        [userId],
        (err) => {
          if (err) {
            console.error('Premium activation error:', err);
            callback(false);
          } else {
            console.log(`User ${userId} premium activated via ${method} payment (Order: ${orderId})`);
            callback(true);
          }
        }
      );
    }
  );
}

// ============================================
// Get premium status
// ============================================
router.get('/status', authMiddleware, (req, res) => {
  const userId = req.userId;

  db.get(
    'SELECT is_premium, premium_expires_at FROM users WHERE id = ?',
    [userId],
    (err, user) => {
      if (err) return res.status(500).json({ error: 'Database error' });

      res.json({
        is_premium: user.is_premium === 1,
        premium_type: 'lifetime',
        premium_expires_at: user.premium_expires_at,
      });
    }
  );
});

// ============================================
// Get payment history
// ============================================
router.get('/history', authMiddleware, (req, res) => {
  const userId = req.userId;

  db.all(
    'SELECT * FROM payments WHERE user_id = ? ORDER BY created_at DESC',
    [userId],
    (err, payments) => {
      if (err) return res.status(500).json({ error: 'Database error' });
      res.json({ payments });
    }
  );
});

// ============================================
// Get pending verifications (admin)
// ============================================
router.get('/admin/pending', (req, res) => {
  const { adminKey } = req.query;
  const configuredAdminKey = process.env.ADMIN_KEY || 'japanese-learning-admin-2026';

  if (adminKey !== configuredAdminKey) {
    return res.status(403).json({ error: 'Unauthorized' });
  }

  db.all(
    `SELECT p.*, u.email, u.name
     FROM payments p
     JOIN users u ON p.user_id = u.id
     WHERE p.status = 'pending_verification'
     ORDER BY p.created_at DESC`,
    (err, payments) => {
      if (err) return res.status(500).json({ error: 'Database error' });
      res.json({ payments });
    }
  );
});

// ============================================
// Webhook for API mode (WeChat Pay)
// ============================================
router.post('/webhook/wechat', express.raw({ type: 'application/xml' }), (req, res) => {
  // Parse XML and verify signature
  // This endpoint receives payment notifications from WeChat Pay
  // Implementation depends on WeChat Pay API version

  const configuredApiKey = paymentConfig.wechat.apiKey;
  if (!configuredApiKey) {
    return res.status(500).json({ error: 'WeChat Pay not configured' });
  }

  // TODO: Parse XML, verify signature, extract order ID and payment result
  // For now, return success to acknowledge receipt
  res.set('Content-Type', 'application/xml');
  res.send('<xml><return_code><![CDATA[SUCCESS]]></return_code></xml>');
});

// ============================================
// Webhook for API mode (Alipay)
// ============================================
router.post('/webhook/alipay', express.urlencoded({ extended: true }), (req, res) => {
  // Verify Alipay signature and process payment notification
  const configuredPublicKey = paymentConfig.alipay.alipayPublicKey;
  if (!configuredPublicKey) {
    return res.status(500).json({ error: 'Alipay not configured' });
  }

  // TODO: Verify signature, extract order ID and payment result
  // For now, return success
  res.send('success');
});

export default router;
