import platform
import ctypes
import json
import urllib.request
import urllib.error

import customtkinter
from PIL import ImageGrab, Image

from cores_windows import ControladorGamma


# TESTE LOCAL:
# cliente e servidor rodando no mesmo computador.
BASE_URL = "http://127.0.0.1:8000"

# LINUX MINT:
# quando o servidor estiver em outra máquina,
# trocar pelo IP/endereço real do servidor.
# Exemplo:
# BASE_URL = "http://192.168.1.50:8000"


token_sessao = None
usuario_logado = None


def enviar_requisicao(rota, metodo="GET", dados=None, token=None):
    url = BASE_URL + rota

    corpo = None
    headers = {}

    if dados is not None:
        corpo = json.dumps(dados).encode("utf-8")
        headers["Content-Type"] = "application/json"

    if token is not None:
        headers["Authorization"] = f"Bearer {token}"

    requisicao = urllib.request.Request(
        url,
        data=corpo,
        headers=headers,
        method=metodo
    )

    with urllib.request.urlopen(
        requisicao,
        timeout=5
    ) as resposta:

        conteudo = resposta.read().decode("utf-8")

        if not conteudo:
            return None

        return json.loads(conteudo)


def ler_erro_http(erro, mensagem_padrao):
    try:
        resposta = json.loads(
            erro.read().decode("utf-8")
        )

        detalhe = resposta.get("detail")

        if isinstance(detalhe, str):
            return detalhe

    except Exception:
        pass

    return mensagem_padrao


def cadastrar_usuario(nome, email, senha):
    dados = {
        "nome": nome,
        "email": email,
        "senha": senha
    }

    try:
        enviar_requisicao(
            "/cadastro",
            metodo="POST",
            dados=dados
        )

        return True, None

    except urllib.error.HTTPError as erro:
        corpo_erro = erro.read().decode("utf-8")

        print("STATUS:", erro.code)
        print("RESPOSTA DO SERVIDOR:", corpo_erro)

        return False, f"Erro HTTP {erro.code}"

    except urllib.error.URLError:
        return False, "Não foi possível conectar ao servidor."


def verificar_usuario(email, senha):
    global token_sessao
    global usuario_logado

    dados = {
        "email": email,
        "senha": senha
    }

    try:
        resposta = enviar_requisicao(
            "/login",
            metodo="POST",
            dados=dados
        )

        token_sessao = resposta["token"]
        usuario_logado = resposta

        return True, None

    except urllib.error.HTTPError as erro:
        mensagem_erro = ler_erro_http(
            erro,
            "E-mail ou senha incorretos."
        )

        return False, mensagem_erro

    except urllib.error.URLError:
        return False, "Não foi possível conectar ao servidor."


janela = customtkinter.CTk()
janela.title("Colorize")
janela.geometry("800x600")
janela.configure(fg_color="#9A9A9A")


controlador_gamma = (
    ControladorGamma()
    if platform.system() == "Windows"
    else None
)

filtro_ativo = False
janela_conta_gotas = None


def limpar_janela():
    for widget in janela.winfo_children():
        widget.destroy()


def criar_cabecalho():
    cabecalho = customtkinter.CTkFrame(
        janela,
        height=65,
        corner_radius=0,
        fg_color="white"
    )

    cabecalho.pack(fill="x")

    titulo = customtkinter.CTkLabel(
        cabecalho,
        text="👁 PROJETO COLORIZE",
        text_color="black",
        font=("Arial", 20, "bold")
    )

    titulo.pack(pady=17)


def mostrar_mensagem(texto, cor="black"):
    mensagem.configure(
        text=texto,
        text_color=cor
    )


def tela_login():
    global mensagem

    limpar_janela()
    criar_cabecalho()

    caixa = customtkinter.CTkFrame(
        janela,
        width=400,
        height=350,
        corner_radius=15,
        fg_color="white"
    )

    caixa.place(
        relx=0.5,
        rely=0.52,
        anchor="center"
    )

    titulo = customtkinter.CTkLabel(
        caixa,
        text="Entrar",
        text_color="black",
        font=("Arial", 26, "bold")
    )

    titulo.pack(pady=(35, 25))

    email = customtkinter.CTkEntry(
        caixa,
        width=300,
        placeholder_text="E-mail"
    )

    email.pack(pady=10)

    senha = customtkinter.CTkEntry(
        caixa,
        width=300,
        placeholder_text="Senha",
        show="*"
    )

    senha.pack(pady=10)

    mensagem = customtkinter.CTkLabel(
        caixa,
        text="",
        font=("Arial", 13)
    )

    mensagem.pack(pady=5)

    botao = customtkinter.CTkButton(
        caixa,
        text="Entrar",
        width=300,
        command=lambda: entrar(
            email.get(),
            senha.get()
        )
    )

    botao.pack(pady=10)

    botao_cadastro = customtkinter.CTkButton(
        caixa,
        text="Criar conta",
        width=300,
        fg_color="transparent",
        text_color="#333333",
        hover_color="#DDDDDD",
        command=tela_cadastro
    )

    botao_cadastro.pack(pady=5)


def entrar(email, senha):
    if not email or not senha:
        mostrar_mensagem(
            "Preencha e-mail e senha.",
            "red"
        )
        return

    sucesso, erro = verificar_usuario(
        email,
        senha
    )

    if sucesso:
        exibir_tela_principal()

    else:
        mostrar_mensagem(
            erro,
            "red"
        )


def tela_cadastro():
    global mensagem

    limpar_janela()
    criar_cabecalho()

    caixa = customtkinter.CTkFrame(
        janela,
        width=400,
        height=430,
        corner_radius=15,
        fg_color="white"
    )

    caixa.place(
        relx=0.5,
        rely=0.52,
        anchor="center"
    )

    titulo = customtkinter.CTkLabel(
        caixa,
        text="Criar Conta",
        text_color="black",
        font=("Arial", 26, "bold")
    )

    titulo.pack(pady=(30, 20))

    nome = customtkinter.CTkEntry(
        caixa,
        width=300,
        placeholder_text="Nome"
    )

    nome.pack(pady=8)

    email = customtkinter.CTkEntry(
        caixa,
        width=300,
        placeholder_text="E-mail"
    )

    email.pack(pady=8)

    senha = customtkinter.CTkEntry(
        caixa,
        width=300,
        placeholder_text="Senha",
        show="*"
    )

    senha.pack(pady=8)

    confirmar = customtkinter.CTkEntry(
        caixa,
        width=300,
        placeholder_text="Confirmar senha",
        show="*"
    )

    confirmar.pack(pady=8)

    mensagem = customtkinter.CTkLabel(
        caixa,
        text="",
        font=("Arial", 13)
    )

    mensagem.pack(pady=5)

    botao = customtkinter.CTkButton(
        caixa,
        text="Cadastrar",
        width=300,
        command=lambda: cadastrar(
            nome.get(),
            email.get(),
            senha.get(),
            confirmar.get()
        )
    )

    botao.pack(pady=8)

    voltar = customtkinter.CTkButton(
        caixa,
        text="Voltar",
        width=300,
        fg_color="transparent",
        text_color="#333333",
        hover_color="#DDDDDD",
        command=tela_login
    )

    voltar.pack(pady=5)


def cadastrar(
    nome,
    email,
    senha,
    confirmar
):
    if (
        not nome
        or not email
        or not senha
        or not confirmar
    ):
        mostrar_mensagem(
            "Preencha todos os campos.",
            "red"
        )

        return

    if senha != confirmar:
        mostrar_mensagem(
            "As senhas não coincidem.",
            "red"
        )

        return

    sucesso, erro = cadastrar_usuario(
        nome,
        email,
        senha
    )

    if sucesso:
        mostrar_mensagem(
            "Conta criada com sucesso.",
            "green"
        )

        janela.after(
            1000,
            tela_login
        )

    else:
        mostrar_mensagem(
            erro,
            "red"
        )
















def atualizar_valor(nome, valor):
    valor = float(valor)
    valores[nome] = valor
    etiquetas[nome].configure(text=f"{valor:.2f}")

    if controlador_gamma:
        controlador_gamma.aplicar(valores["R"], valores["G"], valores["B"])


def restaurar_gamma():
    valores["R"] = 1.0
    valores["G"] = 1.0
    valores["B"] = 1.0

    for nome in ["R", "G", "B"]:
        sliders[nome].set(1.0)
        etiquetas[nome].configure(text="1.00")

    if controlador_gamma:
        controlador_gamma.restaurar()


def obter_cor():
    x, y = ctypes.c_long(), ctypes.c_long()

    if platform.system() == "Windows":
        ctypes.windll.user32.GetCursorPos(ctypes.byref(x), ctypes.byref(y))
        return ImageGrab.grab(bbox=(x.value, y.value, x.value + 1, y.value + 1)).getpixel((0, 0))

    return None


def atualizar_conta_gotas():
    global janela_conta_gotas

    if janela_conta_gotas is None or not janela_conta_gotas.winfo_exists():
        janela_conta_gotas = customtkinter.CTkToplevel(janela)
        janela_conta_gotas.title("Conta-gotas")
        janela_conta_gotas.geometry("250x180")
        janela_conta_gotas.attributes("-topmost", True)

        rotulo = customtkinter.CTkLabel(janela_conta_gotas, text="Mova o mouse para uma cor", font=("Arial", 14))
        rotulo.pack(pady=25)

        resultado = customtkinter.CTkLabel(janela_conta_gotas, text="RGB: --", font=("Arial", 14))
        resultado.pack(pady=10)

        def atualizar():
            if not janela_conta_gotas.winfo_exists():
                return

            cor = obter_cor()

            if cor:
                resultado.configure(text=f"RGB: {cor}")

            janela_conta_gotas.after(100, atualizar)

        atualizar()


def fechar_conta_gotas():
    global janela_conta_gotas

    if janela_conta_gotas and janela_conta_gotas.winfo_exists():
        janela_conta_gotas.destroy()

    janela_conta_gotas = None


def exibir_tela_principal():
    global valores, sliders, etiquetas

    limpar_janela()
    criar_cabecalho()

    principal = customtkinter.CTkFrame(janela, fg_color="transparent")
    principal.pack(fill="both", expand=True, padx=35, pady=25)

    titulo = customtkinter.CTkLabel(principal, text="Colorize o Mundo", font=("Arial", 28, "bold"), text_color="black")
    titulo.pack(pady=(5, 0))

    subtitulo = customtkinter.CTkLabel(principal, text="Personalize as cores exibidas na sua tela.", font=("Arial", 15), text_color="#333333")
    subtitulo.pack(pady=(3, 20))

    painel = customtkinter.CTkFrame(principal, width=650, height=260, corner_radius=15, fg_color="white")
    painel.pack(fill="x", padx=80)

    titulo_cores = customtkinter.CTkLabel(painel, text="Ajuste de Cores", font=("Arial", 20, "bold"), text_color="black")
    titulo_cores.pack(pady=(20, 10))

    valores = {"R": 1.0, "G": 1.0, "B": 1.0}
    sliders = {}
    etiquetas = {}

    for nome in ["R", "G", "B"]:
        linha = customtkinter.CTkFrame(painel, fg_color="transparent")
        linha.pack(fill="x", padx=35, pady=5)

        label = customtkinter.CTkLabel(linha, text=nome, width=30, font=("Arial", 15, "bold"), text_color="black")
        label.pack(side="left")

        slider = customtkinter.CTkSlider(linha, from_=0.5, to=1.0, number_of_steps=50, command=lambda valor, n=nome: atualizar_valor(n, valor))
        slider.set(1.0)
        slider.pack(side="left", fill="x", expand=True, padx=15)

        valor = customtkinter.CTkLabel(linha, text="1.00", width=45, font=("Arial", 14), text_color="black")
        valor.pack(side="right")

        sliders[nome] = slider
        etiquetas[nome] = valor

    botao_restaurar = customtkinter.CTkButton(painel, text="Restaurar cores originais", width=220, command=restaurar_gamma)
    botao_restaurar.pack(pady=15)

    conta_gotas = customtkinter.CTkFrame(principal, width=650, height=120, corner_radius=15, fg_color="white")
    conta_gotas.pack(fill="x", padx=80, pady=20)

    titulo_conta_gotas = customtkinter.CTkLabel(conta_gotas, text="Conta-gotas", font=("Arial", 20, "bold"), text_color="black")
    titulo_conta_gotas.pack(pady=(15, 5))

    texto_conta_gotas = customtkinter.CTkLabel(conta_gotas, text="Identifique a cor que está sob o cursor.", font=("Arial", 13), text_color="#333333")
    texto_conta_gotas.pack(pady=3)

    botao_conta_gotas = customtkinter.CTkButton(conta_gotas, text="Ativar conta-gotas", width=200, command=atualizar_conta_gotas)
    botao_conta_gotas.pack(pady=10)


def encerrar_programa():
    fechar_conta_gotas()

    if controlador_gamma:
        controlador_gamma.restaurar()
        controlador_gamma.finalizar()

    janela.destroy()


janela.protocol("WM_DELETE_WINDOW", encerrar_programa)

tela_login()
janela.mainloop()
