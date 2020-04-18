-- Initialize the database.
-- Drop any existing data and create empty tables.

DROP TABLE IF EXISTS user;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  given_name VARCHAR(20) NOT NULL,
  image_url TEXT,
  last_login DATETIME NOT NULL,
  is_verified INTEGER NOT NULL,
  want_tour INTEGER DEFAULT 1,
  is_admin INTEGER DEFAULT 0
);

-- is_verified: 0-Unverified, 1-GeNet-User, 2-Google-User


INSERT INTO user (username, given_name, password, last_login, is_verified, is_admin) VALUES ('user', 'user', 'pbkdf2:sha256:150000$LuBMEbIc$f3e7ec7e9061bad12ffb9193a8740722cc96be7e193c520e3aa551dc43c78b7c', '2020-04-10 17:24:15.484058', 3, 1);

