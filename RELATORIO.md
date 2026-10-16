# Relatório de finalização — Projeto C.A.S.A.

## 1. Resultado

O sistema ficou **completo e integrado**: o frontend (Next.js) fala com o backend (FastAPI), que usa Firebase Auth e Firestore.
O cadastro agora **só cria a conta depois que o e-mail é confirmado com um código**.

### O que foi testado (e como)

| Verificação | Resultado |
|---|---|
| Testes automáticos do backend (`python -m pytest`) | **19 passaram** |
| Teste de ponta a ponta com servidor HTTP real (`python -m tests.e2e_servidor_real`) | **30 passos OK** (CORS, cadastro em 2 etapas, upload, aparelho, PDF, exclusão de conta) |
| Conferência automática: toda chamada do frontend tem rota no backend | **26 de 26** |
| TypeScript (`tsc`) | **0 erros** |
| ESLint | **0 problemas** |
| Build de produção do Next (`next build`) | **OK**, 10 rotas geradas |

### O que NÃO foi testado (leia com atenção)

1. **Firebase real.** Meu ambiente não alcança o Google nem tem suas credenciais. Os testes usam um Firebase *falso em memória* escrito por mim. As chamadas reais (`verify_id_token`, `create_user`, `get_user_by_email`, consultas e `recursive_delete` do Firestore) seguem a documentação, mas **só o seu teste real prova que funcionam**. Veja o roteiro na seção 6.
2. **Envio real de e-mail (SMTP).** Testei o fluxo com a caixa de saída simulada.
3. **A tela no navegador.** Não há navegador no meu ambiente: validei tipos, lint, build e as chamadas HTTP, mas **não vi as telas renderizadas**. Clique em tudo e me diga o que estiver estranho.
4. Para rodar o build aqui precisei desligar as fontes do Google temporariamente (meu ambiente não as baixa). Seu `layout.tsx` está **intacto**.

---

## 2. Como rodar

**Backend** (terminal 1, pasta `backend`):
```powershell
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```
Coloque o `firebase-credentials.json` em `backend/` (**eu não o incluí no zip**; use o seu). O `.env` já está pronto.

**Frontend** (terminal 2, pasta `frontend`):
```powershell
npm install
npm run dev
```
Abra **http://localhost:3000**.

Sem `SMTP_HOST` no `.env`, o código de cadastro **aparece no terminal do backend** (não é enviado por e-mail). Para enviar de verdade, veja a seção 5.

---

## 3. Mudanças

### Backend
| Arquivo | O que mudou |
|---|---|
| `app/routers/auth.py` (novo) | Cadastro em 2 etapas: `/auth/cadastro` envia o código; `/auth/confirmar` confere e **só então** cria o usuário no Firebase (já com e-mail verificado). Reenvio com espera de 60 s, 5 tentativas, código expira em 15 min, guardado só como hash. **A senha não é gravada** entre as etapas (é reenviada na confirmação). |
| `app/emailer.py` (novo) | Envio por SMTP; sem SMTP, o código vai para o terminal. |
| `app/routers/midias.py`, `app/storage.py` (novos) | Upload de imagem (vira JPEG 240×240 para as telas do ESP32) e áudio MP3/WAV, validados **pelo conteúdo** (não pelo nome). |
| `app/routers/historico.py`, `app/metricas.py`, `app/relatorio.py` (novos) | Histórico com filtros (período e busca), gráfico de desempenho e relatório em **PDF**. |
| `app/routers/notificacoes.py` (novo) | Sino: aparelho pareado e bateria baixa (avisa só ao cruzar 20%). |
| `app/routers/categorias.py` | Botões com `imagem_id`/`audio_id`; reordenar; ao excluir botão/categoria, os arquivos órfãos são apagados do disco. |
| `app/routers/dispositivos.py` | Campos `online`, `codigo` (ex.: ESP32-C10C), `ssid`, `sinal_wifi`; aparelho baixa a lista de arquivos e as mídias. |
| `app/routers/perfil.py` | Exportar dados (LGPD) e excluir conta também apaga os arquivos do disco. |
| `app/schemas.py`, `config.py`, `firebase.py`, `deps.py`, `security.py`, `util.py` | Novos modelos, configurações, limite de requisições, hash HMAC dos códigos, funções do Firebase (`create_user`, `email_existe`). |
| `tests/` | 19 testes + `e2e_servidor_real.py`. |
| `.env.example` / `.env` | Chaves novas (`SECRET_KEY`, SMTP). **Seu `.env` recebeu uma `SECRET_KEY` aleatória; gere a sua** (comando no arquivo). |

### Frontend
| Arquivo | O que mudou |
|---|---|
| `app/cadastro` | Reescrito em **2 etapas** (dados → código de 6 dígitos). Entra direto depois de confirmar. |
| `app/login` | Imports e validação corrigidos; mensagens de erro claras (senha, muitas tentativas, servidor fora do ar). |
| `app/esqueci-senha` | Mantido (Firebase), com limpeza de código morto e tipos. |
| `app/(app)/layout.tsx` | Guarda das telas logadas + carrega o perfil (`/me`). |
| `components/Sidebar.tsx`, `BarraTopo.tsx` (novos) | A sidebar e o sino estavam **copiados em 5 telas**; agora são um componente só. O nome do usuário vem do perfil (antes era "Zeus Alves" fixo). Sino com notificações reais. |
| `app/(app)/dashboard` | Dispositivos reais, status online, bateria/IP/firmware, último acionamento e dica do botão menos usado. **Parear aparelho** (MAC → mostra o token uma única vez). |
| `app/(app)/categoria` | CRUD real. **Novo:** cadastrar botão com imagem e áudio, ouvir o áudio, excluir botão. |
| `app/(app)/historico` | Dados reais; o filtro virou **período** (hoje / 7 dias / 30 dias / tudo); busca; excluir. |
| `app/(app)/desempenho` | Gráfico real por período; botão **Gerar PDF** baixa o relatório. |
| `app/(app)/configuracoes` | Preferências salvas no servidor; excluir conta de verdade. |
| `lib/` | `UsuarioContext`, `erro.ts` (erros tipados), `api.ts`, `auth.ts`, `tempo.ts`; componente `AplicarPreferencias`. |
| Removidos | Os botões "Simular com/sem dados" e as variáveis de simulação (`temDados`, `temNotificacoes` etc.). |

---

## 4. Erros encontrados e corrigidos

### No código que você enviou (trechos colados das minhas instruções)
- **Login:** faltavam os imports de `auth` e `api` (não compilava), a validação de campos vazios tinha sido substituída por um comentário e sobrou um bloco comentado.
- **Cadastro:** a declaração do `feedback` foi apagada e havia **duas funções `handleSubmit`** com o mesmo nome (não compilava). Além disso, o fluxo criava a conta *antes* de validar o e-mail, o oposto do seu objetivo.
- **Sair:** só 1 das 5 telas tinha o botão "Desconectar" ligado.
- **Backend:** o zip tinha a versão 1 (sem histórico, desempenho, notificações).

### No que eu tinha entregue antes
- Eu mandei chamar `/me` dentro do cadastro, o que daria erro 403 com a verificação ligada. Substituído pelo fluxo novo.
- Renomear uma categoria **apagava a cor** (corrigido, com teste).
- Arquivos de botões excluídos ficavam **órfãos no disco** (corrigido, com teste).
- O **nome digitado no cadastro não chegava ao perfil** (o sistema usaria o começo do e-mail e a sidebar mostraria o nome errado). Percebi ao conferir as afirmações deste relatório contra o código; corrigido e coberto por teste.
- A tela de configurações chamava uma rota que não existe (`PUT /me/preferencias`). **Achado pelo teste de ponta a ponta**; corrigido para `PATCH /me`. Depois disso criei a conferência automática das 26 chamadas.

### Só do meu ambiente (não afetam você)
Instalação do npm interrompida, Google Fonts bloqueado no build e uma corrida no teste do e-mail (o envio é em segundo plano).

---

## 5. Pontos de atenção

**Segurança**
1. **Credenciais:** o `.gitignore` está correto e o git **não tem** credenciais no histórico (conferi). Como você já avisou, gere uma nova chave e um novo banco quando for publicar.
2. **Exclusão de conta não pede senha** (o token basta). Em produção, peça a senha de novo.
3. `/device/*` não tem limite de requisições, e o token do aparelho viaja sem HTTPS no ambiente local.
4. O limite de requisições é **em memória** (reinicia com o servidor; com vários servidores, use Redis ou o proxy).
5. Durante o cadastro, alguém pode digitar o e-mail de outra pessoa e disparar um código para ela. Há limite (60 s por e-mail, 10 por minuto por IP), mas não zera o risco.

**Funcionamento**
6. **E-mail:** sem SMTP, **nenhum e-mail sai**. E se o SMTP estiver errado, a falha aparece só no terminal; o usuário vê "código enviado". Gmail exige "Senha de app" (limite ~500 e-mails/dia).
7. **Contas antigas** criadas à mão no console (ex.: `teste1@gmail.com`, sem e-mail verificado) ficam **bloqueadas** com `REQUIRE_EMAIL_VERIFIED=true`. Apague-as no console e recadastre.
8. **Abra o site por `http://localhost:3000`** (ou `127.0.0.1:3000`; ambos estão liberados no CORS). Outro endereço dá erro de CORS.
9. **Arquivos de mídia ficam em disco** (`backend/uploads`). Em hospedagens gratuitas o disco é apagado; não serve como armazenamento definitivo.
10. **Modo escuro** só afeta a tela de Configurações (como no seu design original). O **tamanho da fonte** vale para toda a área logada.
11. O pareamento exige digitar o **MAC** e copiar o token à mão para o ESP32; não há firmware nem Bluetooth.
12. Redes Wi-Fi do aparelho **não existem** nesta versão (só no `backend_sqlite_completo`).
13. Histórico e desempenho são calculados em Python lendo todos os registros (ok para o TCC; para muito volume, use consultas do Firestore).
14. O dashboard atualiza sozinho a cada 30 s; o sino também.
15. **Python 3.14:** se o `pip install` falhar no Pillow, use o Python 3.12 ou 3.13.
16. Existe um `package-lock.json` vazio na **raiz** do projeto (sobra do `npm install` rodado na pasta errada). Pode apagar.

---

## 6. Roteiro para o seu teste real (e comparação)

1. Suba backend e frontend. Em `/docs` do backend, confirme `GET /saude`.
2. **Cadastro:** `/cadastro` → preencha → *Continuar*. Pegue o código **no terminal do backend** (ou no e-mail, se configurou o SMTP).
   - Confira no console do Firebase (**Authentication**) que o usuário **ainda não existe**.
   - Digite um código errado: deve recusar. Digite o certo: a conta aparece no Firebase e você entra no dashboard.
3. **Perfil:** no Firestore deve existir `usuarios/{uid}` e o nome digitado no cadastro.
4. **Categorias:** crie uma categoria, abra, **adicione um botão com áudio e imagem**, toque no áudio.
5. **Dispositivo:** no dashboard, "Conectar" → informe um MAC (ex.: `24:62:AB:E4:C1:0C`) → anote o token.
6. **Simular o ESP32** em `http://localhost:8000/docs` (rota `POST /device/telemetria`, cabeçalho `X-Device-Token`): envie `{"bateria_pct": 15, "acionamentos":[{"botao_id":"<id do botão>","uid_local":"a1"}]}`. O `botao_id` vem de `GET /categorias`.
7. Volte ao site: **Histórico**, **Desempenho** (gráfico e PDF), o **sino** (bateria baixa) e o status **online**.
8. **Esqueci a senha**, **Sair** e tentar abrir `/dashboard` deslogado (deve voltar ao login), e por fim **Excluir conta** (confira que o Firestore ficou sem dados).

**Para comparar com o que você tinha:** o pacote inclui o `.git`; use `git status` e `git diff` para ver cada alteração.

---

## 7. Próximos passos sugeridos

- Pedir a senha para excluir a conta; HTTPS e hospedagem do backend.
- Firmware do ESP32 (pareamento por Bluetooth, uso de `/device/config` e `/device/telemetria`).
- Portar as redes Wi-Fi do aparelho do `backend_sqlite_completo`.
- Aplicar o modo escuro em todas as telas.
