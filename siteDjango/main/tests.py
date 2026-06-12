#from django.test import TestCase

# Create your tests here.
import requests
import json
import os
import sys

# ==========================================
# Configurações Iniciais
# ==========================================
BASE_URL = 'http://127.0.0.1:8080/api/v1/'
USERNAME = 'thales1337' # ⚠️ Coloque um usuário GESTOR válido
PASSWORD = 'user123'

# Iniciamos a sessão vazia (sem auth básico)
session = requests.Session()

# Dicionário para guardar os IDs criados durante a execução do menu
estado = {
    'condo_id': None,
    'prof_id': None,
    'demanda_id': None
}

def imprimir_resposta(passo, response):
    """Imprime os resultados de forma limpa no terminal."""
    print(f"\n--- {passo} ---")
    print(f"Status Code: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except ValueError:
        print(response.text)
    print("-" * 40)

# ==========================================
# Autenticação JWT
# ==========================================
def fazer_login_jwt():
    """Bate no endpoint do SimpleJWT para pegar o token de acesso."""
    print(f"\n🔐 Solicitando token JWT para o usuário '{USERNAME}'...")
    payload_login = {
        'username': USERNAME,
        'password': PASSWORD
    }
    
    # A rota de token geralmente fica na raiz da API (ajuste se necessário no seu urls.py)
    res = session.post(f"{BASE_URL}token/", json=payload_login)
    
    if res.status_code == 200:
        token = res.json().get('access')
        # Injeta o token em TODAS as próximas requisições da sessão
        session.headers.update({'Authorization': f'Bearer {token}'})
        print("✅ Login realizado com sucesso! Token capturado e injetado.")
    else:
        print("❌ Falha na autenticação. Verifique se o usuário/senha estão corretos e se a rota /token/ existe.")
        imprimir_resposta("Erro de Login", res)
        sys.exit(1)

# ==========================================
# Funções de Teste (Endpoints)
# ==========================================
def criar_condominio():
    print("\n🏢 Criando Condomínio mock...")
    payload = {
        "nome": "Condomínio CLI Tester",
        "cnpj": "99.888.777/0001-66",
        "endereco": "Avenida do Terminal, 101",
        "cidade": "João Pessoa",  
        "estado": "PB",           
        "cep": "58000-000"
        
    }
    res = session.post(f"{BASE_URL}condominios/", json=payload)
    imprimir_resposta("Criar Condomínio", res)
    if res.status_code == 201:
        estado['condo_id'] = res.json().get('id')
        print(f"✅ Condomínio salvo no estado (ID: {estado['condo_id']})")

def criar_profissional():
    print("\n🛠️ Criando Profissional mock...")
    payload = {
        "nome": "Mario Encanador CLI",
        "telefone": "11988887777",
        "especialidade": "Hidráulica Geral"
    }
    res = session.post(f"{BASE_URL}profissionais/", json=payload)
    imprimir_resposta("Criar Profissional", res)
    if res.status_code == 201:
        estado['prof_id'] = res.json().get('id')
        print(f"✅ Profissional salvo no estado (ID: {estado['prof_id']})")

def criar_supervisor():
    print("\n🛡️ Atrelando Supervisor (Requer ID de Usuário e Condomínio)...")
    usuario_id = input("Digite o ID do Usuário (Base) para ser Supervisor: ")
    
    condo = estado['condo_id']
    usar_salvo = input(f"Usar Condomínio ID {condo} salvo na memória? (s/n): ") if condo else 'n'
    if usar_salvo.lower() != 's':
        condo = input("Digite o ID do Condomínio: ")

    payload = {
        "usuario": int(usuario_id),
        "condominios": [int(condo)]
    }
    res = session.post(f"{BASE_URL}supervisores/", json=payload)
    imprimir_resposta("Criar Supervisor", res)

def criar_demanda():
    print("\n📋 Criando Demanda...")
    condo = estado['condo_id']
    prof = estado['prof_id']
    
    if not condo:
        condo = input("⚠️ Nenhum condomínio na memória. Digite o ID do Condomínio: ")
    
    payload = {
        "condominio": int(condo),
        "titulo": "Teste via Menu Interativo",
        "descricao": "Demanda gerada pelo script de testes CLI.",
        "prioridade": "MEDIA",
        "status": "PENDENTE",
        "profissional_acionado": prof, # Pode ser None
        "observacoes": "Teste automatizado."
    }
    res = session.post(f"{BASE_URL}demandas/", json=payload)
    imprimir_resposta("Criar Demanda", res)
    if res.status_code == 201:
        estado['demanda_id'] = res.json().get('id')
        print(f"✅ Demanda salva no estado (ID: {estado['demanda_id']})")

def enviar_anexo():
    print("\n📎 Enviando Anexo...")
    demanda = estado['demanda_id']
    if not demanda:
        demanda = input("⚠️ Nenhuma demanda na memória. Digite o ID da Demanda: ")

    nome_arquivo = 'foto_cli.txt'
    with open(nome_arquivo, 'w') as f:
        f.write('Arquivo gerado pelo CLI para testar upload multipart.')

    try:
        with open(nome_arquivo, 'rb') as arquivo_aberto:
            files = {'arquivo': arquivo_aberto}
            data = {'demanda': int(demanda)}
            res = session.post(f"{BASE_URL}anexos/", data=data, files=files)
            imprimir_resposta("Upload de Anexo", res)
    finally:
        os.remove(nome_arquivo)

# ==========================================
# Menu Interativo (CLI)
# ==========================================
def menu_interativo():
    # 🔥 Força o login via JWT antes de carregar o menu principal
    fazer_login_jwt()

    while True:
        print("\n" + "="*45)
        print(" 🚀 AMELO API - PAINEL DE TESTES CLI")
        print("="*45)
        print(f" 💾 Estado Atual: Condo[{estado['condo_id']}] | Prof[{estado['prof_id']}] | Demanda[{estado['demanda_id']}]")
        print("-" * 45)
        print(" 1. 🏢 Criar Condomínio (Mock)")
        print(" 2. 🛠️  Criar Profissional (Mock)")
        print(" 3. 🛡️  Criar/Vincular Supervisor")
        print(" 4. 📋 Criar Demanda (Usa Estado Atual)")
        print(" 5. 📎 Enviar Anexo para a Demanda")
        print(" 6. ⚡ Executar Fluxo Completo (1 -> 2 -> 4 -> 5)")
        print(" 0. 🚪 Sair")
        print("="*45)

        escolha = input("👉 Escolha uma opção: ").strip()

        if escolha == '1':
            criar_condominio()
        elif escolha == '2':
            criar_profissional()
        elif escolha == '3':
            criar_supervisor()
        elif escolha == '4':
            criar_demanda()
        elif escolha == '5':
            enviar_anexo()
        elif escolha == '6':
            print("\n🔥 INICIANDO TESTE EM MASSA...")
            criar_condominio()
            criar_profissional()
            criar_demanda()
            enviar_anexo()
            print("\n🎉 Fluxo completo finalizado com sucesso!")
        elif escolha == '0':
            print("\n👋 Encerrando painel de testes. Até logo!\n")
            sys.exit(0)
        else:
            print("\n❌ Opção inválida. Tente novamente.")
            
        input("\nPressione [ENTER] para voltar ao menu...")

if __name__ == '__main__':
    # Testa a conexão com o servidor local antes de abrir o menu e fazer o login
    try:
        requests.get(BASE_URL)
        menu_interativo()
    except requests.exceptions.ConnectionError:
        print(f"\n❌ ERRO: Não foi possível conectar a {BASE_URL}")
        print("Verifique se o seu servidor Django está rodando (python manage.py runserver).\n")