import express from 'express';
import { db } from '../db/database.js';
import { authMiddleware } from '../utils/auth.js';

const router = express.Router();

// Get user's learning progress
router.get('/', authMiddleware, (req, res) => {
  const userId = req.userId;
  
  db.all(`
    SELECT 
      lp.*,
      v.japanese,
      v.hiragana,
      v.romaji,
      v.meaning_en,
      v.meaning_zh,
      v.jlpt_level
    FROM learning_progress lp
    JOIN vocabulary v ON lp.vocabulary_id = v.id
    WHERE lp.user_id = ?
    ORDER BY lp.last_reviewed DESC
  `, [userId], (err, progress) => {
    if (err) {
      return res.status(500).json({ error: 'Database error' });
    }
    res.json({ progress });
  });
});

// Update learning progress (mark correct/incorrect)
router.post('/update', authMiddleware, (req, res) => {
  const userId = req.userId;
  const { vocabulary_id, correct } = req.body;
  
  if (!vocabulary_id) {
    return res.status(400).json({ error: 'vocabulary_id required' });
  }
  
  // Check if progress exists
  db.get(
    'SELECT * FROM learning_progress WHERE user_id = ? AND vocabulary_id = ?',
    [userId, vocabulary_id],
    (err, existing) => {
      if (err) {
        return res.status(500).json({ error: 'Database error' });
      }
      
      const now = new Date().toISOString();
      const nextReview = new Date();
      nextReview.setDate(nextReview.getDate() + 1); // Simple spaced repetition
      
      if (existing) {
        // Update existing progress
        const updates = correct 
          ? { times_correct: existing.times_correct + 1, mastery_level: Math.min(existing.mastery_level + 1, 5) }
          : { times_incorrect: existing.times_incorrect + 1, mastery_level: Math.max(existing.mastery_level - 1, 0) };
        
        db.run(
          `UPDATE learning_progress 
           SET times_correct = ?, times_incorrect = ?, last_reviewed = ?, next_review_date = ?, mastery_level = ?
           WHERE user_id = ? AND vocabulary_id = ?`,
          [correct ? existing.times_correct + 1 : existing.times_correct,
           correct ? existing.times_incorrect : existing.times_incorrect + 1,
           now,
           nextReview.toISOString(),
           updates.mastery_level,
           userId,
           vocabulary_id],
          (err) => {
            if (err) {
              return res.status(500).json({ error: 'Update failed' });
            }
            res.json({ success: true });
          }
        );
      } else {
        // Create new progress
        db.run(
          `INSERT INTO learning_progress (user_id, vocabulary_id, times_correct, times_incorrect, last_reviewed, next_review_date, mastery_level)
           VALUES (?, ?, ?, ?, ?, ?, ?)`,
          [userId, vocabulary_id, correct ? 1 : 0, correct ? 0 : 1, now, nextReview.toISOString(), correct ? 1 : 0],
          (err) => {
            if (err) {
              return res.status(500).json({ error: 'Create failed' });
            }
            res.json({ success: true });
          }
        );
      }
    }
  );
});

// Get words to review (spaced repetition)
router.get('/review', authMiddleware, (req, res) => {
  const userId = req.userId;
  const now = new Date().toISOString();
  
  db.all(`
    SELECT 
      v.*,
      lp.mastery_level,
      lp.times_correct,
      lp.times_incorrect
    FROM vocabulary v
    LEFT JOIN learning_progress lp ON v.id = lp.vocabulary_id AND lp.user_id = ?
    WHERE lp.next_review_date <= ? OR lp.next_review_date IS NULL
    ORDER BY lp.mastery_level ASC, lp.last_reviewed ASC
    LIMIT 20
  `, [userId, now], (err, words) => {
    if (err) {
      return res.status(500).json({ error: 'Database error' });
    }
    res.json({ words });
  });
});

// Get learning statistics
router.get('/stats', authMiddleware, (req, res) => {
  const userId = req.userId;
  
  db.get(
    `SELECT 
      COUNT(*) as total_words,
      SUM(CASE WHEN mastery_level >= 3 THEN 1 ELSE 0 END) as mastered,
      SUM(CASE WHEN mastery_level = 0 OR mastery_level IS NULL THEN 1 ELSE 0 END) as new_words,
      SUM(times_correct) as total_correct,
      SUM(times_incorrect) as total_incorrect
    FROM learning_progress
    WHERE user_id = ?`,
    [userId],
    (err, stats) => {
      if (err) {
        return res.status(500).json({ error: 'Database error' });
      }
      
      // Get total vocabulary count
      db.get('SELECT COUNT(*) as total_vocab FROM vocabulary WHERE is_premium = 0', (err, vocabCount) => {
        if (err) {
          return res.status(500).json({ error: 'Database error' });
        }
        
        res.json({
          stats: {
            total_words_learned: stats.total_words || 0,
            mastered: stats.mastered || 0,
            new_words: stats.new_words || 0,
            total_correct: stats.total_correct || 0,
            total_incorrect: stats.total_incorrect || 0,
            total_vocabulary: vocabCount.total_vocab,
            accuracy: stats.total_correct + stats.total_incorrect > 0
              ? Math.round((stats.total_correct / (stats.total_correct + stats.total_incorrect)) * 100)
              : 0
          }
        });
      });
    }
  );
});

// Reset learning progress
router.delete('/reset', authMiddleware, (req, res) => {
  const userId = req.userId;
  
  db.run('DELETE FROM learning_progress WHERE user_id = ?', [userId], (err) => {
    if (err) {
      return res.status(500).json({ error: 'Reset failed' });
    }
    res.json({ success: true, message: 'Learning progress reset' });
  });
});

export default router;
