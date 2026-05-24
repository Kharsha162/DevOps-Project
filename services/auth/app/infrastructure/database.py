import os
import psycopg2
import sqlite3
import uuid
import logging
import threading
from app.core.models import User

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@127.0.0.1:5432/ecommerce")
        self.use_sqlite = False
        self.sqlite_conn = None
        self._initialized = False
        self._lock = threading.Lock()

    def _initialize_db(self):
        with self._lock:
            if self._initialized:
                return
            try:
                # Fast socket connection check first (0.2 seconds timeout)
                import socket
                from urllib.parse import urlparse
                parsed = urlparse(self.db_url)
                host = parsed.hostname or '127.0.0.1'
                port = parsed.port or 5432
                
                s = socket.create_connection((host, port), timeout=0.2)
                s.close()
                
                # Schema generation for PostgreSQL
                conn = psycopg2.connect(self.db_url, connect_timeout=1)
                cur = conn.cursor()
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id VARCHAR(50) PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        email VARCHAR(100) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        role VARCHAR(20) NOT NULL
                    )
                """)
                conn.commit()
                cur.close()
                conn.close()
                logger.info("PostgreSQL Database schema initialized successfully.")
            except Exception as e:
                logger.warning(f"PostgreSQL connection failed ({e}). Booting dynamic in-memory SQLite database fallback...")
                self.use_sqlite = True
                # Setup thread-safe in-memory SQLite database
                self.sqlite_conn = sqlite3.connect(":memory:", check_same_thread=False)
                cursor = self.sqlite_conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id TEXT PRIMARY KEY,
                        username TEXT UNIQUE NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        role TEXT NOT NULL
                    )
                """)
                self.sqlite_conn.commit()
                cursor.close()
            self._initialized = True

    def get_connection(self):
        self._initialize_db()
        if self.use_sqlite:
            return self.sqlite_conn
        return psycopg2.connect(self.db_url)

    def check_health(self):
        self._initialize_db()
        if self.use_sqlite:
            return False
        try:
            conn = psycopg2.connect(self.db_url, connect_timeout=1)
            conn.close()
            return True
        except Exception:
            return False


class UserRepository:
    def __init__(self, db_instance):
        self.db = db_instance

    def create(self, username, email, password_hash, role="user"):
        user_id = str(uuid.uuid4())
        conn = self.db.get_connection()
        if self.db.use_sqlite:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO users (id, username, email, password_hash, role) VALUES (?, ?, ?, ?, ?)",
                    (user_id, username, email, password_hash, role)
                )
                self.db.sqlite_conn.commit()
            finally:
                cursor.close()
        else:
            try:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO users (id, username, email, password_hash, role) VALUES (%s, %s, %s, %s, %s)",
                    (user_id, username, email, password_hash, role)
                )
                conn.commit()
                cur.close()
            finally:
                conn.close()
        return User(user_id, username, email, password_hash, role)

    def find_by_username(self, username):
        row = None
        conn = self.db.get_connection()
        if self.db.use_sqlite:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT id, username, email, password_hash, role FROM users WHERE username = ?", (username,))
                row = cursor.fetchone()
            finally:
                cursor.close()
        else:
            try:
                cur = conn.cursor()
                cur.execute("SELECT id, username, email, password_hash, role FROM users WHERE username = %s", (username,))
                row = cur.fetchone()
                cur.close()
                conn.close()
            except Exception:
                row = None
        
        if row:
            return User(row[0], row[1], row[2], row[3], row[4])
        return None

    def find_by_email(self, email):
        row = None
        conn = self.db.get_connection()
        if self.db.use_sqlite:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT id, username, email, password_hash, role FROM users WHERE email = ?", (email,))
                row = cursor.fetchone()
            finally:
                cursor.close()
        else:
            try:
                cur = conn.cursor()
                cur.execute("SELECT id, username, email, password_hash, role FROM users WHERE email = %s", (email,))
                row = cur.fetchone()
                cur.close()
                conn.close()
            except Exception:
                row = None
        
        if row:
            return User(row[0], row[1], row[2], row[3], row[4])
        return None
