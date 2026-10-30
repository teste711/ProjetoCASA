# Backend — Projeto C.A.S.A. (FastAPI + Firebase)

- **Cadastro com e-mail confirmado:** a conta só é criada no Firebase depois que o usuário digita o código de 6 dígitos recebido por e-mail.
- **Login / esqueci a senha:** Firebase Authentication, direto no frontend. O backend só valida o token (`Authorization: Bearer …`).
- **Dados:** Cloud Firestore (perfil, categorias/botões, dispositivos, histórico, notificações). **Mídia dos botões do site:** arquivos em disco (`uploads/`).
- **Fluxo do IoT:** o app envia imagens/áudios à API → ela converte (JPEG 240×240), codifica em **base64**, grava no **Firestore** e acende um **sinal no Realtime Database** → o dispositivo busca, confirma e a API limpa. Não usa o Firebase Storage (que exige plano pago). Veja `Fluxo_IoT.md`.

## Rodar
```powershell
cd backend
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements-dev.txt     # (em produção: só requirements.txt)
copy .env.example .env      # depois edite o .env (SMTP, FIREBASE_DATABASE_URL...)
python -m uvicorn main:app --reload --port 8000     # docs: http://localhost:8000/docs
```
Coloque o `firebase-credentials.json` (chave de serviço) neste aqruivo.

### Testes
```powershell
python -m pytest -q                       # 50 testes (Firebase falso em memória; SMTP contra um servidor SMTP real local)
python -m tests.e2e_servidor_real         # 49 passos com servidor HTTP real: CORS, cadastro, upload, PDF e fluxo do IoT
```

## E-mail do cadastro (SMTP)
Sem `SMTP_HOST` no `.env` o SMTP está **desligado**: nenhum e-mail sai e o código aparece só no terminal. Ao subir, o servidor avisa qual é o estado.
Para ligar (Gmail): verificação em 2 etapas → *Senha de app* → preencha `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` → reinicie.
Confira **sem subir o servidor**: `python -m app.testar_smtp voce@gmail.com` (diz exatamente o que está errado: senha, certificado, porta bloqueada...).
O certificado do servidor SMTP **é verificado** (STARTTLS na 587 ou SSL direto na 465). Se o envio falhar, o cadastro responde **503** (antes, o usuário via "código enviado" e nada saía).

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
| **IoT — app (login)** | `POST /iot/midias` (arquivo + MAC + botão) · `GET /iot/midias?dispositivo=` · `GET/DELETE /iot/midias/{id}?dispositivo=` |
| **IoT — aparelho** | `GET /device/iot/pendentes` · `GET /device/iot/midias/{id}` · `POST …/{id}/concluido` · `POST …/{id}/erro` |

## Firestore
```
cadastros_pendentes/{hash do e-mail}   nome, codigo_hash, tentativas, expira_em   (SEM senha; apagado ao confirmar)
usuarios/{uid}                         nome, email, preferências
usuarios/{uid}/categorias/{id}         nome, slug, ordem, botoes[]
usuarios/{uid}/midias/{id}             metadados do arquivo em disco
usuarios/{uid}/acionamentos/{id}       histórico de uso
usuarios/{uid}/notificacoes/{id}
dispositivos/{MAC}                     owner_uid, token_hash, ajustes, config_versao, bateria…
dispositivos/{MAC}/fila/{id}           IoT: imagem/áudio em base64 aguardando o aparelho (apagado ao concluir)
```
Realtime Database: `dispositivos/{MAC}/sync/{id}` = só o estado (pendente → baixando → concluido | erro).
Regras do Firestore: `allow read, write: if false;` (só o backend acessa, via Admin SDK). Apagar dispositivo ou conta também apaga a fila (base64) e os sinais.


