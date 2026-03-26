"""Database connection management for PostgreSQL"""

import os
import logging
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from contextlib import contextmanager
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class Database:
    """PostgreSQL database connection with connection pooling"""

    def __init__(
        self,
        host: str = None,
        port: int = None,
        database: str = None,
        user: str = None,
        password: str = None
    ):
        """Initialize database connection pool

        Args can be passed directly or loaded from environment variables:
        - DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
        """
        self.host = host or os.getenv('DB_HOST', 'localhost')
        self.port = port or int(os.getenv('DB_PORT', '5432'))
        self.database = database or os.getenv('DB_NAME', 'litellm')
        self.user = user or os.getenv('DB_USER', 'taasaa')
        self.password = password or os.getenv('DB_PASSWORD', '')

        # Create connection pool
        self.pool = SimpleConnectionPool(
            1, 5,  # min/max connections
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.user,
            password=self.password if self.password else None
        )

    @contextmanager
    def connection(self):
        """Get connection from pool as context manager"""
        conn = self.pool.getconn()
        try:
            yield conn
        finally:
            self.pool.putconn(conn)

    def execute(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Execute query and return results as list of dicts

        Args:
            query: SQL query string
            params: Query parameters (optional)

        Returns:
            List of dictionaries, where each dict is a row
        """
        with self.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)

                # Check if query returned results
                if cur.description is None:
                    return []

                # Get column names
                columns = [desc[0] for desc in cur.description]

                # Convert to list of dicts
                return [dict(zip(columns, row)) for row in cur.fetchall()]

    def execute_one(self, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """Execute query and return single result as dict

        Args:
            query: SQL query string
            params: Query parameters (optional)

        Returns:
            Single dictionary or None if no results
        """
        results = self.execute(query, params)
        return results[0] if results else None

    def close(self):
        """Close all connections in the pool"""
        self.pool.closeall()

    def test_connection(self) -> bool:
        """Test if connection is working

        Returns:
            True if connection works, False otherwise
        """
        try:
            with self.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False