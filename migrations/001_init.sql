CREATE TABLE IF NOT EXISTS user (
 id INTEGER PRIMARY KEY,
 first_name VARCHAR(120) NOT NULL,
 last_name VARCHAR(120) NOT NULL,
 full_address VARCHAR(255) NOT NULL,
 email VARCHAR(255) UNIQUE NOT NULL,
 password_hash VARCHAR(255) NOT NULL,
 marketing_opt_in BOOLEAN DEFAULT 0,
 status VARCHAR(20) DEFAULT 'PENDING',
 membership_level VARCHAR(20) DEFAULT 'BASIC',
 locale VARCHAR(10),
 last_hl INTEGER,
 last_fd INTEGER,
 last_sb INTEGER,
 created_at DATETIME
);
CREATE TABLE IF NOT EXISTS approval_token (
 id INTEGER PRIMARY KEY,
 user_id INTEGER NOT NULL,
 purpose VARCHAR(50) NOT NULL,
 action VARCHAR(10) NOT NULL,
 token_hash VARCHAR(64) UNIQUE NOT NULL,
 expires_at DATETIME NOT NULL,
 used_at DATETIME,
 created_at DATETIME,
 FOREIGN KEY(user_id) REFERENCES user(id)
);
CREATE TABLE IF NOT EXISTS audit_log (
 id INTEGER PRIMARY KEY,
 user_id INTEGER NOT NULL,
 event VARCHAR(80) NOT NULL,
 meta TEXT,
 created_at DATETIME,
 FOREIGN KEY(user_id) REFERENCES user(id)
);
CREATE TABLE IF NOT EXISTS rater_application (
 id INTEGER PRIMARY KEY,
 user_id INTEGER NOT NULL,
 intended_use TEXT NOT NULL,
 wine_types TEXT NOT NULL,
 expected_frequency VARCHAR(120) NOT NULL,
 status VARCHAR(20) DEFAULT 'PENDING',
 created_at DATETIME,
 FOREIGN KEY(user_id) REFERENCES user(id)
);
CREATE TABLE IF NOT EXISTS wine (
 id INTEGER PRIMARY KEY,
 wine_name VARCHAR(255) NOT NULL,
 estate VARCHAR(255) NOT NULL,
 vintage INTEGER NOT NULL,
 wine_specific_name VARCHAR(255) NOT NULL,
 country VARCHAR(120) NOT NULL,
 region VARCHAR(120) NOT NULL,
 sub_region VARCHAR(120) NOT NULL,
 score_heavy_light INTEGER NOT NULL,
 score_fruity_dry INTEGER NOT NULL,
 score_smooth_bright INTEGER NOT NULL,
 winemaker_notes TEXT NOT NULL,
 md_review TEXT,
 md_score FLOAT,
 lead_varietal VARCHAR(120) NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_wine_scores ON wine(score_heavy_light,score_fruity_dry,score_smooth_bright);
CREATE TABLE IF NOT EXISTS wine_varietal (
 id INTEGER PRIMARY KEY,
 wine_id INTEGER NOT NULL,
 varietal VARCHAR(120) NOT NULL,
 percentage FLOAT,
 sort_order INTEGER NOT NULL,
 FOREIGN KEY(wine_id) REFERENCES wine(id)
);
CREATE TABLE IF NOT EXISTS notify_request (
 id INTEGER PRIMARY KEY,
 user_id INTEGER NOT NULL,
 hl INTEGER NOT NULL,
 fd INTEGER NOT NULL,
 sb INTEGER NOT NULL,
 created_at DATETIME,
 FOREIGN KEY(user_id) REFERENCES user(id)
);
CREATE TABLE IF NOT EXISTS enquiry (
 id INTEGER PRIMARY KEY,
 user_id INTEGER,
 from_email VARCHAR(255) NOT NULL,
 subject VARCHAR(255) NOT NULL,
 body TEXT NOT NULL,
 status VARCHAR(30) NOT NULL,
 provider_id VARCHAR(255),
 created_at DATETIME,
 FOREIGN KEY(user_id) REFERENCES user(id)
);
CREATE TABLE IF NOT EXISTS analytics_event (
 id INTEGER PRIMARY KEY,
 user_id INTEGER,
 event_name VARCHAR(80) NOT NULL,
 payload TEXT,
 created_at DATETIME,
 FOREIGN KEY(user_id) REFERENCES user(id)
);
