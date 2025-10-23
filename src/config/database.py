from flask import current_app, g
import psycopg2
from psycopg2.extras import RealDictCursor


def get_db_connection():
    """Get a database connection from the pool"""
    if 'db_conn' not in g:
        g.db_conn = current_app.db_pool.getconn()
    return g.db_conn


def close_db_connection():
    """Return connection to the pool"""
    db_conn = g.pop('db_conn', None)
    if db_conn is not None:
        current_app.db_pool.putconn(db_conn)


def execute_query(query, params=None, fetch=False):
    """Execute a query and optionally fetch results"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute(query, params)
        if fetch:
            result = cursor.fetchall()
            return result
        else:
            conn.commit()
            return cursor.rowcount
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()