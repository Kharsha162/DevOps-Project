import os
import uuid
import logging
import threading
import sqlite3

import psycopg2

from app.core.models import Cart, CartItem

logger = logging.getLogger(__name__)


class Database:
    def __init__(self):
        self.db_url = os.getenv(
            "DATABASE_URL",
            "postgresql://postgres:postgres@127.0.0.1:5432/ecommerce",
        )
        self.use_sqlite = False
        self.sqlite_conn = None
        self._initialized = False
        self._lock = threading.Lock()

    def _initialize_db(self):
        with self._lock:
            if self._initialized:
                return
            try:
                import socket
                from urllib.parse import urlparse

                parsed = urlparse(self.db_url)
                host = parsed.hostname or "127.0.0.1"
                port = parsed.port or 5432

                s = socket.create_connection((host, port), timeout=0.2)
                s.close()

                conn = psycopg2.connect(self.db_url, connect_timeout=1)
                cur = conn.cursor()
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS cart_items (
                        id VARCHAR(50) PRIMARY KEY,
                        user_id VARCHAR(50) NOT NULL,
                        product_id VARCHAR(50) NOT NULL,
                        name VARCHAR(100) NOT NULL,
                        price NUMERIC(10, 2) NOT NULL,
                        quantity INTEGER NOT NULL,
                        UNIQUE(user_id, product_id)
                    )
                    """
                )
                conn.commit()
                cur.close()
                conn.close()
                logger.info("PostgreSQL cart schema initialized successfully.")
            except Exception as exc:
                logger.warning(
                    "PostgreSQL connection failed (%s). Using SQLite in-memory fallback.",
                    exc,
                )
                self.use_sqlite = True
                self.sqlite_conn = sqlite3.connect(
                    ":memory:", check_same_thread=False
                )
                cursor = self.sqlite_conn.cursor()
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS cart_items (
                        id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        product_id TEXT NOT NULL,
                        name TEXT NOT NULL,
                        price REAL NOT NULL,
                        quantity INTEGER NOT NULL,
                        UNIQUE(user_id, product_id)
                    )
                    """
                )
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


class CartRepository:
    def __init__(self, db_instance):
        self.db = db_instance

    def _row_to_item(self, row):
        return CartItem(
            product_id=row[2],
            name=row[3],
            price=row[4],
            quantity=row[5],
            item_id=row[0],
        )

    def get_cart(self, user_id):
        conn = self.db.get_connection()
        rows = []
        if self.db.use_sqlite:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    """
                    SELECT id, user_id, product_id, name, price, quantity
                    FROM cart_items
                    WHERE user_id = ?
                    ORDER BY name
                    """,
                    (user_id,),
                )
                rows = cursor.fetchall()
            finally:
                cursor.close()
        else:
            cur = None
            try:
                cur = conn.cursor()
                cur.execute(
                    """
                    SELECT id, user_id, product_id, name, price, quantity
                    FROM cart_items
                    WHERE user_id = %s
                    ORDER BY name
                    """,
                    (user_id,),
                )
                rows = cur.fetchall()
            finally:
                if cur:
                    cur.close()
                conn.close()

        items = [self._row_to_item(row) for row in rows]
        return Cart(user_id, items)

    def add_item(self, user_id, product_id, name, price, quantity):
        conn = self.db.get_connection()
        item_id = str(uuid.uuid4())

        if self.db.use_sqlite:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    """
                    SELECT id, quantity FROM cart_items
                    WHERE user_id = ? AND product_id = ?
                    """,
                    (user_id, product_id),
                )
                existing = cursor.fetchone()
                if existing:
                    new_qty = existing[1] + quantity
                    cursor.execute(
                        "UPDATE cart_items SET quantity = ?, name = ?, price = ? WHERE id = ?",
                        (new_qty, name, float(price), existing[0]),
                    )
                else:
                    cursor.execute(
                        """
                        INSERT INTO cart_items (id, user_id, product_id, name, price, quantity)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (item_id, user_id, product_id, name, float(price), quantity),
                    )
                self.db.sqlite_conn.commit()
            finally:
                cursor.close()
        else:
            cur = None
            try:
                cur = conn.cursor()
                cur.execute(
                    """
                    SELECT id, quantity FROM cart_items
                    WHERE user_id = %s AND product_id = %s
                    """,
                    (user_id, product_id),
                )
                existing = cur.fetchone()
                if existing:
                    new_qty = existing[1] + quantity
                    cur.execute(
                        """
                        UPDATE cart_items
                        SET quantity = %s, name = %s, price = %s
                        WHERE id = %s
                        """,
                        (new_qty, name, price, existing[0]),
                    )
                else:
                    cur.execute(
                        """
                        INSERT INTO cart_items (id, user_id, product_id, name, price, quantity)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        (item_id, user_id, product_id, name, price, quantity),
                    )
                conn.commit()
            finally:
                if cur:
                    cur.close()
                conn.close()

        return self.get_cart(user_id)

    def remove_item(self, user_id, product_id, quantity=None):
        conn = self.db.get_connection()

        if self.db.use_sqlite:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    """
                    SELECT id, quantity FROM cart_items
                    WHERE user_id = ? AND product_id = ?
                    """,
                    (user_id, product_id),
                )
                existing = cursor.fetchone()
                if not existing:
                    return self.get_cart(user_id)

                if quantity is None or quantity >= existing[1]:
                    cursor.execute(
                        "DELETE FROM cart_items WHERE id = ?",
                        (existing[0],),
                    )
                else:
                    cursor.execute(
                        "UPDATE cart_items SET quantity = ? WHERE id = ?",
                        (existing[1] - quantity, existing[0]),
                    )
                self.db.sqlite_conn.commit()
            finally:
                cursor.close()
        else:
            cur = None
            try:
                cur = conn.cursor()
                cur.execute(
                    """
                    SELECT id, quantity FROM cart_items
                    WHERE user_id = %s AND product_id = %s
                    """,
                    (user_id, product_id),
                )
                existing = cur.fetchone()
                if not existing:
                    return self.get_cart(user_id)

                if quantity is None or quantity >= existing[1]:
                    cur.execute(
                        "DELETE FROM cart_items WHERE id = %s",
                        (existing[0],),
                    )
                else:
                    cur.execute(
                        "UPDATE cart_items SET quantity = %s WHERE id = %s",
                        (existing[1] - quantity, existing[0]),
                    )
                conn.commit()
            finally:
                if cur:
                    cur.close()
                conn.close()

        return self.get_cart(user_id)
