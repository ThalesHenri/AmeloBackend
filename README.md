
# 🏢 AMELO - Gestor de Condomínios (Backend API)

Este é o repositório do backend do sistema **AMELO**, responsável por toda a lógica de negócios, persistência de dados, controlo de acessos e fornecimento de APIs REST para o aplicativo mobile (Android & iOS) desenvolvido em Flutter.

O sistema foi desenhado para gerir com eficiência demandas condominiais através de fluxos de trabalho claros, históricos de auditoria e anexos de média.

---

## 🛠️ Tecnologias Utilizadas

- **Framework Principal:** [Django 5.x](https://www.djangoproject.com/)
- **Módulo de API:** [Django REST Framework (DRF)](https://www.django-rest-framework.org/)
- **Linguagem:** Python 3.11+
- **Banco de Dados:** PostgreSQL (Produção) / SQLite (Desenvolvimento local)
- **Autenticação:** JWT (JSON Web Tokens) via `djangorestframework-simplejwt`
- **Hospedagem Alvo:** HostGator (Plano M via Passenger WSGI)

---

## 🏗️ Arquitetura e Modelagem de Dados

O banco de dados é puramente relacional para garantir a integridade das informações entre as entidades core:

- **Condominio:** Regista os edifícios sob gestão do sistema.
- **Demanda (Ordem de Serviço):** O núcleo do sistema, contendo estados (`PENDENTE`, `EM_ANDAMENTO`, `CONCLUIDA`) e níveis de urgência.
- **Profissional & Responsavel:** Entidades que mapeiam os prestadores de serviço acionados e os contactos locais do condomínio.
- **HistoricoAtualizacao:** Linha do tempo (Timeline) automática que regista auditoria de alterações em cada demanda.
- **Anexo:** Permite múltiplos uploads de ficheiros/fotos atrelados a demandas ou históricos.

---

## 🚀 Como Executar o Projeto Localmente

### Pré-requisitos
- Python 3.11 ou superior instalado.
- Gerenciador de pacotes `pip` e utilitário `virtualenv`.

### 1. Clonar o Repositório e Configurar o Ambiente Venv
```bash
git clone [https://github.com/teu-usuario/amelo-backend.git](https://github.com/teu-usuario/amelo-backend.git)
cd amelo-backend

# Criar e ativar o ambiente virtual
python -m venv venv
source venv/bin/activate  # No Windows use: venv\Scripts\activate
```

### 2. Instalar as Dependências
```Bash


pip install -r requirements.txt
```

### 3. Configurar as Variáveis de Ambiente (`.env`)

Cria um ficheiro `.env` na raiz do projeto com base no seguinte modelo:

Code snippet

```Bash
DEBUG=True
SECRET_KEY=sua_chave_secreta_aqui
ALLOWED_HOSTS=localhost,127.0.0.1
# Caso use Postgres localmente (se não, o Django usará SQLite automaticamente por padrão)
DB_NAME=amelo_db
DB_USER=postgres
DB_PASSWORD=sua_senha
DB_HOST=localhost
DB_PORT=5432
```

### 4. Executar Migrations e Criar Superusuário

Bash

```
python manage.py migrate
python manage.py createsuperuser
```

### 5. Iniciar o Servidor de Desenvolvimento

Bash

```
python manage.py runserver
```

A API estará disponível em `http://127.0.0.1:8000/`. O painel administrativo do Django pode ser acedido em `http://127.0.0.1:8000/admin/`.

## 📡 Endpoints Principais da API (Visão Geral)

Todos os endpoints de dados exigem o cabeçalho `Authorization: Bearer <seu_token>` após a autenticação.

### Autenticação

- `POST /api/v1/token/` - Recebe `username` e `password`, retorna os tokens Access e Refresh.
    
- `POST /api/v1/token/refresh/` - Renova o token de acesso expirado.
    

### Condomínios

- `GET /api/v1/condominios/` - Lista os condomínios vinculados ao gestor autenticado.
    
- `POST /api/v1/condominios/` - Cadastra um novo condomínio.
    

### Demandas / Ordens de Serviço

- `GET /api/v1/demandas/` - Retorna a lista de demandas (suporta filtros por status, urgência e condomínio).
    
- `POST /api/v1/demandas/` - Cria uma nova demanda.
    
- `GET /api/v1/demandas/<id>/` - Detalhes completos de uma demanda específica (retorna objetos aninhados de Condomínio e Profissional).
    
- `PATCH /api/v1/demandas/<id>/` - Atualiza parcialmente uma demanda (ex: mudar status).
    

### Históricos e Anexos

- `GET /api/v1/demandas/<id>/historico/` - Retorna a timeline de atualizações daquela demanda.
    
- `POST /api/v1/anexos/` - Endpoint para upload multipart/form-daya de fotos/documentos.
    

## 📦 Estrutura de Resposta Padrão (Exemplo de JSON)

Ao consultar uma demanda (`GET /api/v1/demandas/1/`), o DRF utiliza _Nested Serializers_ para entregar os dados mastigados para o Flutter, evitando sobrecarga de requisições de rede:

JSON

```
{
  "id": 1,
  "titulo": "Vazamento no shaft do 5º andar",
  "descricao": "Vazamento constante no shaft do banheiro do apto 504...",
  "status": "EM_ANDAMENTO",
  "urgencia": "URGENTE",
  "data_abertura": "2026-05-12T09:30:00Z",
  "previsao_conclusao": "2026-05-15",
  "condominio": {
    "id": 3,
    "nome": "Edifício Maria Carolina",
    "endereco": "Rua das Acácias, 320",
    "imagem": "[https://api.amelo.com/media/condominios/maria_carolina.jpg](https://api.amelo.com/media/condominios/maria_carolina.jpg)"
  },
  "profissional_acionado": {
    "id": 7,
    "nome": "Hidráulico João",
    "especialidade": "Hidráulica",
    "telefone": "(83) 99999-9999"
  }
}
```

## 🚀 Notas de Deploy (HostGator M)

O deploy neste ambiente utiliza a estrutura do Application Manager do cPanel (Passenger WSGI).

1. Certifica-te de que o ficheiro `passenger_wsgi.py` aponta corretamente para o `wsgi.py` do projeto.
    
2. Configura o arquivo `.htaccess` na raiz pública para redirecionar o tráfego para a aplicação.
    
3. Garante que as permissões de escrita na pasta `media/anexos_demandas/` estão configuradas corretamente para permitir os uploads feitos pelo aplicativo móvel.
