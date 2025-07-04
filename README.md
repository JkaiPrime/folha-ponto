# 🕒 Sistema de Controle de Ponto

Este projeto é um sistema completo de controle de ponto desenvolvido com **FastAPI** no backend e **Vue.js + Quasar** no frontend. Ele permite o registro, visualização, edição, exclusão e exportação de pontos por colaboradores, além de uma interface administrativa para o RH.

## 🔧 Tecnologias Utilizadas

- **Backend:** FastAPI + SQLAlchemy + SQLite
- **Frontend RH:** Vue.js + Quasar Framework
- **Autenticação:** JWT com proteção contra brute-force (bloqueio após tentativas falhas)

---

## 🚀 Backend (FastAPI)

O backend é responsável por toda a lógica de autenticação, registro e gerenciamento dos pontos e usuários. Está localizado em `src/` e é executado via Uvicorn.

### Principais Endpoints

| Método | Rota                     | Descrição |
|--------|--------------------------|-----------|
| POST   | `/auth/login`            | Login de usuário RH |
| POST   | `/auth/signup`           | Cadastro de novo usuário RH |
| GET    | `/auth/usuarios`         | Lista todos os usuários RH |
| POST   | `/auth/usuarios/{id}/desbloquear` | Desbloqueia um usuário bloqueado |
| DELETE | `/auth/usuarios/{id}`    | Exclui um usuário RH |
| GET    | `/colaboradores`         | Lista colaboradores |
| POST   | `/colaboradores`         | Cria um novo colaborador |
| DELETE | `/colaboradores/{id}`    | Remove um colaborador |
| POST   | `/pontos/bater-ponto`    | Registro de ponto (sem autenticação) |
| GET    | `/pontos`                | Lista todos os registros (autenticado) |
| GET    | `/pontos/hoje`           | Lista todos os pontos registrados hoje |
| GET    | `/pontos/{colaborador_id}` | Pontos por colaborador |
| PUT    | `/pontos/{id}`           | Atualiza um ponto |
| DELETE | `/pontos/{id}`           | Remove um ponto |
| GET    | `/pontos/por-data`       | Lista pontos por colaborador entre duas datas |

---

## 👩‍💼 Frontend RH (Vue + Quasar)

O painel administrativo permite ao RH:

- Fazer login com autenticação protegida
- Criar, visualizar, editar e excluir pontos de colaboradores
- Exportar pontos para Excel
- Criar e gerenciar acessos de usuários do RH
- Desbloquear contas bloqueadas
- Ver apenas os registros do dia na tela de Dashboard

### Telas do RH

- **Login RH**
- **Dashboard**: pontos do dia
- **Visualizar Pontos**: com filtro por mês e exportação para Excel
- **Editar Pontos**: alterar horários registrados
- **Excluir Pontos**: apagar registros por colaborador e por mês
- **Criar Colaborador**
- **Gerenciar Colaboradores**
- **Gerenciar Acesso RH**: lista, exclusão e desbloqueio de usuários

---

## 📲 Tela de Bater Ponto (Pública)

A tela inicial é pública e acessada por colaboradores. Nela, o colaborador insere seu código (6 dígitos) e realiza o registro sequencial:

1. Entrada
2. Saída para almoço
3. Volta do almoço
4. Saída

A cada batida de ponto, o sistema grava o horário atual.

---

## 🔐 Segurança

- Autenticação via JWT
- Bloqueio de conta após 3 tentativas falhas
- Endpoints protegidos com verificação de token
- CORS configurado
- Validação de entrada com Pydantic

### 🔒 Futuras implementações de segurança

- ✅ Refresh Token — Para sessões mais seguras
- ✅ Rate Limiting — Especialmente em produção
- ✅ Logs de login e falhas — Para auditoria e rastreamento

---

## 🛠️ Executando o Projeto

```bash
# Clone o repositório
git clone https://github.com/JkaiPrime/folha-ponto.git

# Backend
cd back
pip install -r requirements.txt
uvicorn src.main:app --reload

# Frontend
cd folha-ponto-rh
pnpm install
quasar dev
```

---

## ✅ Funcionalidades

- [x] Registro de ponto
- [x] Autenticação com bloqueio
- [x] Visualização e edição de registros
- [x] Exportação para Excel
- [x] Desbloqueio de contas

---

## 👤 Autor

- **Lucas Guimaraes Moreira** - [@JkaiPrime](https://github.com/JkaiPrime)

---

## 🤝 Contribuições

Contribuições são bem-vindas!  

1. Fork este repositório
2. Crie sua branch: `git checkout -b minha-feature`
3. Commit suas alterações: `git commit -m 'feat: minha nova feature'`
4. Push para a branch: `git push origin minha-feature`
5. Abra um Pull Request

---

## 🐛 Relatar Problemas

Se encontrar bugs ou tiver sugestões de melhorias, por favor abra uma issue:
[https://github.com/JkaiPrime/folha-ponto/issues](https://github.com/JkaiPrime/folha-ponto/issues)

---

## 📃 Licença

Este projeto está licenciado sob os termos da [Licença MIT](./LICENSE).
