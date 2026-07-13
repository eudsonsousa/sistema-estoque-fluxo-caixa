# 📦 Sistema de Controle de Estoque e Fluxo de Caixa

Sistema completo para gerenciamento de estoque, fluxo de caixa e controle de acesso por níveis de usuários. Desenvolvido com **Python (Flask)** no backend e **React** no frontend, com banco de dados **MySQL**.

## 🎯 Funcionalidades

### ✨ Core
- ✅ **Autenticação JWT** com 4 níveis de acesso (Admin, Gerente, Operacional, Visualizador)
- ✅ **Cadastro de Produtos** com dados tributários (ICMS, IPI, PIS, COFINS)
- ✅ **Duplicação de Produtos** para reaproveitar dados tributários
- ✅ **Controle de Estoque** com entrada, saída, ajuste e devolução
- ✅ **Fluxo de Caixa** com controle de entradas, saídas e pendências
- ✅ **Relatórios** de estoque, fluxo de caixa e movimentações
- ✅ **Dashboard** com resumos visuais
- ✅ **Histórico de Transações** completo

## 🔐 Níveis de Acesso

| Funcionalidade | Admin | Gerente | Operacional | Visualizador |
|---|---|---|---|---|
| Cadastro de usuários | ✅ | ❌ | ❌ | ❌ |
| Cadastro de produtos | ✅ | ✅ | ❌ | ❌ |
| Duplicar produtos | ✅ | ✅ | ❌ | ❌ |
| Entrada/Saída de estoque | ✅ | ✅ | ✅ | ❌ |
| Fluxo de caixa | ✅ | ✅ | ❌ | ❌ |
| Relatórios | ✅ | ✅ | ❌ | ✅ |
| Configurações | ✅ | ❌ | ❌ | ❌ |

## 🛠️ Stack Tecnológico

**Backend:**
- Python 3.8+
- Flask 2.3
- SQLAlchemy (ORM)
- Flask-JWT-Extended (Autenticação)
- Flask-CORS (CORS)
- PyMySQL (Driver MySQL)

**Frontend:**
- React 18
- React Router v6
- Axios (HTTP Client)
- Context API (State Management)
- Recharts (Gráficos)

**Banco de Dados:**
- MySQL 8.0+

## 📁 Estrutura do Projeto

```
sistema-estoque-fluxo-caixa/
├── backend/
│   ├── app/
│   │   ├── models/           # Modelos de dados
│   │   ├── routes/           # Rotas da API
│   │   ├── utils/            # Utilitários e decoradores
│   │   ├── __init__.py
│   │   └── config.py
│   ├── requirements.txt
│   ├── .env.example
│   └── run.py
├── frontend/
│   ├── src/
│   │   ├── components/       # Componentes React
│   │   ├── context/          # Context API
│   │   ├── services/         # Serviços de API
│   │   ├── App.js
│   │   └── index.js
│   ├── public/
│   ├── package.json
│   └── .env.example
├── docker-compose.yml
└── README.md
```

## 🚀 Instalação e Execução

### Opção 1: Com Docker Compose (Recomendado)

#### Pré-requisitos:
- Docker
- Docker Compose

#### Passos:

1. **Clone o repositório:**
```bash
git clone https://github.com/eudsonsousa/sistema-estoque-fluxo-caixa.git
cd sistema-estoque-fluxo-caixa
```

2. **Configure as variáveis de ambiente:**

**Backend** - Copie `.env.example` para `.env`:
```bash
cp backend/.env.example backend/.env
```

Edite `backend/.env` com suas configurações:
```env
DB_HOST=mysql
DB_USER=root
DB_PASSWORD=sua_senha_segura
DB_NAME=sistema_estoque
DB_PORT=3306
FLASK_ENV=production
SECRET_KEY=sua_chave_secreta_muito_segura
JWT_SECRET_KEY=sua_chave_jwt_muito_segura
```

**Frontend** - Copie `.env.example` para `.env`:
```bash
cp frontend/.env.example frontend/.env
```

3. **Inicie os serviços:**
```bash
docker-compose up -d
```

4. **Acesse a aplicação:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000/api

### Opção 2: Instalação Manual

#### Backend:

1. **Crie um ambiente virtual:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

2. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

3. **Configure o arquivo `.env`:**
```bash
cp .env.example .env
# Edite com suas configurações do MySQL
```

4. **Crie o banco de dados (MySQL):**
```sql
CREATE DATABASE sistema_estoque;
USE sistema_estoque;
```

5. **Execute a aplicação:**
```bash
python run.py
```

O backend estará disponível em: `http://localhost:5000`

#### Frontend:

1. **Instale as dependências:**
```bash
cd frontend
npm install
```

2. **Configure o arquivo `.env`:**
```bash
cp .env.example .env
# Edite com a URL da API
REACT_APP_API_URL=http://localhost:5000/api
```

3. **Inicie o servidor de desenvolvimento:**
```bash
npm start
```

O frontend estará disponível em: `http://localhost:3000`

## 👥 Usuários de Teste

Após iniciar a aplicação, você pode registrar novos usuários. Aqui estão exemplos de teste:

**Admin:**
- Email: `admin@sistema.com`
- Senha: `admin123`

**Gerente:**
- Email: `gerente@sistema.com`
- Senha: `gerente123`

**Operacional:**
- Email: `operacional@sistema.com`
- Senha: `operacional123`

**Visualizador:**
- Email: `visualizador@sistema.com`
- Senha: `visualizador123`

## 📝 Endpoints da API

### Autenticação
- `POST /api/auth/register` - Registrar novo usuário
- `POST /api/auth/login` - Fazer login
- `GET /api/auth/me` - Obter dados do usuário autenticado

### Produtos
- `GET /api/products` - Listar produtos
- `GET /api/products/{id}` - Obter detalhes de um produto
- `POST /api/products` - Criar novo produto (Admin, Gerente)
- `PUT /api/products/{id}` - Atualizar produto (Admin, Gerente)
- `POST /api/products/{id}/duplicate` - Duplicar produto (Admin, Gerente)
- `DELETE /api/products/{id}` - Deletar produto (Admin)

### Estoque
- `GET /api/inventory` - Listar inventário
- `GET /api/inventory/{id}` - Obter detalhes de inventário
- `GET /api/inventory/movements` - Listar movimentações
- `POST /api/inventory/movements` - Registrar movimento (Admin, Gerente, Operacional)

### Fluxo de Caixa
- `GET /api/cashflow` - Listar movimentações
- `GET /api/cashflow/summary` - Resumo de fluxo de caixa
- `POST /api/cashflow` - Criar movimentação (Admin, Gerente)
- `PUT /api/cashflow/{id}` - Atualizar movimentação (Admin, Gerente)

### Relatórios
- `GET /api/reports/inventory-summary` - Relatório de estoque
- `GET /api/reports/cashflow-summary` - Relatório de fluxo de caixa
- `GET /api/reports/movements` - Relatório de movimentações

## 🔄 Fluxos Principais

### 1. Cadastro de Produto
1. Admin/Gerente acessa `/products`
2. Clica em "+ Novo Produto"
3. Preenche os dados incluindo informações tributárias
4. Sistema cria o produto e exibe na lista

### 2. Duplicar Produto
1. Admin/Gerente clica no ícone de cópia 📋 na linha do produto
2. Sistema pré-carrega os dados do produto original
3. Usuário altera o SKU e nome (dados tributários são preservados)
4. Sistema cria novo produto com dados replicados

### 3. Movimentação de Estoque
1. Operacional acessa a seção de Estoque
2. Seleciona o tipo de movimentação (entrada, saída, ajuste, devolução)
3. Sistema atualiza a quantidade e registra o histórico
4. Gera alerta se estoque cair abaixo da quantidade mínima

### 4. Fluxo de Caixa
1. Gerente registra entradas e saídas
2. Define datas de vencimento e pagamento
3. Sistema calcula saldo, entradas, saídas e pendências
4. Visualizador pode ver relatórios em dashboard

## 🐛 Troubleshooting

### Erro de conexão com MySQL
```
Error: (2003, "Can't connect to MySQL server")
```
- Verifique se MySQL está rodando
- Confirme credenciais em `.env`
- Verifique se o banco de dados foi criado

### Erro de CORS
```
Access to XMLHttpRequest blocked by CORS policy
```
- Verifique se o backend está rodando
- Confirme a URL do `REACT_APP_API_URL` em `frontend/.env`
- Reinicie o frontend após alterações em `.env`

### Token JWT expirado
```
401 Unauthorized
```
- Faça login novamente
- Verifique a validade do token em `localStorage`

## 📚 Documentação Adicional

### Modelos de Dados
Veja em `backend/app/models/` para detalhes completos sobre a estrutura de dados.

### Decoradores de Permissão
O sistema usa decoradores para controlar acesso:
```python
@role_required(['admin', 'gerente'])
def create_product():
    ...
```

### Context API (Frontend)
Acesso ao contexto de autenticação:
```javascript
const { user, login, logout, hasPermission } = useAuth();
```

## 🤝 Contribuindo

1. Faça um Fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## 📧 Suporte

Para dúvidas ou sugestões, abra uma issue no repositório.

---

**Desenvolvido com ❤️ para facilitar o gerenciamento de estoque**
