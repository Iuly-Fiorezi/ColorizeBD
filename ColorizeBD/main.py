from datetime import datetime, timedelta, timezone

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from psycopg.errors import UniqueViolation

from auth import (
    gerar_hash_senha,
    verificar_senha,
    gerar_token_sessao,
    gerar_hash_token
)
from database import conectar


app = FastAPI()

seguranca = HTTPBearer()

//classe, molde doq espera receber pra executar função de cadastro
class CadastroUsuario(BaseModel):
    nome: str
    email: str
    senha: str

//mesma coisa soq pra login
class LoginUsuario(BaseModel):
    email: str
    senha: str


def obter_usuario_autenticado(
    credenciais: HTTPAuthorizationCredentials = Depends(seguranca)
):
    token = credenciais.credentials
    token_hash = gerar_hash_token(token)

    sql = """
        SELECT usuarios.id, usuarios.nome, usuarios.email, usuarios.tipo
        FROM sessoes
        JOIN usuarios ON usuarios.id = sessoes.usuario_id
        WHERE sessoes.token_hash = %s
        AND sessoes.expira_em > CURRENT_TIMESTAMP;
    """

    conexao = conectar()
    cursor = conexao.cursor()

    try:
        cursor.execute(
            sql,
            (token_hash,)
        )

        resultado = cursor.fetchone()

        if resultado is None:
            raise HTTPException(
                status_code=401,
                detail="Sessão inválida ou expirada"
            )

        return {
            "id": resultado[0],
            "nome": resultado[1],
            "email": resultado[2],
            "tipo": resultado[3],
            "token_hash": token_hash
        }

    finally:
        cursor.close()
        conexao.close()


def obter_admin(
    usuario_atual=Depends(obter_usuario_autenticado)
):
    if usuario_atual["tipo"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Acesso restrito a administradores"
        )

    return usuario_atual

//o app, que é objeto da FastAPI pega o endereço do código, então pode ser acessado
@app.get("/")
def inicio():
    return {
        "mensagem": "Servidor funcionando"
    }

//roda a função quando o /me for executado
@app.get("/me")
def meu_usuario(
    //pra definir usuario atual o usuario precisa estar autenticado
    usuario_atual=Depends(obter_usuario_autenticado)
):
    //retorna essas informações
    return {
        "id": usuario_atual["id"],
        "nome": usuario_atual["nome"],
        "email": usuario_atual["email"],
        "tipo": usuario_atual["tipo"]
    }


@app.get("/admin/teste")
def teste_admin(
    admin=Depends(obter_admin)
):
    return {
        "mensagem": "Acesso de administrador autorizado",
        "admin": {
            "id": admin["id"],
            "nome": admin["nome"],
            "email": admin["email"],
            "tipo": admin["tipo"]
        }
    }

//quando executado o cadastro roda
@app.post("/cadastro")
def cadastrar(usuario: CadastroUsuario):
    //gera a senha hash usando a função criada em auth
    senha_hash = gerar_hash_senha(usuario.senha)

    //pega as informações e transforma em sql, mas ainda n define no bd
    sql = """
        INSERT INTO usuarios (nome, email, senha_hash)
        VALUES (%s, %s, %s)
        RETURNING id, criado_em;
    """

    //ativa afunção conectar do database
    conexao = conectar()
    //objeto que usamos pra mandar sql pela conexão
    cursor = conexao.cursor()

    try:
        //envia de verdade para o bd
        cursor.execute(
            sql,
            (
                usuario.nome,
                usuario.email,
                senha_hash
            )
        )

        //recebe a linha retornada no bd
        resultado = cursor.fetchone()
        //separa o id a data de criação retornados
        id_usuario = resultado[0]
        criado_em = resultado[1]

        //salva definitavamente
        conexao.commit()
    //
    except UniqueViolation:
        conexao.rollback()
        
        raise HTTPException(
            status_code=409,
            detail="Este email já está cadastrado"
        )

    finally:
        cursor.close()
        conexao.close()

    return {
        "id": id_usuario,
        "nome": usuario.nome,
        "email": usuario.email,
        "criado_em": criado_em
    }


@app.post("/login")
def login(usuario: LoginUsuario):
    sql = """
        SELECT id, nome, email, senha_hash, tipo
        FROM usuarios
        WHERE email = %s;
    """

    conexao = conectar()
    cursor = conexao.cursor()

    try:
        cursor.execute(
            sql,
            (usuario.email,)
        )

        resultado = cursor.fetchone()

        if resultado is None:
            raise HTTPException(
                status_code=401,
                detail="Email ou senha inválidos"
            )

        id_usuario = resultado[0]
        nome = resultado[1]
        email = resultado[2]
        senha_hash = resultado[3]
        tipo = resultado[4]

        if not verificar_senha(
            usuario.senha,
            senha_hash
        ):
            raise HTTPException(
                status_code=401,
                detail="Email ou senha inválidos"
            )

        token = gerar_token_sessao()
        token_hash = gerar_hash_token(token)

        expira_em = (
            datetime.now(timezone.utc)
            + timedelta(days=7)
        )

        sql_sessao = """
            INSERT INTO sessoes (
                usuario_id,
                token_hash,
                expira_em
            )
            VALUES (%s, %s, %s);
        """

        cursor.execute(
            sql_sessao,
            (
                id_usuario,
                token_hash,
                expira_em
            )
        )

        conexao.commit()

        return {
            "mensagem": "Login realizado com sucesso",
            "id": id_usuario,
            "nome": nome,
            "email": email,
            "tipo": tipo,
            "token": token,
            "expira_em": expira_em
        }

    finally:
        cursor.close()
        conexao.close()


@app.post("/logout")
def logout(
    usuario_atual=Depends(obter_usuario_autenticado)
):
    sql = """
        DELETE FROM sessoes
        WHERE token_hash = %s;
    """

    conexao = conectar()
    cursor = conexao.cursor()

    try:
        cursor.execute(
            sql,
            (usuario_atual["token_hash"],)
        )

        conexao.commit()

    finally:
        cursor.close()
        conexao.close()

    return {
        "mensagem": "Logout realizado com sucesso"
    }
