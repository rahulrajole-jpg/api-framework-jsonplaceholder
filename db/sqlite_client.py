import sqlite3
from threading import Lock

class SQLiteClient:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
                cls._instance.conn = sqlite3.connect(":memory:", check_same_thread=False) # In memory validation
                # cls._instance.conn = sqlite3.connect("test.db", check_same_thread=False) # For file-based DB
                cls._instance._create_tables()
            return cls._instance

    def _create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, username TEXT, email TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY, userId INTEGER, title TEXT, body TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS comments (id INTEGER PRIMARY KEY, postId INTEGER, name TEXT, email TEXT, body TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS albums (id INTEGER PRIMARY KEY, userId INTEGER, title TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS todos (id INTEGER PRIMARY KEY, userId INTEGER, title TEXT, completed BOOLEAN)''')
        self.conn.commit()

    def insert(self, table, data):
        keys = ','.join(data.keys())
        question_marks = ','.join(['?'] * len(data))
        values = tuple(data.values())
        self.conn.execute(f"INSERT INTO {table} ({keys}) VALUES ({question_marks})", values)
        self.conn.commit()

    def fetchall(self, table):
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM {table}")
        return cursor.fetchall()
