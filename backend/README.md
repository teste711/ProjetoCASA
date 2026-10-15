# Backend — Projeto C.A.S.A. (FastAPI + Firebase)

**Auth simples:** o *Firebase Authentication* faz cadastro, login, confirmação de e-mail e recuperação de senha **no frontend**.
O backend só recebe o ID token (`Authorization: Bearer …`), valida com o Firebase Admin SDK e guarda os dados no **Cloud Firestore**.

## 1. Configurar o Firebase (uma vez)
1. Console Firebase → crie o projeto → **Authentication → Método de login → E-mail/senha** (ativar).
2. **Firestore Database** → criar banco (modo produção).
3. **Configurações do projeto → Contas de serviço → Gerar nova chave privada** → salve como `backend/firebase-credentials.json` (já está no `.gitignore`).
4. **Configurações do projeto → Seus apps → Web** → copie as chaves para `frontend/.env.local` (veja `frontend/lib/firebase.ts`).

## 2. Rodar
```bash
cd backend
python -m venv venv && source venv/bin/activate     # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload --port 8000                # docs em http://localhost:8000/docs
pytest                                               # testes (não precisam de credenciais)
```
Frontend: `NEXT_PUBLIC_API_URL=http://localhost:8000` + as chaves `NEXT_PUBLIC_FIREBASE_*`.

## Endpoints (todos com Bearer do Firebase, exceto `/device/*` e `/saude`)
| | |
|---|---|
| `GET /me` | perfil (cria no 1º acesso — chame após o login) |
| `PATCH /me` | nome e preferências (notificações, modo escuro, fonte 8–20) |
| `DELETE /me` | exclui conta + dados + usuário do Firebase Auth (LGPD) |
| `GET/POST /categorias`, `PATCH/DELETE /categorias/{id}` | máx. 3 categorias |
| `POST /categorias/{id}/botoes`, `PATCH/DELETE …/botoes/{bid}` | máx. 5 botões; guarda `imagem_url`/`audio_url` |
| `POST/GET /dispositivos`, `PATCH/DELETE /dispositivos/{mac}` | pareia ESP32 (devolve `device_token` uma vez) e ajustes |
| `GET /historico` | mais e menos acionados |
| `GET /device/config` · `POST /device/telemetria` | usados pelo ESP32 com `X-Device-Token` |

## Estrutura do Firestore
```
usuarios/{uid}                     nome, email, preferências
usuarios/{uid}/categorias/{id}     nome, slug, ordem, botoes[]  (botão: id, rotulo, imagem_url, audio_url…)
usuarios/{uid}/acionamentos/{id}   botao_nome, categoria_nome, acionado_em   (id = mac_uidLocal → sem duplicar)
dispositivos/{MAC}                 owner_uid, token_hash (SHA-256), ajustes, config_versao, bateria…
```
Regras do Firestore: bloqueie acesso direto do cliente (`allow read, write: if false;`) — só o backend (Admin SDK) acessa.

## Imagens e áudios
Envie do frontend direto ao **Firebase Storage** (`uploadBytes`) e mande a URL no botão (`imagem_url`, `audio_url`, `audio_nome`).
(A versão com upload no próprio servidor, PDF, Wi-Fi e notificações está em `backend_sqlite_completo/`.)

## Limitação conhecida
Os testes usam Firestore/Auth falsos; **a conexão real não pôde ser testada aqui** (sem credenciais) — valide com seu projeto Firebase.
