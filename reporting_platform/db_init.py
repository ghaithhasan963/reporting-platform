import sqlite3

def init_db():
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        username TEXT
    )""")
    conn.commit()
    conn.close()

def add_user(username, password):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()

def find_user(username):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    return {"username": row[0], "password": row[1]} if row else None

def save_report(content, username):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("INSERT INTO reports (content, username) VALUES (?, ?)", (content, username))
    conn.commit()
    conn.close()

def get_reports():
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT content, username FROM reports ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return [{"text": row[0], "user": row[1]} for row in rows]
