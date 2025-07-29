import sqlite3

conn = sqlite3.connect("platform.db")
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT,
    trust_level TEXT DEFAULT 'مبتدئ',
    status TEXT DEFAULT 'active',
    fb_link TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    url TEXT,
    description TEXT,
    screenshot_path TEXT,
    created_at TEXT,
    is_verified INTEGER DEFAULT 0
)''')

c.execute('''CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipient_id INTEGER,
    message TEXT,
    created_at TEXT
)''')

conn.commit()
conn.close()