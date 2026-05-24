import os
import psycopg2
import sqlite3
import uuid
import logging
import threading
from app.core.models import Product

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        # Default local credentials (port 5433, password 1234, database ecommerce)
        self.db_url = os.getenv("DATABASE_URL", "postgresql://postgres:1234@127.0.0.1:5433/ecommerce")
        self.use_sqlite = False
        self.sqlite_conn = None
        self._initialized = False
        self._lock = threading.Lock()

    def _initialize_db(self):
        with self._lock:
            if self._initialized:
                return
            try:
                # Fast socket connection check first (0.2s timeout)
                import socket
                from urllib.parse import urlparse
                parsed = urlparse(self.db_url)
                host = parsed.hostname or '127.0.0.1'
                port = parsed.port or 5433
                
                s = socket.create_connection((host, port), timeout=0.2)
                s.close()
                
                # Schema creation for PostgreSQL
                conn = psycopg2.connect(self.db_url, connect_timeout=1)
                cur = conn.cursor()
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS products (
                        id VARCHAR(50) PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        description TEXT,
                        price NUMERIC(10, 2) NOT NULL,
                        stock INTEGER NOT NULL,
                        category VARCHAR(50) DEFAULT 'general'
                    )
                """)
                conn.commit()
                cur.close()
                conn.close()
                logger.info("PostgreSQL Database schema initialized successfully.")
            except Exception as e:
                logger.warning(f"PostgreSQL connection failed ({e}). Booting SQLite in-memory fallback...")
                self.use_sqlite = True
                self.sqlite_conn = sqlite3.connect(":memory:", check_same_thread=False)
                cursor = self.sqlite_conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS products (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        description TEXT,
                        price REAL NOT NULL,
                        stock INTEGER NOT NULL,
                        category TEXT DEFAULT 'general'
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


class ProductRepository:
    def __init__(self, db_instance):
        self.db = db_instance

    def create(self, name, description, price, stock, category="general"):
        product_id = str(uuid.uuid4())
        conn = self.db.get_connection()
        if self.db.use_sqlite:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO products (id, name, description, price, stock, category) VALUES (?, ?, ?, ?, ?, ?)",
                    (product_id, name, description, float(price), int(stock), category)
                )
                self.db.sqlite_conn.commit()
            finally:
                cursor.close()
        else:
            try:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO products (id, name, description, price, stock, category) VALUES (%s, %s, %s, %s, %s, %s)",
                    (product_id, name, description, price, stock, category)
                )
                conn.commit()
                cur.close()
            finally:
                conn.close()
        return Product(product_id, name, description, price, stock, category)

    def find_by_id(self, product_id):
        row = None
        conn = self.db.get_connection()
        if self.db.use_sqlite:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT id, name, description, price, stock, category FROM products WHERE id = ?", (product_id,))
                row = cursor.fetchone()
            finally:
                cursor.close()
        else:
            try:
                cur = conn.cursor()
                cur.execute("SELECT id, name, description, price, stock, category FROM products WHERE id = %s", (product_id,))
                row = cur.fetchone()
                cur.close()
                conn.close()
            except Exception:
                row = None
        
        if row:
            return Product(row[0], row[1], row[2], row[3], row[4], row[5])
        return None

    def update(self, product_id, name=None, description=None, price=None, stock=None, category=None):
        conn = self.db.get_connection()
        
        # Resolve existing
        p = self.find_by_id(product_id)
        if not p:
            if not self.db.use_sqlite:
                conn.close()
            return None

        # Build update query dynamically
        fields = []
        values = []
        
        if name is not None:
            fields.append("name")
            values.append(name)
        if description is not None:
            fields.append("description")
            values.append(description)
        if price is not None:
            fields.append("price")
            values.append(float(price))
        if stock is not None:
            fields.append("stock")
            values.append(int(stock))
        if category is not None:
            fields.append("category")
            values.append(category)

        if not fields:
            if not self.db.use_sqlite:
                conn.close()
            return p

        if self.db.use_sqlite:
            cursor = conn.cursor()
            try:
                set_clause = ", ".join([f"{f} = ?" for f in fields])
                query = f"UPDATE products SET {set_clause} WHERE id = ?"
                cursor.execute(query, (*values, product_id))
                self.db.sqlite_conn.commit()
            finally:
                cursor.close()
        else:
            try:
                cur = conn.cursor()
                set_clause = ", ".join([f"{f} = %s" for f in fields])
                query = f"UPDATE products SET {set_clause} WHERE id = %s"
                cur.execute(query, (*values, product_id))
                conn.commit()
                cur.close()
            finally:
                conn.close()

        return self.find_by_id(product_id)

    def delete(self, product_id):
        conn = self.db.get_connection()
        if self.db.use_sqlite:
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
                self.db.sqlite_conn.commit()
            finally:
                cursor.close()
        else:
            try:
                cur = conn.cursor()
                cur.execute("DELETE FROM products WHERE id = %s", (product_id,))
                conn.commit()
                cur.close()
            finally:
                conn.close()
        return True

    def find_all(self, search_query=None, limit=10, offset=0):
        conn = self.db.get_connection()
        rows = []
        
        if self.db.use_sqlite:
            cursor = conn.cursor()
            try:
                if search_query:
                    query = "%" + search_query + "%"
                    cursor.execute(
                        "SELECT id, name, description, price, stock, category FROM products WHERE name LIKE ? OR description LIKE ? LIMIT ? OFFSET ?",
                        (query, query, limit, offset)
                    )
                else:
                    cursor.execute("SELECT id, name, description, price, stock, category FROM products LIMIT ? OFFSET ?", (limit, offset))
                rows = cursor.fetchall()
            finally:
                cursor.close()
        else:
            cur = None
            try:
                cur = conn.cursor()
                if search_query:
                    query = "%" + search_query + "%"
                    cur.execute(
                        "SELECT id, name, description, price, stock, category FROM products WHERE name ILIKE %s OR description ILIKE %s LIMIT %s OFFSET %s",
                        (query, query, limit, offset)
                    )
                else:
                    cur.execute("SELECT id, name, description, price, stock, category FROM products LIMIT %s OFFSET %s", (limit, offset))
                rows = cur.fetchall()
            except Exception as e:
                logger.error(f"Error querying products from Postgres: {e}")
                rows = []
            finally:
                if cur:
                    cur.close()
                conn.close()

        return [Product(r[0], r[1], r[2], r[3], r[4], r[5]) for r in rows]
