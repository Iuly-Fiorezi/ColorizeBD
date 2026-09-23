import os

import psycopg


def conectar():
    # Abre a conexão com o banco PostgreSQL.
    return psycopg.connect(
        # Onde o banco está.
        host=os.getenv("DB_HOST", "localhost"),

        # Porta do PostgreSQL.
        port=os.getenv("DB_PORT", "5432"),

        # Banco usado pelo servidor.
        dbname=os.getenv("DB_NAME", "colorizedb"),

        # Usuário PostgreSQL usado pela aplicação.
        user=os.getenv("DB_USER", "colorize_app"),

        # A senha é obrigatória e vem de uma variável de ambiente.
        password=os.environ["DB_PASSWORD"]
    )
