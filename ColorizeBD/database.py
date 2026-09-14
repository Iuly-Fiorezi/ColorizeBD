import os

import psycopg


def conectar():
    //abre a conexão com banco
    return psycopg.connect(
        //onde está
        host=os.getenv("DB_HOST", "localhost"),
        //porta
        port=os.getenv("DB_PORT", "5432"),
        //qual banco vai usar
        dbname=os.getenv("DB_NAME", "colorizedb"),
        //quem vai usar
        user=os.getenv("DB_USER", "colorize_app"),
        //qual a senha
        password=os.environ["DB_PASSWORD"]
        //é diferente pq se for nulo vai dar erro
        //no geral tenta pegar o da esquerda, se não tiver o da direita vai ser definido
    )
    
