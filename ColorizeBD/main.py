from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class CadastroUsuario(BaseModel):
    nome: str
    email: str
    senha: str


@app.get("/")
def inicio():
    return {"mensagem": "Servidor funcionando"}


@app.post("/cadastro")
def cadastrar(usuario: CadastroUsuario):
    return {
        "nome": usuario.nome,
        "email": usuario.email
    }