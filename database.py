import mysql.connector
from mysql.connector import errorcode
from contextlib import contextmanager
from config import DB_CONFIG

# --- SQL table definitions ---
TABLES = {
    "products": """
        CREATE TABLE IF NOT EXISTS products (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            category VARCHAR(255),
            price DECIMAL(10,2) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """,
    "customers": """
        CREATE TABLE IF NOT EXISTS customers (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255),
            phone VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """,
    "sales": """
        CREATE TABLE IF NOT EXISTS sales (
            id INT AUTO_INCREMENT PRIMARY KEY,
            product_id INT NOT NULL,
            customer_id INT NOT NULL,
            sale_date DATE NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
            FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
        )
    """,
}


def get_connection():
    """Connect to MySQL; create database if it doesn't exist."""
    cfg = DB_CONFIG.copy()
    try:
        return mysql.connector.connect(**cfg)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            tmp_cfg = cfg.copy()
            db_name = tmp_cfg.pop("database")
            conn = mysql.connector.connect(**tmp_cfg)
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            conn.commit()
            cursor.close()
            conn.close()
            print(f"[database] Created missing database: {db_name}")
            return mysql.connector.connect(**cfg)
        else:
            raise


@contextmanager
def get_cursor(commit=False):
    """Yield a MySQL cursor; automatically commit/close."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        yield cursor
        if commit:
            conn.commit()
    finally:
        cursor.close()
        conn.close()


def init_db():
    """Initialize all required tables directly (no .sql file)."""
    conn = get_connection()
    cursor = conn.cursor()
    for name, ddl in TABLES.items():
        cursor.execute(ddl)
    conn.commit()
    cursor.close()
    conn.close()
    print("[database] Database and tables initialized successfully.")


def execute_query(query, params=None, commit=False):
    """Run a SQL query safely with automatic cleanup."""
    with get_cursor(commit=commit) as cursor:
        cursor.execute(query, params or ())
        if commit:
            return
        return cursor.fetchall()


def fetch_query(query, params=None):
    """Convenience function for SELECT queries."""
    with get_cursor() as cursor:
        cursor.execute(query, params or ())
        return cursor.fetchall()


