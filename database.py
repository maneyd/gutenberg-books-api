import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()


def get_db_connection():
    """Connect to PostgreSQL database"""
    return psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            database=os.getenv('DB_NAME', 'gutendex'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', '')
        )
