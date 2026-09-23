import hashlib
import secrets

import bcrypt


# Geração do hash da senha para armazenar no banco com segurança.
def gerar_hash_senha(senha: str) -> str:
    senha_bytes = senha.encode("utf-8")
    hash_bytes = bcrypt.hashpw(
        senha_bytes,
        bcrypt.gensalt()
    )

    return hash_bytes.decode("utf-8")


# Verifica se a senha digitada corresponde ao hash salvo.
def verificar_senha(senha: str, senha_hash: str) -> bool:
    senha_bytes = senha.encode("utf-8")
    hash_bytes = senha_hash.encode("utf-8")

    return bcrypt.checkpw(
        senha_bytes,
        hash_bytes
    )


def gerar_token_sessao() -> str:
    # Cria um token aleatório seguro.
    return secrets.token_urlsafe(32)


def gerar_hash_token(token: str) -> str:
    token_bytes = token.encode("utf-8")

    # SHA-256 gera o hash; hexdigest() o transforma em texto hexadecimal.
    return hashlib.sha256(token_bytes).hexdigest()
