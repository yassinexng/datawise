-- User accounts table
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    code_verification TEXT,
    is_verified INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Email verification tracking
CREATE TABLE IF NOT EXISTS email_verifications (
    username TEXT PRIMARY KEY,
    code TEXT NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    attempts INTEGER DEFAULT 0,
    verified_at TIMESTAMP,
    FOREIGN KEY(username) REFERENCES users(username) ON DELETE CASCADE
);

-- Dataset information storage
CREATE TABLE IF NOT EXISTS datasets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    name TEXT NOT NULL,
    content TEXT NOT NULL,
    file_path TEXT UNIQUE,
    status TEXT DEFAULT 'pending',
    row_count INTEGER,
    column_count INTEGER,
    file_size INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(username) REFERENCES users(username) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_datasets_username ON datasets(username);
CREATE INDEX IF NOT EXISTS idx_datasets_status ON datasets(status);
