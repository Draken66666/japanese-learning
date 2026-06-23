import express from 'express';
import { db } from '../db/database.js';
import { verifyToken, authMiddleware } from '../utils/auth.js';

const router = express.Router();

// Get vocabulary list with filters and search
router.get('/', (req, res) => {
  const { jlpt_level, category, page = 1, limit = 20, search, is_premium } = req.query;
  const offset = (page - 1) * limit;

  // Check if user is premium (if token provided)
  let isPremium = false;
  const token = req.headers.authorization?.split(' ')[1];

  if (token) {
    const decoded = verifyToken(token);
    if (decoded) {
      db.get('SELECT is_premium FROM users WHERE id = ?', [decoded.userId], (err, user) => {
        if (user) {
          isPremium = !!user.is_premium;
        }
        fetchVocabulary();
      });
      return;
    }
  }

  fetchVocabulary();

  function fetchVocabulary() {
    let query = 'SELECT * FROM vocabulary WHERE 1=1';
    let countQuery = 'SELECT COUNT(*) as total FROM vocabulary WHERE 1=1';
    const params = [];
    const countParams = [];

    // Filter by premium status (non-premium users can only see free words)
    if (!isPremium) {
      query += ' AND is_premium = 0';
      countQuery += ' AND is_premium = 0';
    }

    // Filter by JLPT level
    if (jlpt_level && jlpt_level !== 'all') {
      query += ' AND jlpt_level = ?';
      countQuery += ' AND jlpt_level = ?';
      params.push(jlpt_level);
      countParams.push(jlpt_level);
    }

    // Filter by category
    if (category && category !== 'all') {
      query += ' AND category = ?';
      countQuery += ' AND category = ?';
      params.push(category);
      countParams.push(category);
    }

    // Search across multiple fields
    if (search && search.trim()) {
      const searchPattern = `%${search.trim()}%`;
      query += ' AND (japanese LIKE ? OR hiragana LIKE ? OR romaji LIKE ? OR meaning_en LIKE ? OR meaning_zh LIKE ?)';
      countQuery += ' AND (japanese LIKE ? OR hiragana LIKE ? OR romaji LIKE ? OR meaning_en LIKE ? OR meaning_zh LIKE ?)';
      params.push(searchPattern, searchPattern, searchPattern, searchPattern, searchPattern);
      countParams.push(searchPattern, searchPattern, searchPattern, searchPattern, searchPattern);
    }

    // Get total count
    db.get(countQuery, countParams, (err, countResult) => {
      if (err) {
        console.error('Vocabulary count error:', err);
        return res.status(500).json({ error: 'Database error' });
      }

      // Add pagination and ordering
      const pageNum = parseInt(page) || 1;
      const limitNum = Math.min(parseInt(limit) || 20, 100);
      const offsetNum = (pageNum - 1) * limitNum;

      query += ' ORDER BY jlpt_level, hiragana LIMIT ? OFFSET ?';
      params.push(limitNum, offsetNum);

      db.all(query, params, (err, words) => {
        if (err) {
          console.error('Vocabulary query error:', err);
          return res.status(500).json({ error: 'Database error' });
        }

        res.json({
          words,
          pagination: {
            page: pageNum,
            limit: limitNum,
            total: countResult.total,
            totalPages: Math.ceil(countResult.total / limitNum)
          }
        });
      });
    });
  }
});

// Get single vocabulary item
router.get('/:id', (req, res) => {
  const { id } = req.params;

  db.get('SELECT * FROM vocabulary WHERE id = ?', [id], (err, word) => {
    if (err) {
      return res.status(500).json({ error: 'Database error' });
    }

    if (!word) {
      return res.status(404).json({ error: 'Word not found' });
    }

    res.json({ word });
  });
});

// Get categories
router.get('/meta/categories', (req, res) => {
  db.all('SELECT DISTINCT category FROM vocabulary WHERE category IS NOT NULL ORDER BY category', (err, categories) => {
    if (err) {
      return res.status(500).json({ error: 'Database error' });
    }
    res.json({ categories: categories.map(c => c.category) });
  });
});

// Get JLPT levels
router.get('/meta/jlpt-levels', (req, res) => {
  db.all('SELECT DISTINCT jlpt_level FROM vocabulary ORDER BY jlpt_level', (err, levels) => {
    if (err) {
      return res.status(500).json({ error: 'Database error' });
    }
    res.json({ levels: levels.map(l => l.jlpt_level) });
  });
});

// Get vocabulary statistics
router.get('/meta/stats', (req, res) => {
  db.all(`
    SELECT jlpt_level, category, COUNT(*) as count
    FROM vocabulary
    GROUP BY jlpt_level, category
    ORDER BY jlpt_level, category
  `, (err, rows) => {
    if (err) {
      return res.status(500).json({ error: 'Database error' });
    }

    const stats = {
      total: 0,
      byLevel: {},
      byCategory: {},
      free: 0,
      premium: 0,
    };

    rows.forEach(row => {
      stats.total += row.count;
      stats.byLevel[row.jlpt_level] = (stats.byLevel[row.jlpt_level] || 0) + row.count;
      stats.byCategory[row.category] = (stats.byCategory[row.category] || 0) + row.count;
    });

    db.get("SELECT COUNT(*) as count FROM vocabulary WHERE is_premium = 0", (err, freeRow) => {
      if (!err && freeRow) {
        stats.free = freeRow.count;
        stats.premium = stats.total - freeRow.count;
      }
      res.json({ stats });
    });
  });
});

// =================== Favorites endpoints ===================

// Get user's favorite words
router.get('/favorites/list', authMiddleware, (req, res) => {
  const userId = req.userId;

  db.all(`
    SELECT v.*, f.created_at as favorited_at
    FROM favorites f
    JOIN vocabulary v ON f.vocabulary_id = v.id
    WHERE f.user_id = ?
    ORDER BY f.created_at DESC
  `, [userId], (err, words) => {
    if (err) {
      return res.status(500).json({ error: 'Database error' });
    }
    res.json({ words, count: words.length });
  });
});

// Add a word to favorites
router.post('/favorites/:wordId', authMiddleware, (req, res) => {
  const userId = req.userId;
  const { wordId } = req.params;

  db.run(
    'INSERT OR IGNORE INTO favorites (user_id, vocabulary_id) VALUES (?, ?)',
    [userId, wordId],
    function(err) {
      if (err) {
        return res.status(500).json({ error: 'Database error' });
      }
      res.json({ success: true, favorited: true });
    }
  );
});

// Remove a word from favorites
router.delete('/favorites/:wordId', authMiddleware, (req, res) => {
  const userId = req.userId;
  const { wordId } = req.params;

  db.run(
    'DELETE FROM favorites WHERE user_id = ? AND vocabulary_id = ?',
    [userId, wordId],
    function(err) {
      if (err) {
        return res.status(500).json({ error: 'Database error' });
      }
      res.json({ success: true, favorited: false });
    }
  );
});

// Check if a word is favorited
router.get('/favorites/check/:wordId', authMiddleware, (req, res) => {
  const userId = req.userId;
  const { wordId } = req.params;

  db.get(
    'SELECT id FROM favorites WHERE user_id = ? AND vocabulary_id = ?',
    [userId, wordId],
    (err, row) => {
      if (err) {
        return res.status(500).json({ error: 'Database error' });
      }
      res.json({ favorited: !!row });
    }
  );
});

// Get user's favorited word IDs (for bulk check)
router.get('/favorites/ids', authMiddleware, (req, res) => {
  const userId = req.userId;

  db.all(
    'SELECT vocabulary_id FROM favorites WHERE user_id = ?',
    [userId],
    (err, rows) => {
      if (err) {
        return res.status(500).json({ error: 'Database error' });
      }
      res.json({ ids: rows.map(r => r.vocabulary_id) });
    }
  );
});

export default router;
