# EAGV Backend

Backend base do projeto EAGV usando FastAPI, PostgreSQL e autenticação JWT.

## Stack

- FastAPI para API HTTP.
- PostgreSQL como banco principal.
- SQLAlchemy 2.0 para ORM.
- Alembic para versionamento de schema.
- JWT para autenticação stateless.
- Argon2 para hash de senha.

## Estrutura

```text
app/
	api/
	core/
	models/
	schemas/
	services/
alembic/
tests/
```

## Configuração

1. Crie o arquivo `.env` com base em `.env.example`.
2. Suba o PostgreSQL:

```bash
docker compose up -d
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Aplique a migração inicial:

```bash
alembic upgrade head
```

5. Rode a API:

```bash
uvicorn app.main:app --reload
```

## Endpoints

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/forgot-password`
- `POST /api/v1/auth/reset-password`
- `GET /api/v1/auth/me`
- `GET /api/v1/system/settings`
- `GET /api/v1/system/settings/{slug}`
- `GET /health`

## Payloads principais

### Registro

```json
{
	"email": "admin@eagv.com",
	"full_name": "Administrador EAGV",
	"role": "admin",
	"sector": "academia",
	"password": "SenhaForte123"
}
```

Setores aceitos para usuario: `academia`, `bar`, `quadra_areia`, `piscina`, `suplemento`, `roupas`, `lanchonete`, `admin`, `recepcao`, `manutencao`, `geral`.

### Login

```json
{
	"email": "admin@eagv.com",
	"password": "SenhaForte123"
}
```

### Recuperar senha

```json
{
	"email": "admin@eagv.com"
}
```

### Redefinir senha

```json
{
	"token": "token-gerado-pelo-backend",
	"new_password": "NovaSenha123"
}
```

Em ambiente local, o endpoint de recuperacao retorna o `reset_token` no corpo para acelerar a integracao do frontend. Em producao, esse token deve ser entregue por e-mail.

## Desenvolvimento local

O backend libera CORS por padrao para `http://localhost:5173` e `http://127.0.0.1:5173`, cobrindo os dois hosts comuns do Vite em ambiente local.

## Settings publicas do sistema

O endpoint `GET /api/v1/system/settings` e publico e foi desenhado para ser a primeira chamada do frontend no bootstrap da aplicacao. Agora ele retorna a lista de perfis publicos disponiveis no banco, como academia e bar. Para buscar uma configuracao especifica, use `GET /api/v1/system/settings/{slug}`.

## Próximos passos recomendados

- Adicionar refresh token com rotação.
- Integrar controle de perfil e permissões.
- Configurar CI para testes e lint.
- Externalizar observabilidade e auditoria de login.