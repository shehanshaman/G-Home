-- Initialize the database.
-- Drop any existing data and create empty tables.

DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS switch;
DROP TABLE IF EXISTS trigger;
DROP TABLE IF EXISTS token;

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

CREATE TABLE token (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  auth_token VARCHAR(50) DEFAULT NULL
);

-- is_verified: 0-Unverified, 1-GeNet-User, 2-Google-User

CREATE TABLE switch (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL,
  name VARCHAR(20) NOT NULL,
  pin VARCHAR(5) NOT NULL,

  FOREIGN KEY (username) REFERENCES user (username)
);

CREATE TABLE trigger (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  switch_id INTEGER NOT NULL,
  value INTEGER DEFAULT 0,
  time INTEGER DEFAULT NULL,
  is_enable INTEGER DEFAULT 1,

  FOREIGN KEY (switch_id) REFERENCES switch (id)
);


-- Test data add

INSERT INTO switch (username, name, pin) VALUES
  ('user', 'A', 'D1'),
  ('user', 'B', 'D10'),
  ('user', 'C', 'D13');

INSERT INTO trigger (switch_id, value, time) VALUES
  (1, 1, 260),
  (1, 0, 290),
  (2, 1, 60),
  (2, 0, 20),
  (3, 0, 160),
  (3, 1, 260),
  (1, 1, 40);

INSERT INTO token (username, auth_token) VALUES ('user', 'abc123');

INSERT INTO user (username, given_name, password, last_login, is_verified, is_admin) VALUES ('user', 'user', 'pbkdf2:sha256:150000$LuBMEbIc$f3e7ec7e9061bad12ffb9193a8740722cc96be7e193c520e3aa551dc43c78b7c', '2020-04-10 17:24:15.484058', 3, 1);

