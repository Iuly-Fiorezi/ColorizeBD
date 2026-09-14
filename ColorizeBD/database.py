import os

import psycopg


def conectar():
    return psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "colorizedb"),
        user=os.getenv("DB_USER", "colorize_app"),
        password=os.environ["DB_PASSWORD"]
    )