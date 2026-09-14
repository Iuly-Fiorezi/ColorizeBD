import hashlib
import secrets

import bcrypt

//geração do hash da senha, pra ficar mais seguro no banco
def gerar_hash_senha(senha: str) -> str:
    senha_bytes = senha.encode("utf-8")
    hash_bytes = bcrypt.hashpw(
        senha_bytes,
        bcrypt.gensalt()
    )

    return hash_bytes.decode("utf-8")

//função para verificar a senha, login e tals
def verificar_senha(senha: str, senha_hash: str) -> bool:
    senha_bytes = senha.encode("utf-8")
    hash_bytes = senha_hash.encode("utf-8")

    //função de checar correspondencia de password
    return bcrypt.checkpw(
        senha_bytes,
        hash_bytes
    )


def gerar_token_sessao() -> str:
    //cria uma sequencia aletoria de 32 caracteres
    return secrets.token_urlsafe(32)


def gerar_hash_token(token: str) -> str:
    token_bytes = token.encode("utf-8")

    //hash com o sha256 e o hexdigest() transforma em código hexadecimal(mais simples de salvar q bytes)
    return hashlib.sha256(token_bytes).hexdigest()
