import sqlite3 from 'sqlite3';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { vocabularyData } from './vocabulary-data.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const dbPath = join(__dirname, '../japanese_learning.db');

const db = new sqlite3.Database(dbPath, (err) => {
  if (err) {
    console.error('Database connection error:', err.message);
  } else {
    console.log('Connected to SQLite database');
  }
});

// Initialize database tables
const initDb = () => {
  db.serialize(() => {
    // Users table
    db.run(`
      CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        name TEXT,
        is_premium INTEGER DEFAULT 0,
        premium_expires_at DATETIME,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `);

    // Vocabulary table
    db.run(`
      CREATE TABLE IF NOT EXISTS vocabulary (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        japanese TEXT NOT NULL,
        hiragana TEXT NOT NULL,
        romaji TEXT NOT NULL,
        meaning_en TEXT,
        meaning_zh TEXT,
        jlpt_level TEXT,
        category TEXT,
        example_sentence TEXT,
        example_translation TEXT,
        is_premium INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `);

    // Create indexes for better search performance
    db.run(`CREATE INDEX IF NOT EXISTS idx_vocab_jlpt ON vocabulary(jlpt_level)`);
    db.run(`CREATE INDEX IF NOT EXISTS idx_vocab_category ON vocabulary(category)`);
    db.run(`CREATE INDEX IF NOT EXISTS idx_vocab_japanese ON vocabulary(japanese)`);
    db.run(`CREATE INDEX IF NOT EXISTS idx_vocab_hiragana ON vocabulary(hiragana)`);
    db.run(`CREATE INDEX IF NOT EXISTS idx_vocab_romaji ON vocabulary(romaji)`);

    // User learning progress
    db.run(`
      CREATE TABLE IF NOT EXISTS learning_progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        vocabulary_id INTEGER,
        times_correct INTEGER DEFAULT 0,
        times_incorrect INTEGER DEFAULT 0,
        last_reviewed DATETIME,
        next_review_date DATETIME,
        mastery_level INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (vocabulary_id) REFERENCES vocabulary(id),
        UNIQUE(user_id, vocabulary_id)
      )
    `);

    // Payments table
    db.run(`
      CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        amount REAL,
        currency TEXT DEFAULT 'CNY',
        payment_method TEXT,
        transaction_id TEXT,
        status TEXT DEFAULT 'pending',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
      )
    `);

    // User settings
    db.run(`
      CREATE TABLE IF NOT EXISTS user_settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        show_romaji INTEGER DEFAULT 1,
        show_hiragana INTEGER DEFAULT 1,
        show_kanji INTEGER DEFAULT 1,
        daily_goal INTEGER DEFAULT 20,
        notification_enabled INTEGER DEFAULT 1,
        FOREIGN KEY (user_id) REFERENCES users(id),
        UNIQUE(user_id)
      )
    `);

    // Favorites table
    db.run(`
      CREATE TABLE IF NOT EXISTS favorites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        vocabulary_id INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (vocabulary_id) REFERENCES vocabulary(id),
        UNIQUE(user_id, vocabulary_id)
      )
    `);

    console.log('Database tables initialized');
  });
};

// Seed vocabulary data
const seedVocabulary = () => {
  db.get("SELECT COUNT(*) as count FROM vocabulary", (err, row) => {
    if (err) {
      console.error('Error checking vocabulary count:', err);
      return;
    }

    if (row.count === 0) {
      console.log(`Seeding ${vocabularyData.length} vocabulary items...`);

      db.serialize(() => {
        db.run("BEGIN TRANSACTION");

        const stmt = db.prepare(`
          INSERT INTO vocabulary (japanese, hiragana, romaji, meaning_en, meaning_zh, jlpt_level, category, example_sentence, example_translation, is_premium)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        `);

        let count = 0;
        vocabularyData.forEach(v => {
          stmt.run(
            v.japanese,
            v.hiragana,
            v.romaji,
            v.meaning_en,
            v.meaning_zh,
            v.jlpt_level,
            v.category,
            v.example_sentence || null,
            v.example_translation || null,
            v.is_premium
          );
          count++;
        });

        stmt.finalize(() => {
          db.run("COMMIT");
          console.log(`Successfully seeded ${count} vocabulary items`);

          // Print level distribution
          db.all("SELECT jlpt_level, COUNT(*) as count FROM vocabulary GROUP BY jlpt_level ORDER BY jlpt_level", (err, rows) => {
            if (!err && rows) {
              console.log("\nVocabulary by level:");
              rows.forEach(r => console.log(`  ${r.jlpt_level}: ${r.count} words`));
            }
          });
        });
      });
    } else {
      console.log(`Vocabulary already seeded (${row.count} items)`);
    }
  });
};

// Reseed vocabulary (drop and re-insert)
const reseedVocabulary = () => {
  db.run("DELETE FROM vocabulary", (err) => {
    if (err) {
      console.error('Error clearing vocabulary:', err);
      return;
    }
    console.log('Vocabulary table cleared, re-seeding...');
    seedVocabulary();
  });
};

export { db, initDb, seedVocabulary, reseedVocabulary };
