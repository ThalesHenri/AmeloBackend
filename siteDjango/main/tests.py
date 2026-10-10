# from django.test import TestCase

# Create your tests here.
import requests
import json
import os
import getpass
import sys
import tempfile

# ==========================================
# Configurações Iniciais
# ==========================================
BASE_URL = os.environ.get(
    'AMELO_API_URL', 'http://192.168.0.217:8080/api/v1/'
).rstrip('/') + '/'
USERNAME = os.environ.get('AMELO_USERNAME')

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
    global USERNAME
    if not USERNAME:
        USERNAME = input('Usuário gestor: ').strip()
    password = os.environ.get('AMELO_PASSWORD') or getpass.getpass('Senha: ')

    print(f"\n🔐 Solicitando token JWT para o usuário '{USERNAME}'...")
    payload_login = {
        'username': USERNAME,
        'password': password
    }
    
    # A rota de token geralmente fica na raiz da API (ajuste se necessário no seu urls.py)
    res = session.post(f"{BASE_URL}auth/token/", json=payload_login, timeout=15)
    
    if res.status_code == 200:
        token = res.json().get('access')
        if not token:
            print('❌ A resposta de autenticação não contém um token de acesso.')
            imprimir_resposta("Erro de Login", res)
            sys.exit(1)
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
    estado['condo_id'] = None
    payload = {
        "nome": "Condomínio CLI Tester",
        "endereco": "Avenida do Terminal, 101",
        "cidade": "João Pessoa",  
        "estado": "PB",           
        "cep": "58000-000"
    }
    res = session.post(f"{BASE_URL}condominios/", json=payload, timeout=15)
    imprimir_resposta("Criar Condomínio", res)
    if res.status_code == 201:
        estado['condo_id'] = res.json().get('id')
        print(f"✅ Condomínio salvo no estado (ID: {estado['condo_id']})")
        return estado['condo_id']
    return None

def criar_profissional():
    print("\n🛠️ Criando Profissional mock...")
    estado['prof_id'] = None
    payload = {
        "nome": "Mario Encanador CLI",
        "telefone": "11988887777",
        "especialidade": "Hidráulica Geral"
    }
    res = session.post(f"{BASE_URL}profissionais/", json=payload, timeout=15)
    imprimir_resposta("Criar Profissional", res)
    if res.status_code == 201:
        estado['prof_id'] = res.json().get('id')
        print(f"✅ Profissional salvo no estado (ID: {estado['prof_id']})")
        return estado['prof_id']
    return None

def criar_supervisor():
    print("\n🛡️ Criando Supervisor e usuário associado...")
    print("O backend cria um novo usuário; informe um username ainda não cadastrado.")
    print("A senha inicial definida pelo backend é 123456. Oriente a troca após o primeiro acesso.")
    username = input("Username do supervisor: ").strip()
    first_name = input("Nome: ").strip()
    last_name = input("Sobrenome: ").strip()
    email = input("E-mail (opcional): ").strip()
    telefone = input("Telefone (opcional): ").strip()
    
    condo = estado['condo_id']
    usar_salvo = input(f"Usar Condomínio ID {condo} salvo na memória? (s/n): ") if condo else 'n'
    if usar_salvo.lower() != 's':
        condo = input("Digite o ID do Condomínio: ")

    payload = {
        "usuario": {
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "telefone": telefone,
        },
        "condominios": [int(condo)] if condo else [],
        "ativo": True,
    }
    res = session.post(f"{BASE_URL}supervisores/", json=payload, timeout=15)
    imprimir_resposta("Criar Supervisor", res)

def criar_demanda():
    print("\n📋 Criando Demanda...")
    estado['demanda_id'] = None
    condo = estado['condo_id']
    prof = estado['prof_id']
    
    if not condo:
        condo = input("⚠️ Nenhum condomínio na memória. Digite o ID do Condomínio: ")

    print("Qual a urgência da demanda?")
    print("1 - Urgente")
    print("2 - Não urgente")
    urgencia_op = input("Escolha (1/2): ").strip()
    if urgencia_op not in {'1', '2'}:
        print("❌ Opção inválida; demanda não criada.")
        return None
    urgencia = "URGENTE" if urgencia_op == "1" else "NAO_URGENTE"
    
    payload = {
        "condominio": int(condo),
        "titulo": f"Teste via Menu ({urgencia})",
        "descricao": "Demanda gerada pelo script de testes CLI.",
        "urgencia": urgencia,
        "profissionalAcionado": int(prof) if prof else None,
        "observacoes": "Teste automatizado do DevWizard."
    }
    # O serviço define status=PENDENTE na criação; omitir esse campo evita duplicar o argumento.
    res = session.post(f"{BASE_URL}demandas/", json=payload, timeout=15)
    imprimir_resposta("Criar Demanda", res)
    if res.status_code in [201, 200]:
        estado['demanda_id'] = res.json().get('id')
        print(f"✅ Demanda salva no estado (ID: {estado['demanda_id']})")
        return estado['demanda_id']
    return None

def enviar_anexo():
    print("\n📎 Enviando Anexo...")
    demanda = estado['demanda_id']
    if not demanda:
        demanda = input("⚠️ Nenhuma demanda na memória. Digite o ID da Demanda: ")

    with tempfile.NamedTemporaryFile(mode='w+b', suffix='.txt') as arquivo_aberto:
        arquivo_aberto.write(b'Arquivo gerado pelo CLI para testar upload multipart.')
        arquivo_aberto.seek(0)
        files = {'arquivo': ('foto_cli.txt', arquivo_aberto, 'text/plain')}
        data = {'demanda': int(demanda)}
        res = session.post(
            f"{BASE_URL}anexos/", data=data, files=files, timeout=30
        )
        imprimir_resposta("Upload de Anexo", res)
        return res.ok

def alterar_status_demanda():
    print("\n🔄 Alterando Status da Demanda...")
    demanda = estado['demanda_id']
    if not demanda:
        demanda = input("⚠️ Nenhuma demanda na memória. Digite o ID da Demanda: ")

    print("Escolha o novo status:")
    print("1 - Em Andamento")
    print("2 - Concluído")
    print("3 - Pendente")
    op = input("Opção: ")
    mapa_status = {"1": "EM_ANDAMENTO", "2": "CONCLUIDA", "3": "PENDENTE"}
    if op not in mapa_status:
        print("❌ Opção inválida; nenhum status foi alterado.")
        return False

    payload = {"status": mapa_status[op]}
    
    # PATCH é o ideal para atualização parcial de status
    res = session.patch(f"{BASE_URL}demandas/{demanda}/", json=payload, timeout=15)
    imprimir_resposta("Alterar Status", res)
    return res.ok

def visualizar_auditoria():
    print("\n👁️ Verificando Logs de Auditoria...")
    demanda = estado['demanda_id']
    if not demanda:
        demanda = input("⚠️ Nenhuma demanda na memória. Digite o ID da Demanda: ")

    res = session.get(f"{BASE_URL}demandas/{demanda}/historico/", timeout=15)
    imprimir_resposta("Histórico de Auditoria Imutável", res)

# ==========================================
# Menu Interativo (CLI)
# ==========================================
def menu_interativo():
    # 🔥 Força o login via JWT antes de carregar o menu principal
    fazer_login_jwt()

    while True:
        print("\n" + "="*50)
        print(" 🧙‍♂️ AMELO API - O GRIMÓRIO DE TESTES CLI")
        print("="*50)
        print(f" 💾 Estado Atual: Condo[{estado['condo_id']}] | Prof[{estado['prof_id']}] | Demanda[{estado['demanda_id']}]")
        print("-" * 50)
        print(" 1. 🏢 Criar Condomínio (Mock)")
        print(" 2. 🛠️  Criar Profissional (Mock)")
        print(" 3. 🛡️  Criar/Vincular Supervisor")
        print(" 4. 📋 Criar Demanda (por urgência)")
        print(" 5. 📎 Enviar Anexo para a Demanda")
        print(" 6. 🔄 Alterar Status da Demanda Salva")
        print(" 7. 👁️  Visualizar Logs de Auditoria da Demanda")
        print(" 8. ⚡ Executar Fluxo Completo (condomínio -> profissional -> demanda -> anexo -> status)")
        print(" 0. 🚪 Sair")
        print("="*50)

        escolha = input("👉 Escolha uma magia: ").strip()

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
            alterar_status_demanda()
        elif escolha == '7':
            visualizar_auditoria()
        elif escolha == '8':
            print("\n🔥 INICIANDO TESTE EM MASSA (O RITUAL COMPLETO)...")
            condo_id = criar_condominio()
            criar_profissional()
            demanda_id = criar_demanda() if condo_id else None

            if not demanda_id:
                print("❌ Fluxo interrompido: não foi possível criar a demanda.")
            else:
                anexo_ok = enviar_anexo()
                status_response = session.patch(
                    f"{BASE_URL}demandas/{demanda_id}/",
                    json={"status": "EM_ANDAMENTO"},
                    timeout=15,
                )
                imprimir_resposta("Alterar Status no Fluxo Completo", status_response)
                if anexo_ok and status_response.ok:
                    print("\n🎉 Fluxo completo finalizado com sucesso!")
                else:
                    print("⚠️ Fluxo executado parcialmente; confira as respostas acima.")
        elif escolha == '0':
            print("\n👋 O Mago encerra a sessão. Que os Deuses da Programação estejam com você!\n")
            sys.exit(0)
        else:
            print("\n❌ Feitiço desconhecido. Tente novamente.")
            
        input("\nPressione [ENTER] para voltar ao grimório...")

if __name__ == '__main__':
    # Testa a conexão com o servidor local antes de abrir o menu e fazer o login
    try:
        requests.get(BASE_URL, timeout=5)
        menu_interativo()
    except requests.exceptions.RequestException as erro:
        print(f"\n❌ ERRO: Não foi possível conectar a {BASE_URL}")
        print(f"Detalhe: {erro}")
        print("Verifique a URL configurada e se o servidor Django está em execução.\n")
