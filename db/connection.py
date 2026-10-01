# ============================================================
#  db/connection.py — MySQL connection manager
#  Risk Management System  ·  by Sasindu Dilshara
# ============================================================

import sys
import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG


class DBConnection:
    """Singleton-style MySQL connection wrapper."""

    _conn = None

    @classmethod
    def get(cls):
        if cls._conn is None or not cls._conn.is_connected():
            try:
                cls._conn = mysql.connector.connect(**DB_CONFIG)
            except Error as e:
                print(f"\n[DB ERROR] Cannot connect to MySQL: {e}")
                print("  → Make sure MySQL is running and credentials in config.py are correct.\n")
                sys.exit(1)
        return cls._conn

    @classmethod
    def cursor(cls, dictionary=True):
        return cls.get().cursor(dictionary=dictionary)

    @classmethod
    def close(cls):
        if cls._conn and cls._conn.is_connected():
            cls._conn.close()
