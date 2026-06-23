// Payment Configuration
// Supports WeChat Pay and Alipay
// Two modes:
// 1. "qrcode" - Simple QR code mode (no merchant account needed, manual verification)
// 2. "api" - API integration mode (requires merchant credentials)

const paymentMode = process.env.PAYMENT_MODE || 'qrcode'; // 'qrcode' or 'api'

export const config = {
  mode: paymentMode,

  // Product configuration
  product: {
    id: 'lifetime_premium',
    name: '日语学习永久会员',
    description: '一次性买断，终身使用，解锁全部JLPT词汇(N5-N1)和所有高级功能',
    price: 49.9, // CNY
    currency: 'CNY',
  },

  // QR Code mode configuration (simplest - no merchant account needed)
  // User scans QR code with WeChat/Alipay to pay, then enters order ID for verification
  qrcode: {
    wechatPayUrl: process.env.WECHAT_PAY_QR_URL || '', // Personal WeChat collection QR code URL
    alipayUrl: process.env.ALIPAY_QR_URL || '', // Personal Alipay collection QR code URL
    // After payment, user enters their payment amount or transaction ID
    // Admin can verify and activate premium manually
    autoActivate: process.env.PAYMENT_AUTO_ACTIVATE === 'true', // Set to true for auto-activation (less secure)
  },

  // API mode configuration (requires merchant accounts)
  // For WeChat Pay: https://pay.weixin.qq.com/
  wechat: {
    appId: process.env.WECHAT_APP_ID || '',
    mchId: process.env.WECHAT_MCH_ID || '', // Merchant ID
    apiKey: process.env.WECHAT_API_KEY || '', // API key
    notifyUrl: process.env.WECHAT_NOTIFY_URL || '', // Payment notification URL
  },

  // For Alipay: https://open.alipay.com/
  alipay: {
    appId: process.env.ALIPAY_APP_ID || '',
    merchantPrivateKey: process.env.ALIPAY_MERCHANT_PRIVATE_KEY || '',
    alipayPublicKey: process.env.ALIPAY_PUBLIC_KEY || '',
    gatewayUrl: process.env.ALIPAY_GATEWAY_URL || 'https://openapi.alipay.com/gateway.do',
    notifyUrl: process.env.ALIPAY_NOTIFY_URL || '',
    returnUrl: process.env.ALIPAY_RETURN_URL || '',
  },
};

export default config;
