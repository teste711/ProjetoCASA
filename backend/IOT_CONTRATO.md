# Contrato do fluxo do IoT (para quem faz o firmware do ESP32)

Fluxo: **app → API → Firestore (base64) → sinal no Realtime Database → dispositivo → "concluído" → limpeza.**

O aparelho **não precisa de credenciais do Firebase**: ele usa só o *token do dispositivo* (mostrado **uma vez** no pareamento) no
cabeçalho `X-Device-Token`, sempre por HTTPS. O Realtime Database serve apenas como "campainha" (opcional).

## 1. O que o aparelho faz (resumo)
1. A cada N minutos (sugestão: 5) ou quando o sinal aparecer: `GET /device/iot/pendentes`.
2. Para cada item: `GET /device/iot/midias/{id}` → `{ base64, sha256, tipo, mime, largura, altura, botao_id, rotulo, categoria_ordem, botao_ordem }`.
3. Decodifica o base64, **calcula o SHA-256 dos bytes decodificados e compara** com `sha256`.
4. Grava no cartão SD (imagem → slot `categoria_ordem` / `botao_ordem`).
5. Sucesso: `POST /device/iot/midias/{id}/concluido` com `{"sha256": "<hash que você calculou>"}`.
   Falha (hash diferente, SD cheio...): `POST /device/iot/midias/{id}/erro` com `{"mensagem": "..."}` (a API conta as tentativas; máx. 5).
6. Confirmar de novo é seguro (idempotente): se a resposta se perder, repita.

## 2. Formato das mídias (a API já converte; o app pode mandar o arquivo original)
- **Imagem:** JPEG **baseline** (não progressivo), **240×240**, RGB, sem EXIF (`image/jpeg`).
- **Áudio:** MP3 ou WAV, até 500 KB (`audio/mpeg`, `audio/wav`). Não é convertido.
- Limite do documento do Firestore: ~1 MiB; o base64 já é validado (≤ 900.000 caracteres).

## 3. Estados de um envio
`pendente` → `baixando` → `concluido`   (ou `erro`, que volta a ser buscável até 5 tentativas).
- Ao concluir, a API **apaga o base64 do Firestore** e deixa só o estado no Realtime Database (apagado após 24 h).
- Item que o aparelho nunca buscou é descartado após 7 dias. Fila máxima por aparelho: 20 itens (HTTP 409 `fila_cheia`).

## 4. Onde ficam os dados
```
Realtime Database   dispositivos/{MAC}/sync/{id} = { tipo, estado, tamanho, criado_em(ms), concluido_em(ms)?,
                                                      botao_id, categoria_ordem, botao_ordem, erro?, tentativas? }
Firestore           dispositivos/{MAC}/fila/{id} = { tipo, mime, base64, sha256, tamanho, largura, altura, estado,
                                                      tentativas, erro, owner_uid, criado_em, botao_id, rotulo, ... }
```
`{MAC}` no formato `AA:BB:CC:DD:EE:FF` (maiúsculas, com dois-pontos).

## 5. Escutar o Realtime Database em vez de consultar (opcional)
Dá resposta mais rápida, mas **mantém o Wi-Fi ligado** (gasta bateria; o aparelho tem 8 telas). Para isso o firmware precisa
autenticar no Firebase e as regras do Realtime Database devem permitir **só leitura** de `dispositivos/{MAC}/sync` àquele aparelho.
O conteúdo (base64) continua vindo pela API (`GET /device/iot/midias/{id}`) — não leia o Firestore direto.
Regras recomendadas do Firestore e do Storage: `allow read, write: if false;` (só o backend acessa).

## 6. Exemplos (PowerShell)
```powershell
$h = @{ "X-Device-Token" = "casa_..." }
Invoke-RestMethod http://localhost:8000/device/iot/pendentes -Headers $h
$i = Invoke-RestMethod http://localhost:8000/device/iot/midias/ID -Headers $h
Invoke-RestMethod -Method Post http://localhost:8000/device/iot/midias/ID/concluido -Headers $h -ContentType "application/json" -Body (@{ sha256 = $i.sha256 } | ConvertTo-Json)
```
Lado do app (login do responsável):
```powershell
curl.exe -X POST http://localhost:8000/iot/midias -H "Authorization: Bearer TOKEN_FIREBASE" -F "dispositivo=24:62:AB:E4:C1:0C" -F "botao_id=ID_DO_BOTAO" -F "arquivo=@foto.png"
```

## 7. Códigos de erro que o firmware deve tratar
`401 dispositivo_nao_autenticado` (token inválido/aparelho removido → parar de sincronizar e sinalizar no OLED) ·
`404 nao_encontrado` (já concluído, cancelado ou expirado → ignorar) · `422 hash_diferente` (refazer o download) ·
`503 rtdb_nao_configurado` (servidor sem FIREBASE_DATABASE_URL).

## 8. O que já existe no Firebase do projeto (É contigo Zeus!) — decidir 

| Onde | O que há | Quem usa |
|---|---|---|
| Realtime Database | `dispositivo/arquivos/slot1/{foto_b64, som_b64}`, `slot2`, `controle` (singular, **sem MAC**, base64 direto no RTDB) | app Kotlin e/ou firmware (este backend **não** usa) |
| Firestore | `arquivos_esp/{foto1, foto2, som1, som2}` com o campo `b64` | app Kotlin e/ou firmware (este backend **não** usa) |
| Firestore | `dispositivos/{MAC}` com campos do backend (`owner_uid`, `token_hash`, `bateria_pct`, `config_versao`...) **e** campos do app (`id`, `idUsuarioDono`, `macAddress`, `nivelBateria`...) | **dois programas escrevendo o mesmo documento** |

Hoje existem **dois fluxos paralelos** de envio de mídia: este contrato (`dispositivos/{MAC}/fila` + `dispositivos/{MAC}/sync`) e o do app/firmware (`arquivos_esp` + `dispositivo/...`).
Escolham UM:

- **A (recomendado): tudo pela API.** O app Kotlin chama `POST /dispositivos` (pareamento) e `POST /iot/midias`; o firmware usa só as rotas `/device/...`.
  Ganhos: um único dono do documento do dispositivo, validação e conversão (JPEG 240×240) no servidor, isolamento por conta, e o firmware não carrega credenciais do Firebase.
- **B: manter o esquema do app/firmware.** Aí a API precisa gravar em `arquivos_esp`/`dispositivo/...`. Para isso preciso do conteúdo do nó `controle` e de um `slot2` aberto.

Riscos enquanto os dois coexistirem:
- Se o app criar `dispositivos/{MAC}` primeiro, o pareamento pelo site responde **409** (já pareado).
- `nivelBateria` (app) e `bateria_pct` (backend) são o mesmo dado em campos diferentes.
- **Regras de segurança:** se o app grava direto no Firestore/Realtime Database com o SDK do cliente, as regras NÃO podem ser "bloquear tudo". Confira se não estão em modo de teste (aberto a qualquer um) e restrinja por usuário.

