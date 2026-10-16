# Backend — Projeto C.A.S.A. (FastAPI + Firebase)

- **Cadastro com e-mail confirmado:** a conta só é criada no Firebase depois que o usuário digita o código de 6 dígitos recebido por e-mail. Deixei SMTP comentado no .env, para facilitar bateria de testes. Ativar depois.


## Rodar
cd backend
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
copy .env.example .env      # já existe um .env pronto neste projeto
python -m uvicorn main:app --reload --port 8000     # docs: http://localhost:8000/docs

### Testes
```powershell
python -m pytest -q                       # 19 testes (Firebase falso em memória)
python -m tests.e2e_servidor_real         # 30 passos com servidor HTTP real + CORS
```

## E-mail do cadastro (importante)
Sem `SMTP_HOST` no `.env` **nenhum e-mail é enviado**: o código aparece só no terminal do uvicorn (bom para testes).
Para enviar de verdade com Gmail: ative a verificação em 2 etapas → crie uma *Senha de app* → preencha `SMTP_*` no `.env` → reinicie.
Se o SMTP estiver errado, o erro aparece **só no terminal** (o usuário vê "código enviado").

## Endpoints
| Grupo | Rotas |
|---|---|
| Cadastro (públicas) | `POST /auth/cadastro` → `POST /auth/confirmar` · `POST /auth/reenviar-codigo` |
| Perfil | `GET/PATCH /me` (nome e preferências) · `GET /me/exportar` · `DELETE /me` |
| Categorias | `GET/POST /categorias` · `PATCH/DELETE /categorias/{id}` · `PUT /categorias/ordem` (máx. 3) |
| Botões | `POST /categorias/{id}/botoes` · `PATCH/DELETE …/botoes/{bid}` · `PUT …/botoes/ordem` (máx. 5) |
| Mídia | `POST /midias` (PNG/JPEG/WEBP → 240×240; MP3/WAV) · `GET /midias/{id}/arquivo` · `DELETE /midias/{id}` |
| Dispositivos | `POST/GET /dispositivos` · `PATCH/DELETE /dispositivos/{mac}` |
| Histórico | `GET /historico?periodo=&busca=` · `DELETE /historico/{id}` · `DELETE /historico` · `POST /historico/acionamentos` |
| Desempenho | `GET /desempenho?periodo=` · `GET /desempenho/relatorio?periodo=` (PDF) |
| Notificações | `GET /notificacoes` · `POST /notificacoes/lidas` · `DELETE /notificacoes` |
| Aparelho (ESP32, `X-Device-Token`) | `GET /device/config` · `GET /device/midias/{id}` · `POST /device/telemetria` |

## Firestore
```
cadastros_pendentes/{hash do e-mail}   nome, codigo_hash, tentativas, expira_em   (SEM senha; apagado ao confirmar)
usuarios/{uid}                         nome, email, preferências
usuarios/{uid}/categorias/{id}         nome, slug, ordem, botoes[]
usuarios/{uid}/midias/{id}             metadados do arquivo em disco
usuarios/{uid}/acionamentos/{id}       histórico de uso
usuarios/{uid}/notificacoes/{id}
dispositivos/{MAC}                     owner_uid, token_hash, ajustes, config_versao, bateria…
```
Regras do Firestore: `allow read, write: if false;` (só o backend acessa, via Admin SDK).

## Limitações
Histórico/desempenho filtram em Python (aceitável). Redes Wi-Fi do aparelho só existem na versão SQLite. Arquivos em disco somem em hospedagens de disco efêmero (Render/Heroku grátis).
